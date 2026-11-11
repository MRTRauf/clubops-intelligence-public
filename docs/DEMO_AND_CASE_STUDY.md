# ClubOps Intelligence: portfolio case study

Independent public-data project. Release evidence dated 11 November 2026.
No LALIGA or club affiliation, endorsement or internal data access.

## Business question

How are listed league fixtures distributed across clubs and seasons, where are
short calendar gaps, and which source results are trustworthy enough for a
meeting briefing? A simulated Club Office analyst needs consistent reporting
with source quality visible alongside the numbers. The project deliberately
avoids player rankings, forecasting and invented operational or financial KPIs.

## Source and lawful-use evidence

Two Spanish Primera JSON files come from openfootball/football.json, whose
retained README and license declare CC0. Their bytes match upstream commit
`e6744429ee395bc86f247348c6184bb08d4eb361`. The acquisition manifest records
exact URLs, verification UTC, sizes and SHA-256 hashes. Builds reject changed
pinned inputs. Upstream's dedication was verified; all underlying rights and
sporting facts were not independently certified against an official feed.

## Data model and automation

A standard-library Python CLI turns raw JSON into a match-grain table, two
club-perspective rows per accepted fixture, club-season aggregates, season QA
summaries and a warning/rejection ledger. Retained raw records and 1-based
source-row references make each result traceable. Reviewed aliases are explicit;
no fuzzy matches or guessed results were introduced.

Calendar gaps use consecutive listed league dates within a club and season.
Unknown results contribute fixture dates but never wins, draws or losses.
The reusable flow is fetch, build, check, brief and HTML generation. Excel
regeneration reads the CSVs, populates named tables and formulas, and uses
native Excel automation to build and verify a season/club PivotTable.

## Useful result and its business implication

Both seasons contain 380 fixtures and 20 clubs. All 760 raw records are accepted,
producing 1,520 club-fixture rows and 40 club-season summaries. However,
2024-25 Matchday 38 has ten empty score objects: only 370 results are scored,
for 97.37% coverage. These remain visible as unknown results and ten warnings.
A complete-looking fixture count therefore cannot justify a complete results
report. The analyst should disclose that gap before presenting season outcomes.

Barcelona has five league gaps <=3 days in 2023-24 and seven in 2024-25.
These independently reconciled values appear in club_summary.csv and
artifacts/validation_summary.md and can be compared in the actual Excel pivot.
They identify dates worth reviewing against a full competition calendar; they
do not establish fatigue or physical recovery needs.

## Verification and audit response

All 19 tests pass both with site packages disabled and with Python optimization.
Regression cases reject corrupted club rows and summaries, altered duplicate
fixtures and colliding club keys. Required validation uses explicit exceptions.
The original synthetic unscored example was changed to a distinct opponent so
it remains a valid fixture under the stricter league duplicate rule.

Raw-derived calculations reconcile all 40 summaries, all accepted fixtures and
the two club perspectives. Repeat builds produce identical CSV bytes. In
Excel 16.0, the report was calculated, saved and reopened; all 120 pivot values
match CSVs. The audit's misleading grand totals are suppressed, its grain is
explained, and shortened captions/wider columns are visible in refreshed real
screenshots. Five actual Chrome renders reconcile 20 displayed KPI values.

The Barcelona briefing as of 1 March 2025 shows 25 prior fixtures, four in the
30-day window, zero prior unknown results and five prior wins. It includes
fixture IDs and source provenance, hides future scores, and clearly describes
a retrospective reconstruction rather than an archived schedule.

## Release boundaries

The public GitHub Pages site hosts the dashboard, case study and traceable
briefing, with optional CSV, Excel and PBIP source downloads. The dashboard is
an HTML application over pinned historical data, not a live data service.
Club and season controls support shareable URLs and browser history.

The PBIP project includes a seven-table model, 14 DAX definitions, seven
relationships, three report pages and 23 bound visuals. Its 32 schema-bearing
files pass ten cached Microsoft schemas. Power BI Desktop acceptance remains
pending: TMDL engine parsing, M/DAX execution, refresh, rendering and interactions
are not verified. No PBIX, Power Automate flow or LLM feature is claimed.

Local browser checks exercise dropdown changes, navigation and desktop/mobile
layouts. Cross-machine Excel acceptance, extra seasons and external review
remain pending. No time-saving or real-client impact measurement is claimed.

For a short presentation, use VIDEO_DEMO_SCRIPT.md. Reproduction and recorded
verification results are in the project README and VALIDATION.md.
