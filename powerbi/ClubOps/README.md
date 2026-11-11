# ClubOps Power BI Project

Open **ClubOps.pbip** in Power BI Desktop. This is a real text-based project
with a TMDL semantic model and enhanced PBIR report definitions, not a PBIX
placeholder or HTML substitute. Desktop was not discovered here, so opening,
refreshing, DAX/M execution and rendering remain manual acceptance steps.

## Contents and data model

- Seven import tables: five existing CSV outputs plus DimSeason and DimClub.
- Fourteen DAX measures in ClubMatches.tmdl; measure locations do not restrict
  which fact tables they reference. Result Coverage is a 0-1 percentage measure.
- Seven explicit many-to-one relationships with single-direction filters.
  DimSeason filters Matches then ClubMatches; it also directly filters
  ClubSummary, SeasonSummary and QA_Issues. DimClub filters ClubMatches and
  ClubSummary. No alternate season path or bidirectional relationship exists.
- Club/season slicers on Club Overview and Fixture & Operations Analytics;
  a season slicer on Data Quality. Each page has bound cards, charts and tables.
- Club Fixtures counts club participations; League Matches counts distinct match
  IDs under the selected clubs. Do not interpret all-club participations as games.
- The operations page compares observed short league calendar gaps. These are
  not player rest, fatigue or all-competition workload measures.

## CSV connections and moving the repository

The M parameter DataFolder in
ClubOps.SemanticModel/definition/expressions.tmdl contains a non-personal setup placeholder. It is intentionally an explicit absolute
path; Power Query does not provide a reliable implicit project-directory base.
Before opening in Desktop, edit that parameter to the new directory with a
trailing slash. Update project_spec.json data_folder to match for static checks.
The supplied validator uses --data-dir (default: repository data/processed)
independently of the configured Desktop path.
Regeneration overwrites authored definitions, so retain custom edits in Git first.

CSV import uses UTF-8 BOM-compatible decoding, named headers, en-US numeric
conversion and explicit column types. Missing numeric cells become null rather
than zero. Dimensions derive from the existing validated CSVs; no new sporting
data or fabricated results have been introduced. This is an import model;
Desktop Refresh is required to materialize its local cache.

## Reproduce static validation

Install `requirements-powerbi.txt` from the repository root, then run:

```powershell
python scripts/validate_pbip.py
```

Ten recursively referenced official Microsoft schemas are cached under schemas/
with their exact URLs and SHA-256 hashes. Validation is offline by default.
`--fetch-schemas` explicitly reacquires them and updates their manifest.
The checker validates 32 schema-bearing JSON files, actual TMDL column and
relationship declarations against the checked specification, CSV paths/counts,
relationship uniqueness/orphans/filter paths and static DAX/visual references.
This is not a Microsoft TOM parser, DAX evaluator or Power Query engine.

Official references:
- https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview
- https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report
- https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview
- https://github.com/microsoft/json-schemas/tree/main/fabric

## Required Desktop acceptance (pending)

1. Enable PBIP/PBIR preview options if required by the installed Desktop version.
   Open ClubOps.pbip; record the actual version and any parse errors.
2. Review DataFolder; permit local-file import and select Refresh. Resolve any
   TMDL/M/DAX errors before describing measures as working in the engine.
3. Confirm Matches 760, ClubMatches 1520, ClubSummary 40, SeasonSummary 2,
   QA_Issues 10, DimSeason 2 and DimClub 23. Inspect relationship directions.
4. Exercise season and club slicers on both analytical pages. For Barcelona:
   2023-24 = 38 fixtures / 38 scored / 5 short gaps / 26 wins;
   2024-25 = 38 / 37 / 7 / 27. Real Madrid 2024-25 = 38 / 37 / 6 / 25.
   Girona 2023-24 = 38 / 38 / 2 / 25. Valencia 2024-25 = 38 / 37 / 3 / 11.
5. On Data Quality select 2024-25: 380 accepted, 370 scored, 10 unknown,
   97.37% coverage and 10 UNSCORED_MATCH warnings. Select 2023-24: 100% coverage
   and zero QA messages. Club slicers are intentionally absent from this page.
6. Verify fixture tables, null gaps/results, chart bindings, interactions and
   measure formatting. JSON schemas cannot verify built-in visual role behavior.
7. Save, close, reopen, refresh again and capture genuine screenshots of all
   three pages. Inspect Git changes; keep .pbi caches/user state ignored.
8. Record observed values and failures in a local acceptance record. Do not replace
   pending checks with a claim that Desktop, DAX or M execution succeeded.

No PBIX file, cloud publication, Excel Power Query integration, Power Automate
flow or LLM capability is implied by this extension.
