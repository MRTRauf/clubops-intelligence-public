# Public website and dashboard

Latest editorial release checks: see [v1.0 verification](V1_RELEASE.md).

Verified live canonical URL: https://mrtrauf.github.io/clubops-intelligence-public/
GitHub Pages deployment and anonymous live-browser checks succeeded on
11 November 2026. This document describes the deployed boundary and evidence.

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
- Live Chrome checks passed five club/season change-event selections (20 KPI
  values), image loads and visitor navigation at desktop/mobile widths, with
  zero console errors and zero HTTP errors. Evidence:
  artifacts/site_browser_verification.json. Fresh live screenshots use
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

## Verified public deployment

Initial successful workflow: https://github.com/MRTRauf/clubops-intelligence-public/actions/runs/43076119828
Site content commit: a0891cb8d2b7072944dbef74d5bbf5171e880759.
The subsequent evidence commit preserves those website/data bytes and is deployed
through the same workflow; final Actions/remote HEAD confirmation is reported
at task completion. No private repository content is uploaded.

Anonymous HTTP crawl: 18 public HTTPS URLs returned 200, including landing,
dashboard, case study, briefing, CSS, screenshots, workbook/CSV/PBIP downloads
and source/attribution links. Downloaded workbook and CSV bytes match the
verified source artifacts; PBIP archive contains the project and schema license.
Evidence: artifacts/site_http_verification.json.

Live browser journey: landing -> dashboard -> home -> case study -> briefing.
Verified Barcelona (both seasons), Real Madrid 2024-25, Girona 2023-24 and
Valencia 2024-25 through real select change events. Desktop 1440px and mobile
390px checks show no page-level horizontal overflow. Live screenshots were
captured and visually inspected. No authentication or stored session was used.

The original private repository remains unchanged at its existing commit/tag.
No analytics rebuild, Power BI Desktop installation or unrelated repository
modification occurred.
