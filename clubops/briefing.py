"""Evidence-grounded, deterministic, non-LLM meeting briefing generator."""
from datetime import date, timedelta
from pathlib import Path
from .pipeline import read_csv


def briefing(out_dir: Path, season: str, club: str, as_of: str, days: int = 30) -> str:
    cutoff = date.fromisoformat(as_of)
    if days < 1 or days > 120:
        raise ValueError("--days must be between 1 and 120")
    all_rows = read_csv(out_dir / "club_matches.csv")
    rows = sorted((x for x in all_rows if x["season"] == season and x["club"].casefold() == club.casefold()), key=lambda x: (x["date"], x["match_id"]))
    if not rows:
        raise ValueError(f"No match rows for {club!r} in {season}. Check club_summary.csv for exact names.")
    club_name = rows[0]["club"]
    past = [r for r in rows if date.fromisoformat(r["date"]) < cutoff]
    upcoming = [r for r in rows if cutoff <= date.fromisoformat(r["date"]) < cutoff + timedelta(days=days)]
    last = [r for r in past if int(r["is_complete"]) == 1][-5:]
    missing = sum(int(r["is_complete"]) == 0 for r in past)
    lines = [f"# ClubOps briefing — {club_name}", "", f"**Season:** {season}  |  **As-of date:** {as_of}  |  **Window:** {days} days", "",
             "## Executive summary", f"- Historical league fixtures in source before cutoff: **{len(past)}**.",
             f"- League fixtures listed within window: **{len(upcoming)}**.",
             f"- Past matches lacking a verified final score: **{missing}**.", "",
             "## Upcoming league fixtures in this source"]
    if upcoming:
        lines.extend(f"- {x['date']} — {x['venue']} vs {x['opponent']} ({x['round']})" for x in upcoming)
    else:
        lines.append("- No fixtures found in the selected period. This is not proof that none exist in reality.")
    lines += ["", "## Last five scored league fixtures before cutoff"]
    if last:
        lines.extend(f"- {x['date']} — {x['venue']} vs {x['opponent']}: {x['goals_for']}-{x['goals_against']} ({x['result']})" for x in last)
    else:
        lines.append("- No scored fixtures available in the selected historical window.")
    evidence = {x['match_id']: x for x in read_csv(out_dir / 'matches.csv')}
    lines += ['', '## Traceability', '- Accepted fixture IDs and 1-based raw JSON rows:']
    for row in last + upcoming:
        match = evidence[row['match_id']]
        lines.append(f"- `{row['match_id']}` — source row {match['source_row']}.")
    match = evidence[rows[0]['match_id']]
    lines += [f"- Source snapshot SHA-256: `{match['source_sha256']}`.", f"- Source URL: {match['source_url']}"]
    lines += ["", "## Data caveats", "- Source: openfootball/football.json; community-maintained, not an official LALIGA fixture feed.",
              "- League matches only. Cup and European fixtures are excluded.",
              "- The historical as-of view filters a present-day dataset; it is NOT a true archived point-in-time schedule and may reflect later rescheduling.",
              "- Scores on or after the as-of date are intentionally excluded from historical results.",
              "- Numerical statements above come only from CSV rows. This briefing does not use an LLM.", ""]
    return "\n".join(lines)
