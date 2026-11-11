"""Check the deploy-only directory, links and unchanged verified dashboard data."""
import csv
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])
        if tag == 'img' and not attrs.get('alt'):
            raise ValueError('Image missing descriptive alt text')


def main():
    checked = 0
    for path in SITE.rglob('*.html'):
        source = path.read_text(encoding='utf-8')
        if re.search(r'localhost|127\.0\.0\.1|file:/{2}|(?<![A-Za-z])[A-Za-z]:[\\/]|CHANGE_ME', source, re.I):
            raise ValueError('Non-public link or placeholder in ' + str(path))
        parser = Links()
        parser.feed(source)
        for target in parser.links:
            url = urlparse(target)
            if url.scheme in ('https', 'data') or target.startswith('#'):
                continue
            if url.scheme or target.startswith('/'):
                raise ValueError('Unsafe/non-project-relative link: ' + target)
            local = (path.parent / unquote(url.path)).resolve()
            if not local.is_relative_to(SITE.resolve()):
                raise ValueError('Link escapes deployed directory: ' + target)
            if local.is_dir():
                local /= 'index.html'
            if not local.is_file():
                raise ValueError('Broken site link: ' + target)
            checked += 1
    original = (ROOT / 'artifacts/ClubOps_Dashboard.html').read_text(encoding='utf-8')
    hosted = (SITE / 'dashboard/index.html').read_text(encoding='utf-8')
    extract = lambda s: json.loads(re.search(r'const DATA=(.*?);\s*const \$', s, re.S).group(1))
    if extract(original) != extract(hosted):
        raise ValueError('Existing dashboard data changed')
    for path in (ROOT / 'data/processed').glob('*.csv'):
        if path.read_bytes() != (SITE / 'data' / path.name).read_bytes():
            raise ValueError('Deployed CSV changed')
    if (SITE / 'downloads/ClubOps_Reporting.xlsx').read_bytes() != (ROOT / 'artifacts/ClubOps_Reporting_COMPLETED.xlsx').read_bytes():
        raise ValueError('Deployed Excel workbook changed')
    with (SITE / 'data/season_summary.csv').open(encoding='utf-8-sig') as stream:
        rows = list(csv.DictReader(stream))
    if sum(int(r['accepted']) for r in rows) != 760 or sum(int(r['unscored']) for r in rows) != 10:
        raise ValueError('Landing page KPI values differ from source')
    if any(p.suffix in ('.py', '.ps1', '.tmdl') for p in SITE.rglob('*')):
        raise ValueError('Unnecessary source files in deployment payload')
    print(f'PASS: 4 HTML pages; {checked} relative links/assets; exact existing dashboard DATA, CSV and Excel bytes; verified landing KPIs')


if __name__ == '__main__':
    main()
