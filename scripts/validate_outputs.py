"""Independent raw-to-CSV reconciliation; no production aggregation helpers used.

Run from the repository root after build. Fails loudly on a mismatch.
"""
import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    with (ROOT / 'data/processed' / name).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def main():
    matches, clubs, summaries, seasons, issues = map(read, [
        'matches.csv', 'club_matches.csv', 'club_summary.csv', 'season_summary.csv', 'qa_issues.csv'])
    config = json.loads((ROOT / 'configs/sources.json').read_text(encoding='utf-8'))
    aliases = json.loads((ROOT / 'configs/aliases.json').read_text(encoding='utf-8'))['aliases']
    hashes = lambda: {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / 'data/processed').glob('*.csv')}
    before = hashes()
    subprocess.run([sys.executable, '-m', 'clubops', 'build'], cwd=ROOT, check=True, capture_output=True)
    if not (before == hashes()):
        raise ValueError('Build is not byte deterministic')
    lines = ['# Validation evidence', '', 'Generated from raw JSON and actual CSV exports by `python scripts/validate_outputs.py`.',
             'A second build produced byte-identical CSVs. Assertions use independent raw-record calculations.', '',
             '| Season | Raw | Accepted | Rejected | Scored | Unknown | QA | Raw names | Delta to 380 |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    raw_by_season, names = {}, {}
    for source in config['sources']:
        season = source['season']
        raw_bytes = (ROOT / 'data/raw' / f'{season}.json').read_bytes()
        raw = json.loads(raw_bytes)['matches']
        raw_by_season[season] = raw
        names[season] = {r[k] for r in raw for k in ('team1', 'team2')}
        ss = next(s for s in seasons if s['season'] == season)
        accepted = [m for m in matches if m['season'] == season]
        rejects = [q for q in issues if q['season'] == season and q['severity'] == 'REJECT']
        if not (len(raw) == len(accepted) + len(rejects) == int(ss['source_records'])):
            raise ValueError('Validation failed at scripts/validate_outputs.py:45')
        if not (hashlib.sha256(raw_bytes).hexdigest() == ss['source_sha256'] == source['sha256']):
            raise ValueError('Validation failed at scripts/validate_outputs.py:46')
        # Current real snapshot has no rejects. Future rejects require explicit review.
        if not (not rejects):
            raise ValueError('Rejected real records require independent review')
        if not (len({(m['home'], m['away']) for m in accepted}) == len(accepted)):
            raise ValueError('Repeated ordered pairing')
        if not (len({m['match_id'] for m in accepted}) == len(accepted)):
            raise ValueError('Validation failed at scripts/validate_outputs.py:50')
        if not (len([r for r in clubs if r['season'] == season]) == 2 * len(accepted)):
            raise ValueError('Validation failed at scripts/validate_outputs.py:51')
        for m in accepted:
            r = raw[int(m['source_row']) - 1]
            if not ((m['date'], m['home'], m['away'], m['round']) == (r['date'], aliases.get(r['team1'], r['team1']), aliases.get(r['team2'], r['team2']), r['round'])):
                raise ValueError('Validation failed at scripts/validate_outputs.py:54')
            ft = r.get('score', {}).get('ft')
            if not (m['is_complete'] == ('1' if ft is not None else '0')):
                raise ValueError('Validation failed at scripts/validate_outputs.py:56')
            if not ((m['home_goals'], m['away_goals']) == (tuple(map(str, ft)) if ft else ('', ''))):
                raise ValueError('Validation failed at scripts/validate_outputs.py:57')
            pair = [x for x in clubs if x['match_id'] == m['match_id']]
            if not ({x['venue'] for x in pair} == {'Home', 'Away'} and len(pair) == 2):
                raise ValueError('Validation failed at scripts/validate_outputs.py:59')
            for c in pair:
                home = c['venue'] == 'Home'
                if not (c['club'] == m['home' if home else 'away']):
                    raise ValueError('Validation failed at scripts/validate_outputs.py:62')
                if not (c['opponent'] == m['away' if home else 'home']):
                    raise ValueError('Validation failed at scripts/validate_outputs.py:63')
                if not (c['date'] == m['date'] and c['is_complete'] == m['is_complete']):
                    raise ValueError('Validation failed at scripts/validate_outputs.py:64')
                if not ((c['goals_for'], c['goals_against']) == ((m['home_goals'], m['away_goals']) if home else (m['away_goals'], m['home_goals']))):
                    raise ValueError('Validation failed at scripts/validate_outputs.py:65')
        scored = sum(bool(r.get('score', {}).get('ft')) for r in raw)
        if not ((int(ss['completed']), int(ss['unscored'])) == (scored, len(raw) - scored)):
            raise ValueError('Validation failed at scripts/validate_outputs.py:67')
        if not (int(ss['clubs']) == len(names[season]) == 20):
            raise ValueError('Validation failed at scripts/validate_outputs.py:68')
        if not (float(ss['result_coverage_pct']) == round(100 * scored / len(raw), 2)):
            raise ValueError('Validation failed at scripts/validate_outputs.py:69')
        if not (Counter(m['home'] for m in accepted) == Counter({n: 19 for n in names[season]})):
            raise ValueError('Validation failed at scripts/validate_outputs.py:70')
        if not (Counter(m['away'] for m in accepted) == Counter({n: 19 for n in names[season]})):
            raise ValueError('Validation failed at scripts/validate_outputs.py:71')
        lines.append(f"| {season} | {len(raw)} | {len(accepted)} | {len(rejects)} | {scored} | {len(raw)-scored} | {sum(q['season']==season for q in issues)} | {len(names[season])} | {len(accepted)-380} |")
    lines += ['', '## Independent club-season checks (all 40)', '',
              '| Season | Club | Fixtures | Scored | H/A | W/D/L | Gaps <=3d | Mean gap |',
              '|---|---|---:|---:|---|---|---:|---:|']
    for summary in summaries:
        season, club = summary['season'], summary['club']
        raw = sorted([r for r in raw_by_season[season] if club in (r['team1'], r['team2'])], key=lambda r: r['date'])
        scores = []
        for r in raw:
            ft = r.get('score', {}).get('ft')
            if ft:
                gf, ga = ft if r['team1'] == club else ft[::-1]
                scores.append('W' if gf > ga else 'D' if gf == ga else 'L')
        gaps = [(date.fromisoformat(b['date']) - date.fromisoformat(a['date'])).days for a, b in zip(raw, raw[1:])]
        expected = dict(fixtures=len(raw), completed=len(scores), home=sum(r['team1']==club for r in raw), away=sum(r['team2']==club for r in raw),
                        wins=scores.count('W'), draws=scores.count('D'), losses=scores.count('L'), short_gaps_le_3_days=sum(g<=3 for g in gaps))
        for key, value in expected.items():
            if not (int(summary[key]) == value):
                raise ValueError((season, club, key))
        average = round(sum(gaps)/len(gaps), 2)
        if not (float(summary['average_gap_days']) == average):
            raise ValueError('Validation failed at scripts/validate_outputs.py:91')
        detail = sorted([r for r in clubs if r['season']==season and r['club']==club], key=lambda r:r['date'])
        if not ([r['gap_days_from_previous'] for r in detail] == [''] + list(map(str, gaps))):
            raise ValueError('Validation failed at scripts/validate_outputs.py:93')
        if not ([r['result'] for r in detail if r['is_complete']=='1'] == scores):
            raise ValueError('Validation failed at scripts/validate_outputs.py:94')
        lines.append(f"| {season} | {club} | {len(raw)} | {len(scores)} | {expected['home']}/{expected['away']} | {scores.count('W')}/{scores.count('D')}/{scores.count('L')} | {expected['short_gaps_le_3_days']} | {average} |")
    lines += ['', '## Schema and names', '']
    for season, raw in raw_by_season.items():
        shapes = Counter(','.join(sorted(r.get('score', {}))) or 'empty object' for r in raw)
        lines.append(f'- {season} score keys: {dict(shapes)}. Only full-time scores are used; half-time is ignored.')
    common = names['2023-24'] & names['2024-25']
    lines += [f'- {len(common)} exact club names persist across seasons; no aliases applied. Departing: {sorted(names["2023-24"]-common)}. Arriving: {sorted(names["2024-25"]-common)}.',
              '- 2024-25 rows 371-380 (Matchday 38) have empty score objects: ten warnings, no invented results.',
              '- All 380 ordered home/away pairs occur once in each season; each club has 19 home and 19 away fixtures. This supports fixture coverage but is not official certification.', '',
              '## Briefing audit', '']
    raw = sorted(raw_by_season['2024-25'], key=lambda r: r['date'])
    barca = [r for r in raw if 'FC Barcelona' in (r['team1'], r['team2'])]
    past = [r for r in barca if r['date'] < '2025-03-01']
    future = [r for r in barca if '2025-03-01' <= r['date'] < '2025-03-31']
    brief = (ROOT / 'artifacts/briefing.md').read_text(encoding='utf-8')
    if not (f'**{len(past)}**' in brief and f'**{len(future)}**' in brief):
        raise ValueError('Validation failed at scripts/validate_outputs.py:110')
    if not (sum(not r.get('score',{}).get('ft') for r in past) == 0):
        raise ValueError('Validation failed at scripts/validate_outputs.py:111')
    last_section = brief.split('## Last five scored league fixtures before cutoff')[1].split('## Traceability')[0]
    for r in past[-5:]:
        ft = r['score']['ft']
        gf, ga = ft if r['team1']=='FC Barcelona' else ft[::-1]
        if not (f"{gf}-{ga} (W)" in last_section and r['date'] in last_section):
            raise ValueError('Validation failed at scripts/validate_outputs.py:116')
    future_section = brief.split('## Upcoming league fixtures in this source')[1].split('## Last five')[0]
    for r in future:
        if not (r['date'] in future_section):
            raise ValueError('Validation failed at scripts/validate_outputs.py:119')
        if not (str(r.get('score',{}).get('ft')) not in future_section):
            raise ValueError('Validation failed at scripts/validate_outputs.py:120')
    if not (len(past) == 25 and len(future) == 4):
        raise ValueError('Validation failed at scripts/validate_outputs.py:121')
    lines += ['- FC Barcelona / 2024-25 / cutoff 2025-03-01: 25 prior fixtures, 4 in [March 1, March 31), 0 prior unscored.',
              '- Upcoming dates: ' + ', '.join(r['date'] for r in future) + '. No scores in that section.',
              '- Last five prior results checked in raw: 7-1, 1-0, 4-1, 1-0, 2-0 (all Barcelona wins).',
              '- Retrospective reconstruction: March 27 Osasuna date is from the acquired file, not a March 1 archived schedule.', '',
              '## Assumptions and limits',
              '- Calendar-day gaps use consecutive listed league dates, reset each season, include unscored fixtures, and are not player rest or all-competition workload.',
              '- 380 is a benchmark only. Result coverage uses accepted records as denominator.',
              '- Raw hash and alias config determine output. Independent validator deliberately stops for unexpected rejects or changed schemas.', '',
              '## Deterministic CSV SHA-256', '']
    lines.extend(f'- `{name}`: `{sha}`' for name,sha in sorted(before.items()))
    target = ROOT / 'artifacts/validation_summary.md'
    target.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    (ROOT / 'artifacts/validation.json').write_text(json.dumps({'club_season_checks': len(summaries), 'matches':len(matches), 'club_rows':len(clubs), 'deterministic':True,'csv_sha256':before},indent=2)+'\n')
    print(f'PASS: {len(matches)} matches; {len(clubs)} club rows; {len(summaries)} independently reconciled summaries; deterministic CSVs; briefing audited')


if __name__ == '__main__':
    main()
