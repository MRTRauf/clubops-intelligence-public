# Editorial website audit

## Current v1.0 release status

PRs #1, #2 and [#3](https://github.com/MRTRauf/clubops-intelligence-public/pull/3)
are merged; the final release commit is `1dfa9a8b8ab93f49ec1e291e7f2bfe07a12afb11`.
[Pages run 43089945351](https://github.com/MRTRauf/clubops-intelligence-public/actions/runs/43089945351)
succeeded. Final maintenance independently checked the merge/deployment records
and reran the **24 tests under both -S and -O**, pipeline, packaging and site checks.
The release is deployed; direct public URL rechecks remain blocked by this
environment's network policy. See [v1.0 verification](V1_RELEASE.md) for details.
Older test counts and implementation-time network blockers below are historical.

The source Markdown renderer now separates adjacent headings and lists, escapes
source text and preserves traceability. The case study reflects the hosted site
and authored PBIP project while keeping Desktop execution limitations explicit.
The dashboard generator supplies query parameters, history restoration and an
announced selection summary. The hosted site shares paper/ink/coral styling,
keyboard focus indicators and navigation. The homepage uses a current browser
capture; original Excel and dashboard evidence captures remain untouched.

## Historical audit validation (before PR #1 merge)

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

## Historical network limitation

The implementation environment denied CONNECT to api.github.com and mrtrauf.github.io.
At the time of that audit, PR creation and live deployment verification were blocked.
The merged release and successful deployment above supersede the old pending status. The attempted configuration draft save failed; no
network configuration change or deployment is claimed by this audit.
