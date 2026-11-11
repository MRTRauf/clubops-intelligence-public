#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m unittest discover -s tests -v
python -m clubops fetch
python -m clubops build
python -m clubops check
printf '\nFinished pipeline. Open data/processed/season_summary.csv and qa_issues.csv.\n'
