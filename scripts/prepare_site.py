"""Package curated GitHub Pages assets without rebuilding analytics."""
import html
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
REPO = 'https://github.com/MRTRauf/clubops-intelligence-public'


def shell(title, body):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | ClubOps Intelligence</title><link rel="icon" href="data:,">
<link rel="stylesheet" href="assets/site.css"></head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav"><a class="brand" href="index.html">CLUBOPS <span>INTELLIGENCE</span></a>
<nav aria-label="Main navigation"><a href="dashboard/">Dashboard</a><a href="case-study.html">Case study</a>
<a href="briefing.html">Briefing</a><a href="{REPO}">Source code</a></nav></header>
{body}<footer><a class="brand" href="index.html">CLUBOPS INTELLIGENCE</a>
<p>Independent portfolio. No affiliation with, endorsement by, or internal data access from LALIGA or its clubs.</p>
<p>Historical community data. No live feed or measured club business impact.</p>
<a href="data/provenance.json">Source provenance</a> · <a href="data/LICENSE.md">Data license (CC0)</a> ·
<a href="{REPO}/blob/main/LICENSE">Code license (MIT)</a></footer></body></html>'''


def markdown_blocks(value):
    """Render the headings, lists and inline syntax used by our source documents."""
    def inline(text):
        text = html.escape(text, quote=True)
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        return re.sub(r'https://[^\s<>]+', lambda m: '<a href="' + m[0] + '">' + m[0] + '</a>', text)
    out, paragraph, items = [], [], []
    def flush():
        if paragraph:
            out.append('<p>' + inline(' '.join(paragraph)) + '</p>')
            paragraph.clear()
        if items:
            out.append('<ul>' + ''.join('<li>' + inline(x) + '</li>' for x in items) + '</ul>')
            items.clear()
    for line in value.splitlines():
        heading = re.match(r'^(#{1,6}) (.*)$', line)
        if heading:
            flush()
            level = len(heading[1])
            out.append(f'<h{level}>' + inline(heading[2]) + f'</h{level}>')
        elif line.startswith('- '):
            if paragraph:
                flush()
            items.append(line[2:])
        elif not line.strip():
            flush()
        else:
            if items:
                flush()
            paragraph.append(line.strip())
    flush()
    return ''.join(out)


def briefing_page(content):
    """Present the audited Markdown snapshot without recomputing analytics."""
    sections = dict(re.findall(r'## ([^\n]+)\n(.*?)(?=\n## |\Z)', content, re.S))
    club = re.search(r'^# ClubOps briefing — (.+)', content)[1]
    season, cutoff, days = re.search(r'\*\*Season:\*\* (\S+).*?\*\*As-of date:\*\* (\S+).*?\*\*Window:\*\* (\d+) days', content).groups()
    from datetime import date
    stamp = date.fromisoformat(cutoff)
    label = f'{stamp.day} {stamp:%B %Y}'
    figures = re.findall(r'\*\*(\d+)\*\*', sections['Executive summary'])
    if len(figures) != 3:
        raise ValueError('Expected three audited briefing scope figures')
    score_note = 'all with final scores' if figures[2] == '0' else f"{figures[2]} without final scores"
    labels = ['Listed league fixtures before cutoff', f'Listed fixtures in next {days} days', 'Earlier fixtures without final scores']
    stats = '<div class="brief-stats" aria-label="Historical reporting scope">' + ''.join(f'<div><strong>{n}</strong><span>{html.escape(t)}</span></div>' for n, t in zip(figures, labels)) + '</div>'
    def table(heading, columns, pattern):
        rows = []
        for line in sections[heading].strip().splitlines():
            match = re.fullmatch(pattern, line)
            if not match:
                raise ValueError('Unexpected briefing fixture format: ' + line)
            rows.append('<tr>' + ''.join('<td>' + html.escape(x) + '</td>' for x in match.groups()) + '</tr>')
        return '<div class="table-scroll" tabindex="0" role="region" aria-label="' + heading + '"><table><caption>' + heading + '</caption><thead><tr>' + ''.join('<th scope="col">'+c+'</th>' for c in columns) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'
    upcoming = table('Upcoming league fixtures in this source', ['Date', 'Home / away', 'Opponent', 'Matchday'], r'- (\d{4}-\d{2}-\d{2}) — (Home|Away) vs (.+) \(Matchday (\d+)\)')
    recent = table('Last five scored league fixtures before cutoff', ['Date', 'Home / away', 'Opponent', 'Score', 'Result'], r'- (\d{4}-\d{2}-\d{2}) — (Home|Away) vs (.+): (\d+-\d+) \(([WDL])\)')
    return f'''<main id="main" class="article release-article"><header class="brief-header"><p class="eyebrow">CLUBOPS / MATCHDAY BRIEFING</p><h1>{html.escape(club)}</h1><p>Spanish Primera · {html.escape(season.replace('-', '–'))}<br>Historical as-of date: <strong>{label}</strong><br>Reporting window: {days} days</p></header>{stats}
