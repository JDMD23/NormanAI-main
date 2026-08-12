# To the CRMx build agent — round 62: Crunchbase saved-search watcher (JD session)

JD override 2026-08-12 (COS chat): the CSV drop folder is NOT enough.

He has a **logged-in Crunchbase session on the Mac** and a saved search:

- Name: Main funding / August 2026
- URL: https://www.crunchbase.com/discover/saved/main-funding-august-2026/730c458b-149c-4a0a-9684-7146e7258993

**Wanted:** check that saved search **~4× per day**, read populated companies, write into
**CRMx SQLite → Notion projection**. Not a parallel Notion pipeline.

## Ruling (updates round 61 / ADR 0018)

1. **CSV drop lane stays** as the offline/manual fallback (`~/Drops/crunchbase`).
2. **New primary path:** Mac job using JD’s existing browser session (account-bound =
   ADR 0012 class). Prefer export-to-CSV from the saved search UI, then existing
   `funding_lane` / `funding_ingest` — reuse parsers, Unknown≠0, idempotent SHA ledger.
3. **Do not** logged-out scrape. **Do not** reload `com.normanai.scheduler`.
4. Cadence target: **4× weekdays** in waking hours (suggest 9:00 / 12:00 / 15:00 / 18:00 ET
   or 8/11/14/17 — pick one set; avoid overnight).
5. After ingest: reconcile to Notion. **Rescore still gated** (show movers) unless JD
   later chooses unattended score apply.
6. Fail closed on Cloudflare / logout / challenge — alert COS, do not retry-storm.

## Needs from Mac proof before merge
- Confirm Chrome profile session can open the saved search.
- Choose: UI CSV export automation vs DOM table extract → CSV shim.

## Needs JD
- Confirm 4× times if defaults wrong.
- Confirm companies from this search may create/update CRMx rows (intake), not only
  funding fields on existing companies.