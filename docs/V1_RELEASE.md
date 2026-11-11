# ClubOps Intelligence v1.0 editorial verification

Editorial release candidate, checked on 11 November 2026. This finishes the
briefing and case study; it does not rebuild analytics or establish new Excel
or Power BI Desktop evidence.

## Checks executed for this release

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

## Release status

GitHub API and both public Pages URLs returned network-policy denials in this
environment. PR creation, merge, deployment and live HTTPS verification remain
pending. This document records local release-candidate checks, not publication.
