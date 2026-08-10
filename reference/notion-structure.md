# Notion: the structure, and the one thing that is actually broken

**Verified against the repo, not recalled.**

---

## THE FINDING: your 173 contacts are not on the board at all

```
grep -rn "person|people|contact"  src/norman/operator/projection.py
                                  src/norman/operator/board_schema.py
→  (nothing)
```

**The people table exists in SQLite only. Nothing projects it to Notion.**

So the 173 humans attached to 50 of your 51 prospects — the work of the last two days — are
reachable **only by running a terminal command.** They are not on the surface you actually work
from.

And the two columns that *do* exist, `workplace_contact` and `workplace_contact_email`, are
**singular**. One company, one contact. **A company with a CEO, a COO and a Head of Ops can hold
one of them** — and nothing writes those columns anyway.

> **173 people ↔ 51 companies is one-to-many. Two singular text columns cannot represent it.**
> This is the textbook case for a second Notion database with a relation, and it is the only
> place in Norman where a second database is clearly right.

---

## THE STRUCTURE — two databases, not one, and not five

| database | rows | what it holds |
|---|---|---|
| **Companies** *(exists)* | 133 | the funnel: stage, fit, evidence, action needed |
| **People** *(missing)* | 173 | name, title, company **relation**, LinkedIn, location, matched title, source, checked date |

**A rollup on Companies gives you what you actually want on the board:** *contact count*, *best
title*, *has a reachable channel*. One number per company, computed from the relation, no
duplication.

**Do not go past two.** The received Notion wisdom is *"5–8 properties per database; more means
you needed a relation"* — and your board has ~46. **That advice is for hand-maintained
databases.** Yours is a **projection of a SQLite store** (ADR 0001), regenerable and never the
source of truth, so wide is fine. **The rule that applies to a projection is different: split
when the CARDINALITY differs, not when the column count grows.**

Companies and people have different cardinality. Everything else on that board is 1:1 with a
company and belongs where it is.

---

## THE VIEWS, once People exists

Each answers one question on one axis (see `reference/funnel-structure-proposal.md`):

1. **Chase list** — `Stage ∈ {Prospect, Top Pursuit}` ∧ `Disposition` blank, sorted Fit Raw desc
2. **My queue** — `Action Needed` starts with `Joe:` — *empties, which is what makes it a queue*
3. **What moved** — change origin = *company*, not *system*
4. **Outgrowing** — `Stage = Recently Signed Lease`, sorted by utilisation *(your ruling)*
5. **Pipeline flow** — entries and exits per stage per week
6. **Call list** *(on People)* — filter to target titles, group by company, sorted by company Fit

**View 6 is the one that turns 173 rows into a morning's work.**

---

## AUTOMATION — where the line sits, and why

Notion's own automations are real but thin, and there is a rule that decides what belongs where:

> **Notion automates the SURFACE. Norman automates the SUBSTANCE.**

| belongs in Notion | belongs in Norman |
|---|---|
| status change → notify | anything that computes a value |
| a checkbox → set a date | anything that reads an external source |
| formula/rollup display | anything that decides a stage |

**Anything that computes belongs in the reconcile loop, because ADR 0001 makes the board a
rebuildable view.** A Notion automation that writes a value the store does not know about
**creates a second source of truth** — the exact drift the reconcile loop exists to eliminate.

**One exception worth taking: rollups.** A rollup is *derived display*, not stored truth. It
cannot drift because it is recomputed from the relation every time it renders.

---

## WHAT NOT TO DO

- **Do not split Companies into more databases.** Wide is correct for a projection.
- **Do not automate a computation in Notion.** It becomes a second writer the reconcile loop
  cannot see.
- **Do not hand-maintain a view Norman could declare.** `config/board-views.json` exists so the
  views are reproducible; the Notion API cannot create them, so you build them once by hand and
  the config is the record of intent.
- **Do not add a property to hold something with different cardinality.** That is what the
  contact columns did, and it is why they are empty.

---

## THE ORDER

1. **Project People to Notion** with a relation to Companies. The data already exists; only the
   projection is missing.
2. **Rollups on Companies**: contact count, best title, has-channel.
3. **The call-list view** on People.
4. The funnel re-partition *(separate, larger, `reference/funnel-structure-proposal.md`)*.

**Step 1 is the whole gap.** Everything after it is configuration.
