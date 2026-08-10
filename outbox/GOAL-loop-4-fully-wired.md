# GOAL: every board column is fed or retired, and company #134 arrives complete

**To the CRMx build agent.** Loop 4. **The checklist is frozen and you may not edit it.**

JD is about to send a new CSV. **The test is not "fill in today's blanks."**

> **The test is: does a company that arrives TOMORROW get every field, without anyone
> remembering to run something?**

Backfilling the current 93 is half the work. The half that matters is whether the pipeline
populates these for company #134 on its own.

---

## BAND A — the four Notion writes

All four are computable from data already in the store. **No measurement, no fetch, no credits.**

| property | source | note |
|---|---|---|
| **`NYC Δ`** | `nyc_employees − prev_nyc_employees` | Blank when there is no prior reading. **A first measurement has no delta and that is not zero.** |
| **`Desk Jobs`** | `nyc_jobs_in_office + 0.8 × nyc_jobs_hybrid` | JD's weighting. Remote counts zero. Blank where the careers lane never ran — that is a coverage gap, not a zero. |
| **`NYC Band`** | banded `nyc_employees` | **Select, not formula.** The projection must emit one of the eight option strings exactly or Notion rejects the write. |
| **`Reach`** | the contacts table | `Both` / `LinkedIn` / `Email` / `None` from what each company's people actually carry. **`None` only when contacts exist and none is reachable** — a company with no contacts yet is blank, not `None`. |

**A1 · Project all four.**
**A2 · Confirm `Intensity` and `Signal` populate themselves** — both are formulas downstream of
`Desk Jobs` and `NYC Δ`. Nothing to write; verify they fill.
**A3 · The observable: for each of the 93 rows, every one of the four is either populated or
blank for a stated reason.** Report the counts, not a summary.

**Before writing `NYC Band`, run the distribution.** JD's bands are linear; startup headcount is
log-distributed. If most of the board lands in the first two bands, **say so** — the option list
is changeable, but only deliberately.

---

## BAND B — the thirteen empty fields: feed each one or retire it

Your own field detector found **13 fields empty on every row.** Several are on the board as
columns.

> **A column that is empty on every row is a promise the system is not keeping.** For each one,
> make a decision and record it: **FEED** (name the source), or **RETIRE** (remove from the
> board; the field stays in the store).

| field | first question to answer |
|---|---|
| `months_a_to_b` · `months_b_to_c` · `months_late_stage` · `months_seed_to_a` | Velocity is now wired. **Do these populate as a side effect, or were they always display-only?** Four board columns hold nothing today. |
| `nyc_jobs_senior` · `nyc_jobs_facilities` | **The desk-role classifier computes role types. Why is nothing stored?** `Head of Workplace` as a buy signal was the whole point of that work. |
| `nyc_heads_manhattan` | §3b's Manhattan-tight geography. Is there a source, or was it never built? |
| `down_round` · `layoffs_hit_nyc` | **Both are scoring inputs.** A scoring input that is empty everywhere is an inert component — the `hq_city` problem in a new place. |
| `workplace_contact` · `workplace_contact_email` | **Superseded by the contacts table and `Reach`.** Strong retire candidates. |
| `employee_band` | This is `NYC Band`'s store-side counterpart. Feed it in Band A. |
| `removed_at` · `removed_reason` | Tombstoning fields. Empty is probably correct — confirm and move on. |

**B1 · One line per field: FEED with a named source, or RETIRE with a reason.**
**B2 · Execute the FEEDs. Remove the RETIREs from the board only** — never from the store.

---

## BAND C — the contacts reach the board

**173 people exist in SQLite and are projected nowhere.**

**C1 · Write the roster into each company's page body**, the same way the fit math already is:
name · title · matched target title · LinkedIn · location · source · date checked.
**C2 · `Reach` derives from that roster** (overlaps A) — one derivation, not two.
**C3 · Add a company-level `last_touched_on`**: entity field, store column, reconcile field map,
and the blank-is-an-adoption list. **Without it, JD's "Called today" button writes a value the
store never sees**, and it would be lost on a board rebuild.

`last_touched_on` currently exists **on the person only**. Company-level and person-level are
different questions; **the company value wins when present, with person dates as detail.**

---

## BAND D — the 93 / 133 gap

**The board holds 93. The store is reported to hold 133.**

```sql
SELECT COUNT(*) FROM companies;
SELECT COUNT(*) FROM companies WHERE notion_page_id IS NULL;
SELECT status, COUNT(*) FROM companies WHERE notion_page_id IS NULL GROUP BY status;
```

**The third query is the finding.** Tombstoned or Do-Not-Pursue is working as designed.
**Any Prospect in that set means the projection has been silently dropping companies** — which
would outrank everything else in this loop.

**D1 · Run all three and report the breakdown.**
**D2 · If any non-terminal status appears, stop and escalate before Band E.**

---

## BAND E — will company #134 arrive complete?

**This band is the point of the loop.**

**E1 · The growth component.** JD approved the direction: **`growth` keys on active NYC hiring
and fresh funding — the two signals §1b names that the intake can actually supply — with
velocity a refinement where dated round history exists.**

Because `funding_rounds` is fed by nothing and a Crunchbase CSV carries no dated history,
**every CSV company would otherwise arrive with growth excluded and be scored on a renormalized
formula relative to the existing board.**

**Bundled into the same change: `fresh_raise_growth_pts` (14) must come within the `growth`
weight (10)**, and add the boot check beside `formula_is_coherent` — that rule already catches
this class and missed this instance.

> **This is a GATED change. Simulate → show JD the movers with one concrete company beside the
> rate → apply → oracle → re-freeze.** Approval of a direction is not approval of an apply.

**E2 · Bound `rescore`'s scope.** It has no scope flag, so `--apply` in a batch pipeline lands
the 40 first-scorings JD deferred in round 28 — **a decision nobody would be taking.**

**E3 · THE ACCEPTANCE TEST — ingest one synthetic company and follow it end to end.**

Not the existing 93. **A new row, arriving the way a CSV row arrives**, through the whole
pipeline: ingest → careers → score → route → project → contacts → chase.

**Then read its board row and account for every column:**

```
populated          — with what, from where
blank, correctly   — no evidence exists yet, and that is the honest state
blank, WRONGLY     — a source exists and nothing carried it   ← every one of these is a defect
```

**A single column in the third category means the pipeline is not wired.** That is the exact
failure this loop exists to prevent, and it is invisible until a real batch arrives.

Use a clearly synthetic name, and **delete the row afterward** — the board is JD's working
surface.

---

## THE LOOP

```
budget: 3 passes. Not 4.
each pass: run A + B + C + D + E → fix only what failed → re-run ALL of them
all green → stop
after pass 3 with anything red → escalate the specific criterion. No fourth pass.
```

**Frozen scope: anything found that is not on this checklist goes to `found-not-fixed.md` —
recorded, not fixed.** Two exceptions: data loss, or risk to JD's LinkedIn account.

**One report at the end. Not one per finding.**

---

## OUT OF SCOPE

The render pass and careers-URL discovery · the property set and scheduler *(loop 3 — still
queued)* · Sales Nav coverage *(human-gated, JD's go)* · floor storage · any new scoring signal
beyond E1 · **ingesting JD's real CSV. This loop proves readiness; it does not consume the
batch.**

---

## SUCCESS

**A CSV arrives and every company on it lands with every column either populated or blank for a
reason someone can state.** No column empty because a projection was never written. No component
scored on a different formula than the board it joins.

**And the proof is E3 — one synthetic company, followed end to end, with every column accounted
for.** Not an assertion that it works. A row you can look at.
