# Validation evidence

Generated from raw JSON and actual CSV exports by `python scripts/validate_outputs.py`.
A second build produced byte-identical CSVs. Assertions use independent raw-record calculations.

| Season | Raw | Accepted | Rejected | Scored | Unknown | QA | Raw names | Delta to 380 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023-24 | 380 | 380 | 0 | 380 | 0 | 0 | 20 | 0 |
| 2024-25 | 380 | 380 | 0 | 370 | 10 | 10 | 20 | 0 |

## Independent club-season checks (all 40)

| Season | Club | Fixtures | Scored | H/A | W/D/L | Gaps <=3d | Mean gap |
|---|---|---:|---:|---|---|---:|---:|
| 2023-24 | Athletic Club | 38 | 38 | 19/19 | 19/11/8 | 1 | 7.76 |
| 2023-24 | CA Osasuna | 38 | 38 | 19/19 | 12/9/17 | 3 | 7.73 |
| 2023-24 | Cádiz CF | 38 | 38 | 19/19 | 6/15/17 | 3 | 7.7 |
| 2023-24 | Club Atlético de Madrid | 38 | 38 | 19/19 | 24/4/10 | 4 | 7.7 |
| 2023-24 | Deportivo Alavés | 38 | 38 | 19/19 | 12/10/16 | 2 | 7.73 |
| 2023-24 | FC Barcelona | 38 | 38 | 19/19 | 26/7/5 | 5 | 7.76 |
| 2023-24 | Getafe CF | 38 | 38 | 19/19 | 10/13/15 | 7 | 7.76 |
| 2023-24 | Girona FC | 38 | 38 | 19/19 | 25/6/7 | 2 | 7.73 |
| 2023-24 | Granada CF | 38 | 38 | 19/19 | 4/9/25 | 2 | 7.68 |
| 2023-24 | Rayo Vallecano de Madrid | 38 | 38 | 19/19 | 8/14/16 | 3 | 7.78 |
| 2023-24 | RC Celta de Vigo | 38 | 38 | 19/19 | 10/11/17 | 1 | 7.76 |
| 2023-24 | RCD Mallorca | 38 | 38 | 19/19 | 8/16/14 | 2 | 7.78 |
| 2023-24 | Real Betis Balompié | 38 | 38 | 19/19 | 14/15/9 | 2 | 7.73 |
| 2023-24 | Real Madrid CF | 38 | 38 | 19/19 | 29/8/1 | 4 | 7.76 |
| 2023-24 | Real Sociedad de Fútbol | 38 | 38 | 19/19 | 16/12/10 | 4 | 7.76 |
| 2023-24 | Sevilla FC | 38 | 38 | 19/19 | 10/11/17 | 3 | 7.81 |
| 2023-24 | UD Almería | 38 | 38 | 19/19 | 3/12/23 | 3 | 7.78 |
| 2023-24 | UD Las Palmas | 38 | 38 | 19/19 | 10/10/18 | 3 | 7.78 |
| 2023-24 | Valencia CF | 38 | 38 | 19/19 | 13/10/15 | 2 | 7.81 |
| 2023-24 | Villarreal CF | 38 | 38 | 19/19 | 14/11/13 | 4 | 7.73 |
| 2024-25 | Athletic Club | 38 | 37 | 19/19 | 19/13/5 | 5 | 7.65 |
| 2024-25 | CA Osasuna | 38 | 37 | 19/19 | 12/15/10 | 4 | 7.57 |
| 2024-25 | CD Leganés | 38 | 37 | 19/19 | 8/13/16 | 4 | 7.57 |
| 2024-25 | Club Atlético de Madrid | 38 | 37 | 19/19 | 21/10/6 | 4 | 7.54 |
| 2024-25 | Deportivo Alavés | 38 | 37 | 19/19 | 10/11/16 | 3 | 7.59 |
| 2024-25 | FC Barcelona | 38 | 37 | 19/19 | 27/4/6 | 7 | 7.59 |
| 2024-25 | Getafe CF | 38 | 37 | 19/19 | 11/9/17 | 3 | 7.62 |
| 2024-25 | Girona FC | 38 | 37 | 19/19 | 11/8/18 | 3 | 7.65 |
| 2024-25 | Rayo Vallecano de Madrid | 38 | 37 | 19/19 | 13/12/12 | 4 | 7.54 |
| 2024-25 | RC Celta de Vigo | 38 | 37 | 19/19 | 15/7/15 | 3 | 7.59 |
| 2024-25 | RCD Espanyol de Barcelona | 38 | 37 | 19/19 | 10/9/18 | 3 | 7.51 |
| 2024-25 | RCD Mallorca | 38 | 37 | 19/19 | 13/8/16 | 4 | 7.54 |
| 2024-25 | Real Betis Balompié | 38 | 37 | 19/19 | 16/11/10 | 4 | 7.59 |
| 2024-25 | Real Madrid CF | 38 | 37 | 19/19 | 25/6/6 | 6 | 7.54 |
| 2024-25 | Real Sociedad de Fútbol | 38 | 37 | 19/19 | 13/7/17 | 3 | 7.54 |
| 2024-25 | Real Valladolid CF | 38 | 37 | 19/19 | 4/4/29 | 5 | 7.51 |
| 2024-25 | Sevilla FC | 38 | 37 | 19/19 | 10/11/16 | 1 | 7.62 |
| 2024-25 | UD Las Palmas | 38 | 37 | 19/19 | 8/8/21 | 1 | 7.59 |
| 2024-25 | Valencia CF | 38 | 37 | 19/19 | 11/12/14 | 3 | 7.54 |
| 2024-25 | Villarreal CF | 38 | 37 | 19/19 | 19/10/8 | 3 | 7.54 |

