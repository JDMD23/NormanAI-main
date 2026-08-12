# To the CRMx build agent — round 61: funding lands in CRMx, retire Notion-era husks

JD (2026-08-12) is correctly angry that dead automation was reported instead of retired,
and that Crunchbase funding still isn't a live CRMx uploader.

## Ruling

1. **SQLite CRMx is the only funding SoR.** No parallel Notion funding pipeline.
2. **Retire** legacy `com.normanai.scheduler` (LinkedIn/Crunchbase Notion-era jobs) — unload,
   move plist to Retired, never reload.
3. Empty `crunchbase-funding-watcher` log dirs are **not** a lane. Mark retired until a real
   CRMx tool writes funding_rounds.
4. **Implement** a real funding ingest path that is boring and honest:
   - Primary now: CSV → `norman.tools.ingest_csv` (or current CRMx ingest) → `funding_rounds`
     + company funding fields → optional Notion projection via reconcile only.
   - Next: a Mac-safe "funding watcher" that detects new CSV drops (or attended Crunchbase
     export) and runs that ingest — **not** logged-out Crunchbase scraping (already broken /
     Cloudflare).
5. Cadence: remove `crunchbase` from feeling "automated" in operator docs until the watcher
   records ledger outcomes; keep `manual_sources` until then, or flip only when the watcher
   actually records checks.

## Needs JD
- Where new Crunchbase CSVs will be dropped on the Mac (folder path), once watcher exists.

## Do not
- Reload legacy scheduler. Overnight SN. Invent zeros.