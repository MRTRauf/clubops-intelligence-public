"""CLI: fetch | build | check | brief."""
import argparse
import sys
from pathlib import Path
from .pipeline import fetch, build, check
from .briefing import briefing
from .dashboard import write_html


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="ClubOps Intelligence: one-day football operations data MVP")
    sub = p.add_subparsers(dest="command", required=True)
    fetch_p = sub.add_parser("fetch", help="Download configured real upstream JSON data")
    fetch_p.add_argument("--config", type=Path, default=Path("configs/sources.json"))
    fetch_p.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    fetch_p.add_argument("--overwrite", action="store_true", help="Explicitly replace stored raw snapshots")
    build_p = sub.add_parser("build", help="Validate data and export Power BI/Excel-ready CSV")
    build_p.add_argument("--config", type=Path, default=Path("configs/sources.json"))
    build_p.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    build_p.add_argument("--out-dir", type=Path, default=Path("data/processed"))
    build_p.add_argument("--aliases", type=Path, default=Path("configs/aliases.json"))
    check_p = sub.add_parser("check", help="Reconcile generated source and output counts")
    check_p.add_argument("--out-dir", type=Path, default=Path("data/processed"))
    brief_p = sub.add_parser("brief", help="Generate rule-based meeting briefing")
    brief_p.add_argument("--out-dir", type=Path, default=Path("data/processed"))
    brief_p.add_argument("--season", required=True)
    brief_p.add_argument("--club", required=True)
    brief_p.add_argument("--as-of", required=True, help="ISO YYYY-MM-DD (historical cutoff)")
    brief_p.add_argument("--days", type=int, default=30)
    brief_p.add_argument("--output", type=Path, default=Path("artifacts/briefing.md"))
    html_p = sub.add_parser("html", help="Create offline read-only HTML dashboard from real processed CSVs")
    html_p.add_argument("--out-dir", type=Path, default=Path("data/processed"))
    html_p.add_argument("--output", type=Path, default=Path("artifacts/ClubOps_Dashboard.html"))
    args = p.parse_args(argv)
    try:
        if args.command == "fetch":
            results = fetch(args.config, args.raw_dir, args.overwrite)
        elif args.command == "build":
            results = build(args.config, args.raw_dir, args.out_dir, args.aliases)
        elif args.command == "check":
            results = [str(check(args.out_dir))]
        elif args.command == "html":
            results = [f"Written {write_html(args.out_dir, args.output)}"]
        else:
            text = briefing(args.out_dir, args.season, args.club, args.as_of, args.days)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
            results = [f"Written {args.output}"]
        for result in results:
            print(result)
        return 0
    except (OSError, ValueError, KeyError, AssertionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
