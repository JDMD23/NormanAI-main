# To the CRMx build agent — four properties the Notion board now needs

The board was rebuilt: 9 views, buttons, and 7 new properties. **Integrity proved** — 4,650
SHA-256 hashes across 93 rows, identical digest before the build, after property creation, and
after view creation. **No row value was touched.**

**Four of the new properties are yours to write, and all four are computable from data already in
the store.** Until they are written, three views are empty — not broken, just unfed.

---

## THE FOUR

| Notion property | type | source | note |
|---|---|---|---|
| **`NYC Δ`** | number | `nyc_employees − prev_nyc_employees` | **Both fields already exist.** Blank when there is no prior reading — a first measurement has no delta, and that is not zero. |
| **`Desk Jobs`** | number | `nyc_jobs_in_office + 0.8 × nyc_jobs_hybrid` | JD's own weighting. Remote roles count zero. |
| **`NYC Band`** | select | banded `nyc_employees` | Options exist and are **blank on all 93 rows**. See the constraint below. |
| **`Reach`** | select | the contacts table | `Both` / `LinkedIn` / `Email` / `None` from what each company's people actually carry. |

**Blank ≠ zero on every one of these.** An unmeasured company gets a blank band, not `0-20`. A
company with no prior reading gets a blank delta, not `0`.

---

## THE CONSTRAINT ON `NYC Band` — it must be a SELECT, and Notion is strict

We wanted a formula. **Notion rejected it: *"Group-by property of type formula does not support
grouping."*** So it is a Select with eight fixed options:

```
0-20 · 20-40 · 40-60 · 60-80 · 80-100 · 100-150 · 150-200 · 200+
```

**The projection must write one of those exact strings or the API errors.** A value not in the
option list is rejected — this is not a free-text field.

**Run the distribution before trusting the cuts.** JD's bands are linear; startup headcount is
roughly log-distributed. If most of the board lands in the first two bands, say so — the option
list can be changed, but only deliberately.

---

## WHAT IS EMPTY UNTIL YOU WRITE THEM

| view | current state |
|---|---|
| **BY SIZE** | all 93 rows in one "No NYC Band" group |
| **HIRING** | empty — `Desk Jobs > 0` matches nothing |
| **HEALTH · NYC BAND** | a single bar |

**`Signal`** renders partial output correctly — a company with only headcount shows `0 NYC`, and
gains `· +12 · 9 desks` as the inputs arrive. **Nothing needs changing there; it just needs
feeding.**

---

## THE ONE THING THAT ISN'T A WRITE

**`Reach` is currently owned by the machine and there is no lane that produces it.** That is a
fifth instance of the built-but-unfed pattern unless it goes into the same projection pass as
the other three. **Put it in the same change.**

---

## STILL OPEN, SEPARATELY

**The board has 93 rows. The store is reported to hold 133.** The build proved preservation for
the 93 only. **Three queries settle it:**

```sql
SELECT COUNT(*) FROM companies;
SELECT COUNT(*) FROM companies WHERE notion_page_id IS NULL;
SELECT status, COUNT(*) FROM companies WHERE notion_page_id IS NULL GROUP BY status;
```

**The third line is the one that matters.** Tombstoned or Do-Not-Pursue is working as designed.
**Prospects would mean the projection has been silently dropping companies** — and that would be
a larger finding than anything in this build.

**This is not blocking. It goes after loop 3.**
