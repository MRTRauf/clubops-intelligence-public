# KPI dictionary and accuracy boundaries

| Metric | Calculated from | Definition / limitation |
|---|---|---|
| Fixtures | `club_matches.csv` | One club-match row per accepted fixture for selected season/club. |
| Completed fixtures | `club_matches.is_complete` | Has a valid final score; does NOT prove result officially confirmed. |
| Home / Away | `venue` | Opponent-dependent view; source does not guarantee actual stadium use. |
| W / D / L | goals_for, goals_against | For scored matches only, league results only. |
| Short league-fixture gap | `gap_days_from_previous` | Calendar date difference to prior listed league fixture for same club/season. Threshold <=3 days is illustrative. Not physical recovery time, not all competitions. |
| Average gap | nonempty gaps | Mean observed league calendar-day gap, no season breaks across season boundary. |
| Source completeness | source_records, accepted, rejected | `accepted + rejected = source_records`. QA reasons retained. |
| Result coverage | completed / accepted | Percent of accepted source fixtures with final scores, not official league completeness. |
| Missing to 380 | 380 - accepted | Benchmark ONLY for a 20-club double round-robin, not an authoritative expected source count. |
| Listed upcoming fixtures | date cutoff filtered | Retrospectively filtered current source, **not** a historical as-published archive. |

**Historical reporting caution:** The briefing deliberately hides scores for future fixtures relative to a requested cutoff. But because a downloaded historical file is not a versioned point-in-time schedule, those future fixture dates may have been revised later.

**Data model:** `matches.csv` is match-grain; `club_matches.csv` is club-match-grain (two records per match). Counting club_matches as distinct league games without dividing by two will double count.

**Other limitations:** No attendance, financials, travel times, player GPS, actual training workload, venue changes, European/cup commitments or confidential business operations data.
