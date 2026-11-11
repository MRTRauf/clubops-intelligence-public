"""Synthetic regression cases for the release audit findings."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from clubops.pipeline import build, check, normalize_one, read_csv, write_csv


class ValidationRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        raw = self.root / 'raw'
        raw.mkdir()
        self.record = dict(date='2099-01-01', round='Round 1', team1='Club A',
                           team2='Club B', score={'ft': [2, 1]})
        records = [self.record, dict(self.record, date='2099-01-04', round='Round 2',
                                    team1='Club B', team2='Club A', score={})]
        (raw / '2099-00.json').write_text(json.dumps({'matches': records}))
        config = self.root / 'sources.json'
        config.write_text(json.dumps({'sources': [{'season': '2099-00',
            'url': 'https://raw.githubusercontent.com/openfootball/football.json/master/2099-00/es.1.json'}]}))
        self.out = self.root / 'out'
        build(config, raw, self.out, self.root / 'no-aliases.json')

    def rewrite(self, filename, rows):
        write_csv(self.out / filename, list(rows[0]), rows)

    def test_corrupted_club_reporting_fields_rejected(self):
        path = self.out / 'club_matches.csv'
        original = path.read_bytes()
        for field, value in [('result', 'INVALID'), ('result', 'W'), ('goals_for', '999'),
                             ('goals_against', '-1'), ('gap_days_from_previous', '-99'),
                             ('venue', 'Home'), ('opponent', 'Invented'),
                             ('date', '2099-02-01'), ('is_complete', '0')]:
            with self.subTest(field=field, value=value):
                path.write_bytes(original)
                rows = read_csv(path)
                rows[0][field] = value
                self.rewrite(path.name, rows)
                with self.assertRaisesRegex(ValueError, 'Club-match'):
                    check(self.out)

    def test_two_rows_per_match_required_not_only_total_count(self):
        rows = read_csv(self.out / 'club_matches.csv')
        rows[0] = dict(rows[-1])
        self.rewrite('club_matches.csv', rows)
        with self.assertRaisesRegex(ValueError, 'Club-match'):
            check(self.out)

    def test_summary_and_qa_corruption_rejected(self):
        for filename, field, value in [('club_summary.csv', 'wins', '999'),
                                      ('season_summary.csv', 'completed', '999'),
                                      ('qa_issues.csv', 'source_row', '999')]:
            with self.subTest(filename=filename):
                path = self.out / filename
                original = path.read_bytes()
                rows = read_csv(path)
                rows[0][field] = value
                self.rewrite(filename, rows)
                with self.assertRaises(ValueError):
                    check(self.out)
                path.write_bytes(original)

    def test_unknown_result_cannot_acquire_goals(self):
        rows = read_csv(self.out / 'matches.csv')
        unknown = next(r for r in rows if r['is_complete'] == '0')
        unknown['home_goals'] = '0'
        self.rewrite('matches.csv', rows)
        with self.assertRaisesRegex(ValueError, 'Unscored'):
            check(self.out)

    def test_validation_stays_active_under_optimization(self):
        rows = read_csv(self.out / 'club_matches.csv')
        rows[0]['result'] = 'INVALID'
        self.rewrite('club_matches.csv', rows)
        result = subprocess.run([sys.executable, '-O', '-m', 'clubops', 'check',
                                 '--out-dir', str(self.out)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Club-match reconciliation failed', result.stderr)

    def test_duplicate_fixture_ignores_round_and_date_changes(self):
        for changes in ({'round': 'Round 99'}, {'date': '2099-03-01'},
                        {'round': 'Round 99', 'date': '2099-03-01'}):
            with self.subTest(changes=changes):
                records = [self.record, dict(self.record, **changes)]
                rows, issues, metrics = normalize_one('2099-00', json.dumps({'matches': records}).encode(), 'synthetic', {})
                self.assertEqual((len(rows), metrics['rejected']), (1, 1))
                self.assertIn('Duplicate ordered', issues[0]['detail'])
                self.assertEqual(issues[0]['source_row'], 2)

    def test_club_key_collision_quarantined(self):
        for records in ([self.record, dict(self.record, team1='Club-A', team2='Club C')],
                        [dict(self.record, team2='Club-A')]):
            with self.subTest(records=records):
                rows, issues, metrics = normalize_one('2099-00', json.dumps({'matches': records}).encode(), 'synthetic', {})
                self.assertEqual(metrics['rejected'], 1)
                self.assertIn('Club-key collision', issues[0]['detail'])
                self.assertEqual(len(rows), len(records)-1)

    def test_reviewed_alias_and_reverse_fixture_remain_valid(self):
        records = [self.record, dict(self.record, team1='Club B', team2='Club-A', date='2099-01-04')]
        rows, issues, metrics = normalize_one('2099-00', json.dumps({'matches': records}).encode(), 'synthetic', {'Club-A': 'Club A'})
        self.assertEqual((len(rows), metrics['rejected'], len(issues)), (2, 0, 0))
        self.assertEqual(check(self.out)['matches'], 2)


if __name__ == '__main__':
    unittest.main()
