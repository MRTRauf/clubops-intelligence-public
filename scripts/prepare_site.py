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
<a href="briefing.html">Briefing</a><a href="{REPO}">Source code ↗</a></nav></header>
{body}<footer><a class="brand" href="index.html">CLUBOPS INTELLIGENCE</a>
<p>Independent portfolio. No affiliation with, endorsement by, or internal data access from LALIGA or its clubs.</p>
<p>Historical community data. No live feed or measured club business impact.</p>
<a href="data/provenance.json">Source provenance</a> · <a href="data/LICENSE.md">Data license (CC0)</a> ·
<a href="{REPO}/blob/main/LICENSE">Code license (MIT)</a></footer></body></html>'''


def markdown_blocks(value):
    out = []
    for block in value.strip().split('\n\n'):
        if block.startswith('# '):
            out.append('<h1>' + html.escape(block[2:]) + '</h1>')
        elif block.startswith('## '):
            out.append('<h2>' + html.escape(block[3:]) + '</h2>')
        elif block.strip():
            text = html.escape(block).replace('\n', '<br>')
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
            text = re.sub(r'(https://[^<\s]+)', r'<a href="\1">\1</a>', text)
            out.append('<p>' + text + '</p>')
    return ''.join(out)


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
    original = (ROOT / 'artifacts/ClubOps_Dashboard.html').read_text(encoding='utf-8')
    hosted = original.replace('</head>', '''<link rel="icon" href="data:,"><style>
header a{color:#8ce3db}a:focus-visible,select:focus-visible{outline:3px solid #e08d30;outline-offset:4px}
.foot{overflow-wrap:anywhere}@media(max-width:750px){.controls label,select{width:100%;min-width:0}
section{overflow-x:auto}td,th{padding:9px 5px}.card{padding:14px}}</style></head>''')
    hosted = hosted.replace('<header>', '''<header><a href="../index.html">← Portfolio home</a> ·
<a href="../case-study.html">Case study</a><p><strong>Historical public-data demonstration ·
2023–24 / 2024–25 · Not a live feed</strong></p>''', 1)
    hosted = hosted.replace('This dashboard is generated locally from validated CSV files.',
                            'This historical dashboard uses the validated public CSV snapshot.')
    (SITE / 'dashboard/index.html').write_text(hosted, encoding='utf-8')
    for output, source, title in [('case-study.html', 'docs/DEMO_AND_CASE_STUDY.md', 'Case study'),
                                  ('briefing.html', 'artifacts/briefing.md', 'Traceable briefing')]:
        content = (ROOT / source).read_text(encoding='utf-8').split('For a short presentation,')[0]
        body = '<main id="main" class="article"><a href="index.html">← Portfolio home</a>'
        body += markdown_blocks(content) + '<p><a class="button primary" href="dashboard/">Explore dashboard →</a></p></main>'
        (SITE / output).write_text(shell(title, body), encoding='utf-8')
    (SITE / '.nojekyll').touch()
    print('Packaged curated site assets; analytics and embedded dashboard data preserved')


if __name__ == '__main__':
    main()
