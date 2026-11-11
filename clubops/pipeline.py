"""Standard-library extraction, validation and CSV exports for Spanish Primera JSON."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

MATCH_COLUMNS = ["season", "match_id", "date", "round", "home", "away", "home_key", "away_key", "home_goals", "away_goals", "is_complete", "source_row", "source_sha256", "source_url"]
CLUB_MATCH_COLUMNS = ["season", "match_id", "date", "round", "club", "club_key", "opponent", "venue", "goals_for", "goals_against", "result", "is_complete", "gap_days_from_previous"]
CLUB_SUMMARY_COLUMNS = ["season", "club", "club_key", "fixtures", "completed", "home", "away", "wins", "draws", "losses", "short_gaps_le_3_days", "average_gap_days"]
SEASON_SUMMARY_COLUMNS = ["season", "source_records", "accepted", "rejected", "clubs", "completed", "unscored", "illustrative_expected_380", "difference_from_380", "result_coverage_pct", "source_sha256"]
QA_COLUMNS = ["severity", "season", "source_row", "code", "detail"]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def slug(value: str) -> str:
    norm = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", norm.lower())).strip("-")


def configured_sources(config_path: Path) -> list[dict]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    result = config.get("sources", [])
    if not result or len({x["season"] for x in result}) != len(result):
        raise ValueError("Config must contain unique named seasons")
    for source in result:
        if not source["url"].startswith("https://raw.githubusercontent.com/openfootball/football.json/"):
            raise ValueError(f"Unexpected source host: {source['url']}")
    return result


def load_aliases(alias_path: Path) -> dict:
    if not alias_path.exists():
        return {}
    payload = json.loads(alias_path.read_text(encoding="utf-8"))
    aliases = payload.get("aliases", {})
    if not isinstance(aliases, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in aliases.items()):
        raise ValueError("aliases must be a string-to-string mapping")
    return aliases


def fetch(config_path: Path, raw_dir: Path, overwrite: bool = False) -> list[str]:
    """Download real upstream bytes. Never replace an existing snapshot without opt-in."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for source in configured_sources(config_path):
        season, url = source["season"], source["url"]
        destination = raw_dir / f"{season}.json"
        if destination.exists() and not overwrite:
            verify_snapshot(source, destination.read_bytes())
            results.append(f"SKIP {season}: existing snapshot retained")
            continue
        request = Request(url, headers={"User-Agent": "ClubOpsIntelligencePortfolio/0.1"})
        with urlopen(request, timeout=35) as response:  # noqa: S310 (allowlisted GitHub host)
            data = response.read(2_500_001)
        if len(data) > 2_500_000:
            raise ValueError(f"Unexpectedly large source: {url}")
        payload = json.loads(data)
        if not isinstance(payload, dict) or not isinstance(payload.get("matches"), list):
            raise ValueError(f"Source does not match expected JSON shape: {url}")
        verify_snapshot(source, data)
        destination.write_bytes(data)
        results.append(f"FETCHED {season}: {len(data)} bytes, sha256={sha256_bytes(data)}")
    return results


def verify_snapshot(source: dict, data: bytes):
    expected = source.get("sha256")
    if expected and sha256_bytes(data) != expected:
        raise ValueError(f"{source['season']}: raw SHA-256 differs from pinned config; review source provenance")


def parse_score(score):
    if score is None:
        return "", "", 0
    if isinstance(score, dict):
        ft = score.get("ft")
    elif isinstance(score, list):
        ft = score
    else:
        raise ValueError("Invalid score type")
    if ft is None:
        return "", "", 0
    if not (isinstance(ft, list) and len(ft) == 2 and all(type(g) is int and g >= 0 for g in ft)):
        raise ValueError("Final score must contain two non-negative integer goals")
    return ft[0], ft[1], 1


def canonical_name(name: str, aliases: dict) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Missing club name")
    canonical = aliases.get(name, name).strip()
    if not canonical or not slug(canonical):
        raise ValueError("Club name must have a nonempty canonical key")
    return canonical


