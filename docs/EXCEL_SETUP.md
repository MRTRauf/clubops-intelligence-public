# Excel report - actual status and refresh

`excel/ClubOps_Excel_Starter.xlsx` remains unchanged and was opened read-only in Excel. `artifacts/ClubOps_Reporting_COMPLETED.xlsx` is the populated report, created separately using the starter sheet structure.

## Actually verified in desktop Excel 16.0

- Tables: SeasonData on Season Summary (two records), ClubData on Club Summary (40 records), QAIssues on QA Issues (ten records).
- Overview: SUM/COUNTA totals, coverage formula, and season/club SUMIFS selectors in B12/B13. Counts: 2 seasons, 760 fixtures, 750 scored, 10 unknown, 0 rejected; coverage 98.68% across both seasons.
- FC Barcelona 2024-25 focus: 38 fixtures, 37 scored, 27 wins, 7 gaps <=3 days. Changing focus to 2023-24 recalculated scored fixtures to 38, then the demonstration was restored.
- Club Pivot: genuine `ClubSeasonPivot`, club rows, season columns, sum fixtures/scored/short gaps. Both grand totals are suppressed; short captions and wider columns identify the per-club grain. Every one of 120 season-club measure cells was checked via Excel GetPivotData against CSVs.
- The file was saved, closed and reopened; native PivotTables count and cached formula value were checked again. Overview and pivot were exported by Excel to PDFs. Genuine Excel-window screenshots were captured and visually inspected.

Evidence: `artifacts/excel_verification.json`, `artifacts/screenshots/Excel_Overview.png`, `Excel_Club_Pivot.png`, The redundant PDF exports are omitted from this distribution.

This is application-automated verification plus screenshot inspection. An independent human walkthrough and cross-machine Excel compatibility remain pending. There is no embedded Power Query or external connection in the workbook. Regeneration is the implemented refresh method.

## Supported refresh (additional reviewed seasons included)

1. Review/pin a source in configs/sources.json and acquire its real raw file. Do not remove hash checks to bypass a discrepancy.
2. Run `python -m clubops build`, `python -m clubops check` and the appropriate source/aggregate audit. Inspect QA first.
3. Close the generated workbook. Install optional reporting dependency with `python -m pip install -r requirements-reporting.txt` if needed.
4. Run `python scripts/build_excel.py`. This intentionally recreates the report from CSVs and resets custom workbook edits. It leaves the native PivotTable pending.
5. Run `powershell -NoProfile -File scripts/complete_excel.ps1` in a logged-in Windows desktop session with Excel. It creates/refreshes the pivot, recalculates, reconciles and reopens the saved workbook. Failure means verification is pending, regardless of filename.

The source and club tables expand from CSV row counts. Source accounting and total-formula checks use actual season_summary values. The historical Barcelona demonstration still checks the two audited seasons. Review fixed date/caveat text when adding seasons. An extra real season was not fetched or tested in this build.

## Manual CSV / Power Query alternative

In a copy of the workbook, use Data > Get Data > From Text/CSV for club_summary.csv and season_summary.csv. Choose UTF-8, comma delimiter, keep season/club/keys/hash as Text, counts as Whole Number, average_gap_days/result_coverage_pct as Decimal Number. Missing numeric values should become null, not zero.

Load data into tables and name them ClubData/SeasonData (remove or replace existing tables first). Overview formulas use those exact table and header names. If table names differ, update formulas explicitly. Do the same for QAIssues. A manual CSV replacement must resize each table to include every new row.

Select ClubData > Insert > PivotTable > new worksheet. Rows=club; Columns=season; Values=sum fixtures, sum completed, sum short_gaps_le_3_days. Refresh the pivot after changing the table. Compare Barcelona values above and at least four more entries in artifacts/validation_summary.md. Save, reopen and capture the real application. These are manual instructions, not a claim that an embedded query exists.

## Implementation finding

Excel refused a generated file that had overlapping worksheet-level AutoFilter and table filters. Removing the worksheet AutoFilter fixed it; the named tables keep their own working filters. The final report opened without repair. The original template was not modified.
