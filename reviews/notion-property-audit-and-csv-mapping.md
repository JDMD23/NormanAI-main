# Notion property audit + Crunchbase CSV mapping (for the CRMx rebuild)

Design input for the ground-up rebuild (NormanAI-CRMx). Audits the **81
properties** of the current board (from crm-core's committed
`crm-property-dictionary-v1.json` — the authoritative schema; the live Notion
link is behind login and could not be read directly, but this dictionary *is* the
board's schema) and maps the real Crunchbase CSV (133 Series-A companies, 23
columns) into the new database.

## The headline decision (flows from "datastore = truth, Notion = view")

Because the real datastore now holds the truth and **Notion becomes a clean
operator view**, roughly **a third of the current properties come OFF the board**
and live in the datastore instead. The current board carries 19 `audit`
timestamp/score-component fields, 5 `machine` work-queue flags, and several
technical automation fields — that machinery belongs in the datastore + receipts,
not cluttering the operator's screen. This single move declutters Notion
dramatically *and* implements the source-of-truth decision. The new board shows
the operator what they need to act; the datastore remembers everything else.

## What the CSV gives you (intake → new properties)

The CSV is clean (amounts already integers, dates ISO). At intake a company lands
`Status = Research`, **no Fit Score yet** (brain/10 #5: score only when evidence
is complete). Column → new property mapping, with the coercion rule:

| CSV column | New property | Coercion / rule |
|---|---|---|
| Organization Name | **Company** (title) | trim; identity key with Website/LinkedIn |
| Organization Name URL | **Crunchbase Profile** (url) | as-is |
| Website | **Website** (url) | normalize scheme; primary identity signal |
| LinkedIn | **LinkedIn Company Page** (url) | as-is (1 blank → leave blank, never "0") |
| X (Twitter) | **X Profile** (url) | 70/134 blank → blank, not fabricated |
| Headquarters Location | **Headquarters** (text) + City/State/Country | split `"New York, New York, United States"` → 3 parts |
| Founded Date | **Founded** (year) | take year; keep precision below |
| Founded Date Precision | (internal) `founded_precision` | year vs exact — governs display |
| Industries | **Industries** (multi-select) | declared multi-value split on `", "` (inside the quoted cell) |
| Founders | **Founders** (multi-select/text) | multi-value split; 7 blank → blank |
| Last Funding Date | **Latest Funding Date** (date) | ISO as-is |
| Last Funding Amount (in USD) | **Latest Funding Amount — $M** (number) | USD ÷ 1,000,000 → millions |
| Last Funding Type | **Latest Funding Round** (select) | "Series A" etc. |
| Total Funding Amount (in USD) | **Total Funding — $M** (number) | USD ÷ 1,000,000 |
| Number of Funding Rounds | **Funding Round Count** (number) | int |
| Top 5 Investors | **Key Investors** (multi-value) | split on `", "` |
| Lead Investors | (into **Key Investors** / lead flag) | 2 blank → blank |
| Description | **Company Summary** (text) | short |
| Full Description | (into `Funding Evidence`/body) | 13 blank → blank |

**Unknown ≠ 0 throughout:** every blank stays blank/Unknown (brain/04, brain/10
#4). A missing funding amount is "not found," which the Crunchbase lane later
fills — never `0`.

## The property audit — TAKE / TRANSFORM / LEAVE-from-Notion

### TAKE — the operator-facing core (stays on the new board)
**Entity & evidence (CSV-populated):** Company · Website · LinkedIn Company Page ·
Crunchbase Profile · Careers Page · X Profile · Headquarters · Founded · Founders ·
Industries · Company Summary · Latest Funding Amount $M · Latest Funding Date ·
Latest Funding Round · Total Funding $M · Funding Round Count · Key Investors ·
Funding Evidence · Funding Momentum.
**NYC evidence (enriched later):** NYC Employees · NYC Jobs · NYC Employee History ·
NYC Job History · Hiring Evidence.
**Decision core:** Fit Score · Fit Data Quality · Why This Fit Score · Status ·
Priority Score · Priority Tier · Why This Priority · Review Reason · Missing Fit Data.
**Change surface:** What Changed · Changed At · Why Fit Changed · Fit Score Change ·
Key People Changes.
**Human-owned (JD authority — never machine-written):** Relationship Notes ·
Current Angle · Angle History · Workplace Contact · Workplace Contact Email ·
the protected/relationship Statuses.
**Provenance kept visible:** Added On · Added From.

### TRANSFORM — keep the value, change the shape
- **The 5 operator-card fields** (At a Glance · Where It Stands · Why This Result ·
  Data Check · Next Step) + **What You Need to Do** + **Why This Fit Score / Why
  This Priority**: keep, but as **derived projections computed from the datastore**,
  not hand-maintained columns (brain/10 #11; rendergit dual-reader). The card is a
  *view* of the truth, regenerated on reconcile — this is where the operator
  clarity lives.
- **The 2 operator-command fields** (Resume Automation · JD Careers Finding): keep
  a *minimal* set as the human→machine control surface (how JD's decisions flow
  back — brain/10 #10). These are the only "write-back from Notion" fields.
- **Founded / precision**, **HQ → City/State/Country**: reshape as in the CSV map.

### LEAVE the Notion board (move to the datastore + receipts)
- **All 19 `audit` fields** — NYC/Funding/Employees Checked-At timestamps, the six
  `Fit — <component>` sub-scores, Fit Model Version, Prior Fit Score, Fit Score
  Changed At, Priority Checked At, the `Automation — *` technical fields. These are
  machine bookkeeping (brain/10 #7: operational outcomes are a *separate*
  vocabulary from business state) — they belong in the datastore/outbox/receipts,
  surfaced only in a "Full Audit" view or on demand, not as board columns.
- **All 5 `machine` queue flags** (Check Careers/Crunchbase/LinkedIn · Recalculate
  Fit · Priority Needs Refresh): the work queue lives in the scheduler/datastore,
  not as Notion checkboxes. (The `Need-*` pattern moves off the board.)
- **The 2 `retire` fields** (Legacy Automation Summary · Empty NYC Jobs Change 30D):
  drop entirely — tombstoned already.

### DEFER — build the slot, populate later
- **The 2 `future` warm-path fields** (Check Warm Path · Warm Path Checked At) →
  owned by the `warm_path` context; design the fields, populate when that context
  is built.

## Net effect
- **New board ≈ 45–50 clean, operator-facing properties** (entity, evidence,
  fit/status/priority, the derived operator card, human-owned, minimal command
  surface) — down from 81, with the machine bookkeeping moved to the datastore.
- **~30 properties move off the board** into the datastore/receipts (all audit +
  machine + technical automation + retired).
- The CSV populates the intake set; enrichment lanes fill NYC + refresh funding;
  the scorer fills Fit/Status; second pass fills Priority; the operator card is
  *derived*, not stored.

## Open items to confirm with JD (design of the new board)
1. **Which properties are you actively acting on daily?** Anything you never look
   at is a candidate to move off-board even if it's "active" today.
2. **Are there properties only in the live Notion, not in the dictionary?** If the
   board drifted from the committed schema, export its property list (or grant a
   Notion connection) and I'll reconcile — but the dictionary should be complete.
3. **The control surface:** confirm the minimal set of write-back-from-Notion
   commands you want (Resume Automation, Careers finding, protected-status edits).
