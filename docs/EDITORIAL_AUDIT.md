# Editorial website audit

The source Markdown renderer now separates adjacent headings and lists, escapes
source text and preserves traceability. The case study reflects the hosted site
and authored PBIP project while keeping Desktop execution limitations explicit.
The dashboard generator supplies query parameters, history restoration and an
announced selection summary. The hosted site shares paper/ink/coral styling,
keyboard focus indicators and navigation. The homepage uses a current browser
capture; original Excel and dashboard evidence captures remain untouched.

Validation on 11 November 2026:

- 21 Python tests passed with `-S` and `-O`, including Markdown regressions.
- `python3 -m clubops check`: 760 fixtures, 1,520 club rows, no rejections.
- `python3 scripts/check_site.py`: four pages, 45 local links/assets before
  the screenshot change; unchanged CSV, workbook and dashboard data.
- Local Chromium: five club/season cases, 20 KPI values; reloadable query
  parameters, history, invalid parameters, keyboard selection, visitor journey,
  images and 1440/390px layouts. No console or HTTP errors. Screenshots inspected.
- Dashboard embedded DATA compared equal to the pre-change Git baseline.
- Native Excel and Power BI Desktop acceptance were not rerun on Linux.

The environment denied CONNECT to api.github.com and mrtrauf.github.io.
Consequently PR creation and live deployment verification require those domains
in environment settings. The attempted configuration draft save failed; no
network configuration change or deployment is claimed by this audit.
