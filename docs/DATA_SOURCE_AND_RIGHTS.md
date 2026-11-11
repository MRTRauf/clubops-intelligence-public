# Source audit - 11 November 2026

This is independent educational portfolio work, not official LALIGA data or an internal club system.

## Acquisition and rights evidence

Repository: https://github.com/openfootball/football.json . The README describes public football JSON and the retained `LICENSE.md` declares CC0 1.0 Universal. Copies are in `data/provenance/`; no private or restricted source was used. The project code has its own existing root LICENSE.

Initial `master` downloads were independently compared byte-for-byte with immutable commit **e6744429ee395bc86f247348c6184bb08d4eb361**. GitHub API was used to resolve the commit; pinned bytes and upstream README/LICENSE were fetched before updating config. `data/provenance/manifest.json` records exact acquisition UTC, original URLs, pinned URLs, sizes and hashes. No alternative dataset was substituted.

| Season | Pinned source URL | Bytes | SHA-256 |
|---|---|---:|---|
| 2023-24 | https://raw.githubusercontent.com/openfootball/football.json/e6744429ee395bc86f247348c6184bb08d4eb361/2023-24/es.1.json | 114187 | e4c1e1a958f224ba3c815c898982ab495b9577315cc58ee7a5e7b532960f738b |
| 2024-25 | https://raw.githubusercontent.com/openfootball/football.json/e6744429ee395bc86f247348c6184bb08d4eb361/2024-25/es.1.json | 108296 | da5bfa1b3634e1039d9e71aec50bdc847f8761189e3de235a4e730e0dc64ca38 |

`fetch` and `build` now reject any configured hash mismatch, including an existing snapshot that would otherwise be skipped. Retained bytes make the build reproducible without depending on moving `master`.

## Actual accounting

| Season | Raw | Accepted | Rejected | Scored | Unscored | WARN / REJECT | Distinct raw clubs | Delta to 380 |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| 2023-24 | 380 | 380 | 0 | 380 | 0 | 0 / 0 | 20 | 0 |
| 2024-25 | 380 | 380 | 0 | 370 | 10 | 10 / 0 | 20 | 0 |

Score shapes: 2023-24 has 349 `{ft,ht}` and 31 `{ft}` objects. 2024-25 has 350 `{ft,ht}`, 20 `{ft}` and ten empty `{}` objects. No direct score arrays or malformed score shapes were observed in these real snapshots; array support is synthetic-tested. Half-time is ignored. Empty score objects in 2024-25 source rows 371-380 (Matchday 38) produce ten `UNSCORED_MATCH` warnings. Those raw records remain retained and traceable.

Fixture identities are season + normalized round + home/away keys. No duplicate IDs, slug collisions or repeated ordered home/away pairs were found. Each season has 380 unique ordered pairings; each club has 19 home and 19 away fixtures. This supports calendar coverage, not official certification. The source does not guarantee authoritative dates or scores.

Seventeen club names persist exactly between seasons; no aliases were needed. Departing names: Cádiz CF, Granada CF, UD Almería. Arriving names: CD Leganés, RCD Espanyol de Barcelona, Real Valladolid CF. These set differences are not fuzzy name matches. `configs/aliases.json` remains empty. IDs depend on round labels and reviewed aliases; changes to either require rebuilding all downstream outputs.

## Refresh and manual recovery

For a missing snapshot, save the exact pinned URL above as `data/raw/<season>.json` (raw JSON, not GitHub HTML). Verify with `Get-FileHash -Algorithm SHA256 data/raw/2023-24.json`, compare all 64 hex digits, then run `build`, `check` and the independent validator. Never fill missing results manually without a separately sourced, reviewed change.

Adding a season requires a reviewed config entry with a pinned raw URL and hash. Fetch/build/check use the same multi-season code and Excel tables expand when regenerated. Audit the new source before extending the snapshot-specific independent validator. `scripts/pin_sources.py` documents the original pinning procedure; it resolves current master and stops if its bytes differ from the stored snapshots. It is not a routine refresh command.

## Limits

Community-maintained league data only; no official as-published schedule archive, cup/European matches, venue guarantees, attendance, finance, workload or private operations data. Scored coverage is 100% and 97.37% of accepted fixtures respectively. Full fixture counts do not make 2024-25 results complete. No cross-source official-result audit was performed.
