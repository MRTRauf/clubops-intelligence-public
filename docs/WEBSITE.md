# Public website and dashboard

Intended canonical URL: https://mrtrauf.github.io/clubops-intelligence-public/
The final deployment and live-browser checks must succeed before hosting is
reported complete. This document describes the deployment contract.

## Visitor journey

Landing page -> interactive historical dashboard -> case study -> traceable
briefing. All visitor pages, images, stylesheets, CSVs and workbook/PBIP downloads
are served from the public GitHub Pages project. Source/attribution links use
public HTTPS GitHub endpoints. No accounts or local installation are required.

## Deployment boundary

Only site/ is uploaded by .github/workflows/pages.yml. The curated directory has
four HTML pages, one stylesheet, genuine existing screenshots, pinned reporting
CSVs, source license/provenance and public download bundles. Internal prompts,
private history, handoffs, caches and development environments are not deployed.
The private backup repository is unchanged.

The hosted dashboard reuses artifacts/ClubOps_Dashboard.html. Packaging adds
portfolio navigation, a historical-data label and mobile/focus styling; its
embedded DATA object and analytical control logic are preserved. The original
offline artifact remains available in source for reproducibility.

## Checks

- Nineteen Python tests pass; the existing reporting integrity check passes.
- Four pages and 42 relative references pass scripts/check_site.py.
- Hosted CSV and workbook bytes match the existing verified artifacts.
- Landing coverage numbers match actual season_summary.csv values.
- Local Chrome preview passes five club/season selections via live change events,
  desktop/mobile layouts (1440/390 pixels), images and visitor navigation.
- Local browser console and HTTP error collections are empty.
- Final live evidence is written to artifacts/site_browser_verification.json by
  the browser checker after successful deployment. Fresh live screenshots use
  Website_Desktop.png, Website_Mobile.png and Dashboard_Mobile.png.

The browser checker uses an isolated ignored profile. Its temporary loopback
server is for local QA only; no loopback link appears in deployed content.
Static packaging and the public Pages URL work under the repository subpath.

## Limitations

Historical public data, not live LALIGA information. Ten results remain unknown;
league gaps are not physical rest. No LALIGA affiliation or business impact is
claimed. The PBIP source download is statically validated only: Desktop
rendering, refresh and DAX/M execution remain pending. Its DataFolder setup
placeholder is an offline Desktop configuration, not a website link. No LLM or
Power Automate implementation is claimed. Responsive checks and basic labeled
controls/alt text do not constitute a full accessibility certification.