## Schema and names

- 2023-24 score keys: {'ft,ht': 349, 'ft': 31}. Only full-time scores are used; half-time is ignored.
- 2024-25 score keys: {'ft,ht': 350, 'ft': 20, 'empty object': 10}. Only full-time scores are used; half-time is ignored.
- 17 exact club names persist across seasons; no aliases applied. Departing: ['Cádiz CF', 'Granada CF', 'UD Almería']. Arriving: ['CD Leganés', 'RCD Espanyol de Barcelona', 'Real Valladolid CF'].
- 2024-25 rows 371-380 (Matchday 38) have empty score objects: ten warnings, no invented results.
- All 380 ordered home/away pairs occur once in each season; each club has 19 home and 19 away fixtures. This supports fixture coverage but is not official certification.

## Briefing audit

- FC Barcelona / 2024-25 / cutoff 2025-03-01: 25 prior fixtures, 4 in [March 1, March 31), 0 prior unscored.
- Upcoming dates: 2025-03-02, 2025-03-16, 2025-03-27, 2025-03-30. No scores in that section.
- Last five prior results checked in raw: 7-1, 1-0, 4-1, 1-0, 2-0 (all Barcelona wins).
- Retrospective reconstruction: March 27 Osasuna date is from the acquired file, not a March 1 archived schedule.

## Assumptions and limits
- Calendar-day gaps use consecutive listed league dates, reset each season, include unscored fixtures, and are not player rest or all-competition workload.
- 380 is a benchmark only. Result coverage uses accepted records as denominator.
- Raw hash and alias config determine output. Independent validator deliberately stops for unexpected rejects or changed schemas.

## Deterministic CSV SHA-256

- `club_matches.csv`: `801eed73c3d79b47dc7008e1775d7565a17f169eeaddbba49d4936a84d96267b`
- `club_summary.csv`: `86224e3678e38119622b06a62d35be0cfab95128bf20acb8cc98f88dc50d6922`
- `matches.csv`: `ccaa301eebddb7c3862d3d21e0d663b002462959c91f340fc4dbdccbcbfc82ce`
- `qa_issues.csv`: `ebdb22d3b89422b929ad2d25d9cff38397d815aadeba0935f782097302c15d00`
- `season_summary.csv`: `cd3fc9d95974253c3fae2f993e42a2193b18ad518c176186e30146eff5815ac1`
