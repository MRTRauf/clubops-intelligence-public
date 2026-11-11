"""Render the offline HTML in installed Chrome and reconcile five filter views."""
import csv
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
CHROME = Path('C:/Program Files/Google/Chrome/Application/chrome.exe')


def main():
    with (ROOT/'data/processed/club_summary.csv').open(encoding='utf-8-sig',newline='') as f:
        clubs = list(csv.DictReader(f))
    with (ROOT/'data/processed/season_summary.csv').open(encoding='utf-8-sig',newline='') as f:
        seasons = list(csv.DictReader(f))
    evidence = ROOT/'artifacts/screenshots'
    evidence.mkdir(exist_ok=True)
    runtime = ROOT/'.runtime/browser'
    runtime.mkdir(parents=True,exist_ok=True)
    cases = [('2024-25','FC Barcelona'),('2023-24','FC Barcelona'),('2024-25','Real Madrid CF'),
             ('2023-24','Girona FC'),('2024-25','Valencia CF')]
    results = []
    for i,(season,club) in enumerate(cases):
        url = (ROOT/'artifacts/ClubOps_Dashboard.html').as_uri()+'?'+urlencode(dict(season=season,club=club))
        cmd = [str(CHROME),'--headless','--disable-gpu','--no-sandbox','--no-first-run',
               f'--user-data-dir={runtime}', '--window-size=1440,1100','--virtual-time-budget=1500','--dump-dom']
        if i < 2:
            cmd.append(f'--screenshot={evidence / ("HTML_"+season+".png")}')
        result = subprocess.run(cmd+[url],capture_output=True,timeout=45)
        if not (result.returncode == 0):
            raise ValueError(result.stderr.decode(errors='replace')[-500:])
        dom = result.stdout.decode('utf-8')
        summary = next(r for r in clubs if r['season']==season and r['club']==club)
        ss = next(r for r in seasons if r['season']==season)
        values = dict(fixtures=summary['fixtures'],complete=summary['completed'],short=summary['short_gaps_le_3_days'],scorecover=f"{float(ss['result_coverage_pct']):.1f}%")
        for key,expected in values.items():
            actual = re.search(r'id="'+key+r'">([^<]+)</div>',dom).group(1)
            if not (actual == expected):
                raise ValueError((season,club,key,expected,actual))
        fixture_body = re.search(r'<tbody id="fixtureRows">(.*?)</tbody>',dom,re.S).group(1)
        if not (fixture_body.count('<tr>') == 12):
            raise ValueError('Validation failed at scripts/verify_browser.py:41')
        if not ('<option value="'+club+'"' in dom):
            raise ValueError('Validation failed at scripts/verify_browser.py:42')
        results.append(dict(season=season,club=club,values=values,fixture_rows=12))
    (ROOT/'artifacts/browser_verification.json').write_text(json.dumps({'browser':'Chrome headless, real offline file rendering','views':results},indent=2)+'\n')
    print('PASS: 5 actual browser filter views; 20 KPI values reconciled; 12 fixture rows per view; 2 real rendered screenshots')


if __name__ == '__main__':
    main()
