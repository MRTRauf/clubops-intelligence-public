# Public website and dashboard

## Current v1.0 release status

PRs #1, #2 and [#3](https://github.com/MRTRauf/clubops-intelligence-public/pull/3)
are merged; the final release commit is `1dfa9a8b8ab93f49ec1e291e7f2bfe07a12afb11`.
[Pages run 43089945351](https://github.com/MRTRauf/clubops-intelligence-public/actions/runs/43089945351)
succeeded. Final maintenance independently checked the merge/deployment records
and reran the **24 tests under both -S and -O**, pipeline, packaging and site checks.
The release is deployed; direct public URL rechecks remain blocked by this
environment's network policy. See [v1.0 verification](V1_RELEASE.md) for details.
Older test counts and implementation-time network blockers below are historical.

Latest editorial release checks: see [v1.0 verification](V1_RELEASE.md).

Canonical website URL: https://mrtrauf.github.io/clubops-intelligence-public/
The initial publication had successful deployment and anonymous live-browser
checks on 11 November 2026. That earlier evidence is distinguished below from
the final deployment and current maintenance checks.

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

The hosted dashboard is generated from clubops/dashboard.py and the verified
CSV snapshot. Packaging supplies shared navigation and editorial CSS while
preserving its embedded DATA object and analytical control logic. The original
offline artifact remains available in source for reproducibility.

## Historical initial publication checks

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

## Historical initial public deployment

Initial successful workflow: https://github.com/MRTRauf/clubops-intelligence-public/actions/runs/43076119828
Site content commit: a0891cb8d2b7072944dbef74d5bbf5171e880759.
The subsequent evidence commit preserved those website/data bytes and used
the same workflow. The current final deployment is recorded above. No private repository content is uploaded.

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
