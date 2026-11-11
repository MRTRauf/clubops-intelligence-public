# 90-second video demo script

Use the actual local files and application windows. This is a script, not a
claim that a video was recorded or a dashboard was published.

| Time | Show | Say |
|---|---|---|
| 0-10s | README status table | "This independent project helps a simulated Club Office analyst compare league calendars and see data-quality limits. It is not affiliated with LALIGA." |
| 10-25s | Raw 2024-25 JSON and provenance manifest | "These are real public openfootball records with a retained CC0 declaration, a pinned upstream commit and exact file hashes. No club-internal data is used." |
| 25-40s | `python -m clubops check`; season_summary.csv and qa_issues.csv | "There are 760 accepted fixtures across two seasons. The 2024-25 file lists 380 fixtures but only 370 final scores. Ten missing results remain unknown." |
| 40-60s | Real Excel Club Pivot and its scope note | "The native Excel pivot shows Barcelona's short league gaps changing from five to seven. These are calendar gaps, not player rest. All 120 pivot values were reconciled; misleading grand totals are suppressed." |
| 60-80s | artifacts/briefing.md; optionally show its CLI command | "This rules-based briefing has 25 prior fixtures and four listed in the next 30 days. It cites source rows and hides future scores. The schedule is reconstructed from a downloaded file, not archived as known at that date." |
| 80-90s | README limitations and actual HTML screenshot | "The HTML preview is verified locally. Power BI remains a handoff; no Power Query, Power Automate or LLM functionality is claimed. Nineteen tests pass, including the audit regressions." |

Briefing command:

```powershell
python -m clubops brief --season 2024-25 --club "FC Barcelona" --as-of 2025-03-01 --days 30
```

Record against the committed release checkpoint. Do not replace local evidence
with a mocked Power BI screen or claim measured productivity improvements.