<section><h2>Executive summary</h2><p>The source lists {figures[0]} league fixtures before the cutoff, {score_note}, and {figures[1]} fixtures within the next {days} days. Check the listed dates against a full competition calendar before using them in an operations discussion: this retrospective view may reflect later rescheduling.</p></section>
<section><h2>Upcoming fixtures</h2>{upcoming}</section><section><h2>Recent results</h2>{recent}<p class="quiet">Scores are from the selected club’s perspective. W = win, D = draw, L = loss.</p></section>
<aside class="historical-note" aria-labelledby="scope-heading"><h2 id="scope-heading">Read this as historical evidence</h2><p>This is a historical reconstruction, not a live feed or a schedule archived as known at the cutoff. It uses the currently downloaded source snapshot. League fixtures only; calendar gaps do not establish physical rest, fatigue or total workload. Independent community data, not official LALIGA data.</p></aside>
<details class="evidence"><summary>Technical evidence &amp; source traceability</summary>{markdown_blocks('## Traceability'+chr(10)+sections['Traceability'])}<p><a href="data/provenance.json">Full source provenance</a></p>{markdown_blocks('## Data caveats'+chr(10)+sections['Data caveats'])}</details>
<div class="actions"><a class="button primary" href="dashboard/">Explore the dashboard</a><a class="button" href="index.html">Portfolio home</a></div></main>'''


def case_study_page(content):
    parts = re.split(r'^## (.+)$', content, flags=re.M)
    body = '<main id="main" class="article release-article"><p class="eyebrow">CLUBOPS / CASE STUDY</p>' + markdown_blocks(parts[0])
    for title, text in zip(parts[1::2], parts[2::2]):
        style = ' class="approach"' if title == 'Approach' else (' class="findings"' if title == 'Key findings' else '')
        body += '<section' + style + '><h2>' + html.escape(title) + '</h2>' + markdown_blocks(text)
        if title == 'Genuine visual evidence':
            body += '<div class="evidence-figures"><figure><a href="dashboard/"><img src="assets/Fixture_Desk.png" alt="Actual Barcelona dashboard with 38 listed fixtures, 37 scored and seven short league gaps" loading="lazy"></a><figcaption>Interactive HTML dashboard. Historical 2024–25 Barcelona selection; not Power BI.</figcaption></figure><figure><img src="assets/Excel_Club_Pivot.png" alt="Native Excel PivotTable comparing fixtures, scored matches and short league gaps by season and club" loading="lazy"><figcaption>Earlier native Excel evidence. 120 PivotTable values reconciled to CSVs in Excel 16.0.</figcaption></figure></div>'
        body += '</section>'
    body += '<div class="actions"><a class="button primary" href="dashboard/">Explore the dashboard</a><a class="button" href="briefing.html">Read the briefing</a><a class="button" href="downloads/ClubOps_Reporting.xlsx">Excel reporting workbook</a><a class="button" href="' + REPO + '">GitHub source code</a></div></main>'
    return body


def main():
    for folder in ('assets', 'dashboard', 'downloads', 'data'):
        (SITE / folder).mkdir(parents=True, exist_ok=True)
    for name in ('HTML_2024-25.png', 'Excel_Club_Pivot.png'):
        shutil.copyfile(ROOT / 'artifacts/screenshots' / name, SITE / 'assets' / name)
    shutil.copyfile(ROOT / 'artifacts/ClubOps_Reporting_COMPLETED.xlsx', SITE / 'downloads/ClubOps_Reporting.xlsx')
    for path in (ROOT / 'data/processed').glob('*.csv'):
        shutil.copyfile(path, SITE / 'data' / path.name)
    shutil.copyfile(ROOT / 'data/provenance/manifest.json', SITE / 'data/provenance.json')
    shutil.copyfile(ROOT / 'data/provenance/LICENSE.md', SITE / 'data/LICENSE.md')
    with zipfile.ZipFile(SITE / 'downloads/ClubOps-PowerBI-Project.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((ROOT / 'powerbi/ClubOps').rglob('*')):
            if path.is_file():
                archive.write(path, Path('ClubOps') / path.relative_to(ROOT / 'powerbi/ClubOps'))
    with zipfile.ZipFile(SITE / 'downloads/ClubOps-Reporting-Data.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((ROOT / 'data/processed').glob('*.csv')):
            archive.write(path, path.name)
        archive.write(ROOT / 'data/provenance/LICENSE.md', 'LICENSE.md')
        archive.write(ROOT / 'data/provenance/manifest.json', 'provenance.json')
    import sys
    sys.path.insert(0, str(ROOT))
    from clubops.dashboard import render_html
    original = render_html(ROOT / 'data/processed')
    hosted = re.sub(r'<style>.*?</style>', '<link rel="stylesheet" href="../assets/site.css">', original, flags=re.S)
    nav = shell('Dashboard', '').split('<header class="nav">')[1].split('</header>')[0]
    nav = nav.replace('href="index.html"', 'href="../index.html"').replace('href="dashboard/"', 'href="./"').replace('href="case-study.html"', 'href="../case-study.html"').replace('href="briefing.html"', 'href="../briefing.html"')
    hosted = hosted.replace('<body>', '<body class="dashboard"><a class="skip" href="#main">Skip to content</a><header class="nav">' + nav + '</header>')
    (SITE / 'dashboard/index.html').write_text(hosted, encoding='utf-8')
    for output, source, title in [('case-study.html', 'docs/DEMO_AND_CASE_STUDY.md', 'Case study'),
                                  ('briefing.html', 'artifacts/briefing.md', 'Traceable briefing')]:
        content = (ROOT / source).read_text(encoding='utf-8').split('For a short presentation,')[0]
        body = briefing_page(content) if output == 'briefing.html' else case_study_page(content)
        (SITE / output).write_text(shell(title, body), encoding='utf-8')
    (SITE / '.nojekyll').touch()
    print('Packaged curated site assets; analytics and embedded dashboard data preserved')


if __name__ == '__main__':
    main()