def normalize_one(season: str, raw_json: bytes, source_url: str, aliases: dict) -> tuple[list[dict], list[dict], dict]:
    """One accepted match per valid record; invalid records go to QA with REJECT."""
    sha = sha256_bytes(raw_json)
    source = json.loads(raw_json)
    records = source["matches"]
    if not isinstance(records, list):
        raise ValueError("'matches' must be a list")
    matches, issues, seen = [], [], set()
    seen_pairs, club_keys = set(), {}
    for i, rec in enumerate(records, start=1):
        try:
            if not isinstance(rec, dict):
                raise ValueError("Match entry is not an object")
            home, away = canonical_name(rec.get("team1"), aliases), canonical_name(rec.get("team2"), aliases)
            if home == away:
                raise ValueError("Home and away club match")
            dt = date.fromisoformat(rec["date"]).isoformat()
            round_name = str(rec.get("round") or "Unknown round")
            home_goals, away_goals, completed = parse_score(rec.get("score"))
            candidate_keys = dict(club_keys)
            for name in (home, away):
                key_name = slug(name)
                if key_name in candidate_keys and candidate_keys[key_name] != name:
                    raise ValueError(f"Club-key collision: {name!r} and {candidate_keys[key_name]!r}")
                candidate_keys[key_name] = name
            pair = (home, away)
            if pair in seen_pairs:
                raise ValueError("Duplicate ordered home/away fixture within league season (round/date changes do not create a new fixture)")
            key = f"{season}|{slug(round_name)}|{slug(home)}|{slug(away)}"
            if key in seen:
                raise ValueError("Duplicate match identity within season")
            seen.add(key)
            seen_pairs.add(pair)
            club_keys = candidate_keys
            matches.append({"season": season, "match_id": key, "date": dt, "round": round_name,
                            "home": home, "away": away, "home_key": slug(home), "away_key": slug(away),
                            "home_goals": home_goals, "away_goals": away_goals, "is_complete": completed,
                            "source_row": i, "source_sha256": sha, "source_url": source_url})
            if not completed:
                issues.append({"severity": "WARN", "season": season, "source_row": i,
                               "code": "UNSCORED_MATCH", "detail": "No valid final score: result unknown"})
        except (KeyError, TypeError, ValueError) as err:
            issues.append({"severity": "REJECT", "season": season, "source_row": i,
                           "code": "INVALID_RECORD", "detail": str(err)})
    accepted = len(matches)
    rejected = sum(issue["severity"] == "REJECT" for issue in issues)
    require(accepted + rejected == len(records), "Every source entry must be accounted for")
    return matches, issues, {"source_records": len(records), "accepted": accepted, "rejected": rejected, "sha": sha}


def club_match_rows(matches: list[dict]) -> list[dict]:
    rows = []
    for item in matches:
        finished = bool(item["is_complete"])
        hg, ag = item["home_goals"], item["away_goals"]
        for venue in ("Home", "Away"):
            is_home = venue == "Home"
            gf = (hg if is_home else ag) if finished else ""
            ga = (ag if is_home else hg) if finished else ""
            result = ("W" if gf > ga else "D" if gf == ga else "L") if finished else ""
            rows.append({"season": item["season"], "match_id": item["match_id"],
                         "date": item["date"], "round": item["round"],
                         "club": item["home"] if is_home else item["away"],
                         "club_key": item["home_key"] if is_home else item["away_key"],
                         "opponent": item["away"] if is_home else item["home"],
                         "venue": venue, "goals_for": gf, "goals_against": ga,
                         "result": result, "is_complete": int(finished), "gap_days_from_previous": ""})
    groups = defaultdict(list)
    for item in rows:
        groups[(item["season"], item["club_key"])].append(item)
    for group in groups.values():
        group.sort(key=lambda x: (x["date"], x["match_id"]))
        for prev, cur in zip(group, group[1:]):
            cur["gap_days_from_previous"] = (date.fromisoformat(cur["date"]) - date.fromisoformat(prev["date"])).days
    return sorted(rows, key=lambda x: (x["season"], x["date"], x["match_id"], x["venue"]))


