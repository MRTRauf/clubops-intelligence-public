import json
import tempfile
import unittest
from pathlib import Path
from clubops.pipeline import normalize_one, club_match_rows, club_summaries, build, check, verify_snapshot
from clubops.briefing import briefing
from clubops.dashboard import render_html


SAMPLE = {"name": "SYNTHETIC TEST ONLY", "matches": [
    {"round": "Matchday 1", "date": "2024-08-01", "team1": "Team A", "team2": "Team B", "score": {"ft": [2, 1]}},
    {"round": "Matchday 2", "date": "2024-08-04", "team1": "Team B", "team2": "Team A", "score": [0, 0]},
    {"round": "Matchday 3", "date": "2024-08-10", "team1": "Team A", "team2": "Team C"},
    {"round": "Matchday 4", "date": "not-a-date", "team1": "Team A", "team2": "Team B"},
]}


class ClubOpsTests(unittest.TestCase):
    def test_observed_empty_score_object_is_unknown(self):
        case = {'matches': [{**SAMPLE['matches'][0], 'score': {}}]}
        rows, issues, counts = normalize_one('2099-00', json.dumps(case).encode(), 'synthetic', {})
        self.assertEqual((counts['accepted'], counts['rejected']), (1, 0))
        self.assertEqual((rows[0]['home_goals'], rows[0]['away_goals'], rows[0]['is_complete']), ('', '', 0))
        self.assertEqual(issues[0]['code'], 'UNSCORED_MATCH')
        self.assertEqual(club_summaries(club_match_rows(rows))[0]['draws'], 0)

    def test_observed_half_time_is_not_final_result(self):
        case = {'matches': [{**SAMPLE['matches'][0], 'score': {'ht': [0, 0], 'ft': [2, 1]}}]}
        rows, _, _ = normalize_one('2099-00', json.dumps(case).encode(), 'synthetic', {})
        self.assertEqual((rows[0]['home_goals'], rows[0]['away_goals']), (2, 1))
        case['matches'][0]['score'] = {'ht': [0, 0]}
        rows, _, _ = normalize_one('2099-00', json.dumps(case).encode(), 'synthetic', {})
        self.assertEqual(rows[0]['is_complete'], 0)

    def test_pinned_hash_rejects_mutated_snapshot(self):
        import hashlib
        source = {'season': 'synthetic', 'sha256': hashlib.sha256(b'original').hexdigest()}
        verify_snapshot(source, b'original')
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            verify_snapshot(source, b'mutated')

    def sample(self):
        return normalize_one("2099-00", json.dumps(SAMPLE).encode(), "https://example.test/synthetic", {})

    def test_accounting_and_score_forms(self):
        rows, issues, metrics = self.sample()
        self.assertEqual(metrics["source_records"], 4)
        self.assertEqual(metrics["accepted"], 3)
        self.assertEqual(metrics["rejected"], 1)
        self.assertEqual(sum(r["is_complete"] for r in rows), 2)
        self.assertTrue(any(i["code"] == "UNSCORED_MATCH" for i in issues))

    def test_rejects_duplicate_id(self):
        case = {"matches": [SAMPLE["matches"][0], SAMPLE["matches"][0]]}
        rows, _, counts = normalize_one("2099-00", json.dumps(case).encode(), "synthetic", {})
        self.assertEqual((len(rows), counts["rejected"]), (1, 1))

    def test_gaps_and_results(self):
        rows, _, _ = self.sample()
        detail = club_match_rows(rows)
        summary = club_summaries(detail)
        a = next(x for x in summary if x["club"] == "Team A")
        self.assertEqual(a["completed"], 2)
        self.assertEqual(a["short_gaps_le_3_days"], 1)
        self.assertEqual(a["wins"], 1)
        self.assertEqual(a["draws"], 1)
        self.assertEqual(len(detail), 6)

    def test_build_check_and_no_future_score_leak(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            (base / "raw").mkdir()
            (base / "raw" / "2099-00.json").write_text(json.dumps(SAMPLE), encoding="utf-8")
            (base / "sources.json").write_text(json.dumps({"sources": [{"season": "2099-00", "url": "https://raw.githubusercontent.com/openfootball/football.json/master/2099-00/es.1.json"}]}))
            build(base / "sources.json", base / "raw", base / "out", base / "nonexistent.json")
            stats = check(base / "out")
            self.assertEqual((stats["matches"], stats["club_match_rows"]), (3, 6))
            result = briefing(base / "out", "2099-00", "Team A", "2024-08-03")
            self.assertIn("2-1 (W)", result)
            self.assertNotIn("0-0 (D)", result)
            self.assertIn("NOT a true archived point-in-time", result)

    def test_negative_score_rejected(self):
        case = {"matches": [{**SAMPLE["matches"][0], "score": {"ft": [-1, 2]}}]}
        _, issues, counts = normalize_one("2099-00", json.dumps(case).encode(), "synthetic", {})
        self.assertEqual(counts["rejected"], 1)
        self.assertEqual(issues[0]["severity"], "REJECT")



    def test_offline_html_uses_real_pipeline_tables_only(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            (base / "raw").mkdir()
            (base / "raw" / "2099-00.json").write_text(json.dumps(SAMPLE), encoding="utf-8")
            config = base / "sources.json"
            config.write_text(json.dumps({"sources": [{"season": "2099-00", "url": "https://raw.githubusercontent.com/openfootball/football.json/master/2099-00/es.1.json"}]}))
            build(config, base / "raw", base / "out", base / "aliases.json")
            html = render_html(base / "out")
            self.assertIn("ClubOps Intelligence", html)
            self.assertIn("HTML demo, not a Power BI report", html)
            self.assertIn("Team A", html)

    def test_deterministic_csv_outputs(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            (base / "raw").mkdir()
            (base / "raw" / "2099-00.json").write_text(json.dumps(SAMPLE), encoding="utf-8")
            config = base / "sources.json"
            config.write_text(json.dumps({"sources": [{"season": "2099-00", "url": "https://raw.githubusercontent.com/openfootball/football.json/master/2099-00/es.1.json"}]}))
            build(config, base / "raw", base / "out", base / "aliases.json")
            first = {p.name: p.read_bytes() for p in (base / "out").glob("*.csv")}
            build(config, base / "raw", base / "out", base / "aliases.json")
            second = {p.name: p.read_bytes() for p in (base / "out").glob("*.csv")}
            self.assertEqual(first, second)

    def test_explicit_alias_mapping(self):
        case = {"matches": [{"round": "Round 1", "date": "2024-01-01", "team1": "A FC", "team2": "B FC", "score": {"ft": [1, 0]}}]}
        rows, issues, _ = normalize_one("2099-00", json.dumps(case).encode(), "synthetic", {"A FC": "Team Alpha"})
        self.assertEqual(rows[0]["home"], "Team Alpha")
        self.assertEqual(rows[0]["home_key"], "team-alpha")
        self.assertEqual(issues, [])

if __name__ == "__main__":
    unittest.main()
