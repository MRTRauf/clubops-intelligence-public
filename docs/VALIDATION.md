# Validation evidence

Public snapshot checks: 11 November 2026. No analytics dataset, report or model
was rebuilt during curation. Synthetic tests use temporary fixtures only.

## Checks rerun for this distribution

- `python -S -m unittest discover -s tests -v`: 19 tests, OK (0.828 seconds).
- `python -O -m unittest discover -s tests -v`: 19 tests, OK (0.522 seconds).
- `python -m clubops check`: 2 seasons, 760 matches, 1,520 club rows, 0 rejected.
- Existing independent raw-reconciliation checks executed read-only, omitting
  their rebuild and report-writing steps: all 760 fixtures, 1,520 club rows and
  40 summaries passed. Real CSV byte-determinism remains earlier recorded
  evidence; synthetic deterministic-build regression passed in the test suite.
- `python scripts/validate_pbip.py --data-dir data/processed`: 32 documents,
  ten official schemas, seven tables, seven relationships, fourteen measure
  definitions and 23 visual references checked. Zero orphan keys or ambiguous
  filter paths. This is static validation, not DAX/M execution.

## Preserved application evidence

The original Excel 16.0 verification created/calculated/saved/reopened a native
PivotTable and reconciled all 120 measure values. Formula totals, focus values
and a season change were checked. Grand totals are suppressed to avoid confusing
club participations with distinct matches. Existing Excel screenshots are genuine.

The public workbook is the same reporting artifact with only private saved-path,
last-editor and pivot-refresh-author metadata removed from its ZIP/XML package.
Worksheet data, cached formulas, PivotTable definitions and records are retained.
The sanitized workbook was also opened read-only in Excel 16.0 during curation:
all 120 pivot values, suppressed totals and the cached 760-fixture total passed.
No save or file-byte change occurred. The private original remains unchanged.
The screenshots predate this metadata
cleanup and show the same numerical report content.

Five original Chrome-rendered views reconciled 20 displayed KPIs and 12 fixture
rows per view. Existing browser screenshots are retained; no new browser test
or screenshot capture is claimed during public curation. Rendering checks are
not manual accessibility certification or live dropdown-event tests.

## Data quality and scope

2023-24: 380 accepted/scored fixtures. 2024-25: 380 accepted fixtures, 370 scored,
ten unknown Matchday 38 results and ten warnings. Every ordered home-away pair
occurs once per season; 380 is a benchmark, not official certification.
The Barcelona briefing has 25 fixtures before 1 March 2025 and four in the
30-day window, with no future scores and explicit retrospective limitations.

Original source hashes, exact URLs and CC0 dedication are retained in
[data provenance](../data/provenance/manifest.json). Schema URLs/hashes and the
Microsoft MIT license are retained under [schemas](../powerbi/ClubOps/schemas/).

## Acceptance still pending

Power BI Desktop was not available: Microsoft TMDL deserialization, Power Query
refresh, DAX evaluation, native rendering, slicer interactions and save/reopen
acceptance remain unverified. The PBIP guide supplies five club reconciliation
cases. There is no claimed PBIX, LLM feature, Power Automate flow or deployment.