def club_summaries(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[(row["season"], row["club_key"], row["club"])].append(row)
    results = []
    for (season, club_key, club), entries in sorted(groups.items()):
        gaps = [int(x["gap_days_from_previous"]) for x in entries if x["gap_days_from_previous"] != ""]
        results.append({"season": season, "club": club, "club_key": club_key,
                        "fixtures": len(entries), "completed": sum(int(x["is_complete"]) for x in entries),
                        "home": sum(x["venue"] == "Home" for x in entries),
                        "away": sum(x["venue"] == "Away" for x in entries),
                        "wins": sum(x["result"] == "W" for x in entries),
                        "draws": sum(x["result"] == "D" for x in entries),
                        "losses": sum(x["result"] == "L" for x in entries),
                        "short_gaps_le_3_days": sum(x <= 3 for x in gaps),
                        "average_gap_days": round(sum(gaps) / len(gaps), 2) if gaps else ""})
    return results


def write_csv(path: Path, fieldnames: list[str], records: list[dict]):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def build(config_path: Path, raw_dir: Path, out_dir: Path, alias_path: Path) -> list[str]:
    sources = configured_sources(config_path)
    aliases = load_aliases(alias_path)
    matches, issues, seasons = [], [], []
    for src in sources:
        season = src["season"]
        raw_file = raw_dir / f"{season}.json"
        if not raw_file.exists():
            raise FileNotFoundError(f"Missing {raw_file}. Run `python -m clubops fetch` first.")
        raw = raw_file.read_bytes()
        verify_snapshot(src, raw)
        parsed, qa, metrics = normalize_one(season, raw, src["url"], aliases)
        matches.extend(parsed)
        issues.extend(qa)
        n_clubs = len({row["home_key"] for row in parsed} | {row["away_key"] for row in parsed})
        n_complete = sum(row["is_complete"] for row in parsed)
        if metrics["accepted"] != 380:
            issues.append({"severity": "WARN", "season": season, "source_row": "",
                           "code": "NOT_380_ACCEPTED", "detail": "380 is an illustrative 20-club double round-robin benchmark, not a guarantee of upstream coverage"})
        seasons.append({"season": season, "source_records": metrics["source_records"],
                        "accepted": metrics["accepted"], "rejected": metrics["rejected"],
                        "clubs": n_clubs, "completed": n_complete,
                        "unscored": metrics["accepted"] - n_complete,
                        "illustrative_expected_380": 380,
                        "difference_from_380": metrics["accepted"] - 380,
                        "result_coverage_pct": round(100 * n_complete / metrics["accepted"], 2) if metrics["accepted"] else 0,
                        "source_sha256": metrics["sha"]})
    matches.sort(key=lambda x: (x["season"], x["date"], x["match_id"]))
    issues.sort(key=lambda x: (x["season"], str(x["source_row"]), x["code"]))
    cm = club_match_rows(matches)
    summaries = club_summaries(cm)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, columns, entries in [
        ("matches.csv", MATCH_COLUMNS, matches),
        ("club_matches.csv", CLUB_MATCH_COLUMNS, cm),
        ("club_summary.csv", CLUB_SUMMARY_COLUMNS, summaries),
        ("season_summary.csv", SEASON_SUMMARY_COLUMNS, seasons),
        ("qa_issues.csv", QA_COLUMNS, issues),
    ]:
        write_csv(out_dir / name, columns, entries)
    return [f"{s['season']}: {s['accepted']}/{s['source_records']} accepted, {s['rejected']} rejected, {s['unscored']} without scores" for s in seasons]


def require(condition: bool, message: str):
    """Required validation remains active under python -O."""
    if not condition:
        raise ValueError(message)


def check(out_dir: Path) -> dict:
    seasons = read_csv(out_dir / "season_summary.csv")
    matches = read_csv(out_dir / "matches.csv")
    club_matches = read_csv(out_dir / "club_matches.csv")
    summaries = read_csv(out_dir / "club_summary.csv")
    issues = read_csv(out_dir / "qa_issues.csv")
    require(bool(seasons), "Missing season summaries")
    require(len({s['season'] for s in seasons}) == len(seasons), "Duplicate seasons")
    season_names = {s['season'] for s in seasons}
    require(all(r['season'] in season_names for r in matches + club_matches + summaries + issues), "Unknown season in exports")
    require(len({row["match_id"] for row in matches}) == len(matches), "Duplicate IDs")
    typed, pairs, keys = [], set(), {}
    for row in matches:
        m = dict(row)
        require(date.fromisoformat(m['date']).isoformat() == m['date'], "Invalid fixture date")
        for side in ('home', 'away'):
            name = canonical_name(m[side], {})
            key = (m['season'], slug(name))
            require(m[side] == name and m[side+'_key'] == key[1], "Invalid canonical club/key")
            require(key not in keys or keys[key] == name, "Club-key collision in matches")
            keys[key] = name
        require(m['home'] != m['away'], "Same-club fixture")
        pair = (m['season'], m['home'], m['away'])
        require(pair not in pairs, "Duplicate ordered home/away fixture")
        pairs.add(pair)
        expected_id = f"{m['season']}|{slug(m['round'])}|{m['home_key']}|{m['away_key']}"
        require(m['match_id'] == expected_id, "Invalid match identity")
        require(m['is_complete'] in ('0', '1'), "Invalid completion flag")
        if m['is_complete'] == '1':
            m['home_goals'], m['away_goals'], _ = parse_score([int(m['home_goals']), int(m['away_goals'])])
        else:
            require(m['home_goals'] == m['away_goals'] == '', "Unscored fixture contains goals")
        m['is_complete'] = int(m['is_complete'])
        require(int(m['source_row']) > 0, "Invalid source row")
        typed.append(m)

    def compare(actual, expected, columns, label):
        actual_rows = Counter(tuple(r[c] for c in columns) for r in actual)
        expected_rows = Counter(tuple(str(r[c]) for c in columns) for r in expected)
        require(actual_rows == expected_rows, f"{label} reconciliation failed (row values/counts differ)")

    expected_clubs = club_match_rows(typed)
    compare(club_matches, expected_clubs, CLUB_MATCH_COLUMNS, 'Club-match')
    compare(summaries, club_summaries(expected_clubs), CLUB_SUMMARY_COLUMNS, 'Club summary')
    for s in seasons:
        rows = [m for m in typed if m['season'] == s['season']]
        ledger = [q for q in issues if q['season'] == s['season']]
        require(all(q['severity'] in ('WARN', 'REJECT') for q in ledger), "Invalid QA severity")
        rejected = [q for q in ledger if q['severity'] == 'REJECT']
        count, completed = len(rows), sum(m['is_complete'] for m in rows)
        for col, value in dict(accepted=count, rejected=len(rejected), completed=completed,
                               unscored=count-completed, clubs=len({m[k] for m in rows for k in ('home_key','away_key')}),
                               illustrative_expected_380=380, difference_from_380=count-380).items():
            require(int(s[col]) == value, f"Season {s['season']}: {col} mismatch")
        require(int(s['source_records']) == count + len(rejected), "Unreconciled source records")
        for issue in ledger:
            if issue['source_row']:
                require(1 <= int(issue['source_row']) <= int(s['source_records']), "QA source row outside raw range")
            else:
                require(issue['severity'] == 'WARN' and issue['code'] == 'NOT_380_ACCEPTED', "Missing QA source row")
        source_rows = [int(m['source_row']) for m in rows] + [int(q['source_row']) for q in rejected]
        require(sorted(source_rows) == list(range(1, int(s['source_records'])+1)), "Source rows missing or duplicated")
        require(all(m['source_sha256'] == s['source_sha256'] for m in rows), "Source hash mismatch across tables")
        require(float(s['result_coverage_pct']) == (round(100*completed/count,2) if count else 0), "Result coverage mismatch")
        unknown = Counter(m['source_row'] for m in rows if not m['is_complete'])
        warnings = Counter(q['source_row'] for q in ledger if q['code'] == 'UNSCORED_MATCH' and q['severity'] == 'WARN')
        require(unknown == warnings, "Unscored QA ledger mismatch")
    return {"seasons": len(seasons), "matches": len(matches), "club_match_rows": len(club_matches),
            "rejected": sum(int(x["rejected"]) for x in seasons)}
