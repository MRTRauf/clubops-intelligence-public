$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m clubops fetch
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m clubops build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m clubops check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Finished pipeline. Review data/processed/season_summary.csv and qa_issues.csv."
