# ClubOps Intelligence v1.0 editorial verification

## Current v1.0 release status

PRs [#1](https://github.com/MRTRauf/clubops-intelligence-public/pull/1),
[#2](https://github.com/MRTRauf/clubops-intelligence-public/pull/2) and
[#3](https://github.com/MRTRauf/clubops-intelligence-public/pull/3) are merged.
PR #3 was squash-merged into `main` as
`1dfa9a8b8ab93f49ec1e291e7f2bfe07a12afb11` on 11 November 2026.
[GitHub Pages run 43089945351](https://github.com/MRTRauf/clubops-intelligence-public/actions/runs/43089945351)
reports **Success** for that commit. These merge and workflow results were
independently checked against the public GitHub pages and remote Git history
during final maintenance.

The final suite contains **24 tests**, passing with both `-S` and `-O`.
Final maintenance reran both suites, the pipeline check, site packaging and
site validation. No new Excel, Power BI Desktop or browser acceptance is claimed.
The earlier local browser evidence remains documented below and in the release
verification notes.

The release is deployed. Direct HTTPS rechecks of the public website and
dashboard remain blocked by this maintenance environment's network policy;
that limitation does not indicate a deployment failure. Earlier statements
about blocked PR creation or pending release deployment are historical.


Final editorial release, checked on 11 November 2026. This finishes the
briefing and case study; it does not rebuild analytics or establish new Excel
or Power BI Desktop evidence.

## Final editorial release checks (before merge)

- 24 Python tests passed under both `python -S -m unittest discover -s tests -v`
  and `python -O -m unittest discover -s tests -v`.
- `python -m clubops check`: two seasons, 760 fixtures, 1,520 club rows,
  no rejected records.
- `python scripts/prepare_site.py` and `python scripts/check_site.py`:
  four pages, 50 relative references, unchanged verified CSV and Excel bytes.
- Chromium visited homepage → case study → dashboard → briefing → homepage
  through actual links. All five existing dashboard selections and their 20 KPI
  values passed, alongside URL/history, reload and keyboard filter checks.
- The two release articles passed at 1440, 768, 390 and 320px. Images loaded,
  one h1 per article, no page-level horizontal overflow. Fixture tables use
  labeled, keyboard-focusable horizontal scroll regions on narrow screens.
- Enter opened the native evidence disclosure from keyboard focus. The source
  hash was present, all four upcoming and five recent fixtures were rendered.
- No browser console errors or missing resources. Desktop/mobile screenshots
  were captured and inspected. These checks are not a full accessibility audit.
- Page generation was repeated to check byte-identical article HTML. Original
  data, analytics code, dashboard, PBIP and Excel files remain unchanged.

## Earlier evidence and limits

Excel 16.0 calculation/reopen and reconciliation of 120 PivotTable values remain
earlier evidence, not a current Linux test. The Power BI project's 32 documents
and ten cached schemas remain earlier static evidence; no Desktop parsing,
M/DAX execution, refresh or rendering is claimed. No official cross-source
reconciliation, client impact measurement, LLM or Power Automate flow is claimed.

## Historical environment limitation before PR #3 merge

The implementation environment denied GitHub API and public Pages access.
At that point PR creation, merge, deployment and live HTTPS verification were
pending. PR #3 and successful deployment now supersede that release status;
direct public Pages verification is still blocked in the maintenance environment.
