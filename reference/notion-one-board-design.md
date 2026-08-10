# One database, designed properly — 50 properties down to 24

**JD's ruling: one database.** This is the right call for company-first work, and it is not a
compromise — see §5 for what it costs and why the cost is acceptable.

---

## THE PRINCIPLE

> **A property is not storage. It is an ANSWER to a question you ask while scanning.**
> The page body is for deciding once you have stopped scanning.

Everything Norman knows is already in SQLite. **Nothing is lost by moving a property to the page
body** — ADR 0001 makes the whole board a rebuildable projection, and the page body is part of
that projection. This is purely about what earns a column in a list you scan.

**Round 3 already ruled this once** — *"fit math moves to page body"* — and the eight `Fit:`
component columns came back anyway. This is that ruling, applied and held.

---

## THE CUT — 50 → 24

### KEEP AS COLUMNS (24) — you filter, sort, or read these while scanning

**Identity & funnel (6)**
`Company` · `Status` · `Fit Score` · `Fit Raw` *(hidden, sort key)* · `Fit Drivers` · `Headquarters`

**The evidence you actually rank on (4)**
`NYC Employees` · `NYC Open Jobs` · `Industries` · `Funding Velocity`

**Reachability — NEW (4)** *(see §3)*
`Best Contact` · `Best Contact Title` · `Reachable` · `Contacts`

**Your queue (3)**
`Action Needed` · `Data Status` · `Re-check` *(human)*

**Change & freshness (3)**
`Changes` · `Last Checked` · `Next Check Due`

**Yours (4)**
`Relationship Notes` · `Current Angle` · `Website` · `Careers Page`

### MOVE TO PAGE BODY (26) — read when you are already on the company

**The eight `Fit:` component columns** — `Employees` · `Jobs` · `Growth` · `Industry` ·
`Funding` · `Investors` · `Stage` · `HQ`
> You never filter on "Fit: Investors". You read **Fit Drivers** to know why. **Eight columns
> freed, and the math is more legible as a block than as eight cells.**

**The four `Months:` columns** — `Seed→A` · `A→B` · `B→C` · `Late Stage`
> **All four were flagged EMPTY by the detector.** Four columns holding nothing.

**Funding detail (6)** — `Latest Funding $M` · `Latest Funding Date` · `Latest Round` ·
`Total Funding $M` · `Funding Rounds` · `Key Investors`
> Context for a call, not a scan criterion. `Funding Velocity` stays because you rank on it.

**Reference links (4)** — `Crunchbase` · `X Profile` · `LinkedIn` · `Founders`

**Provenance (4)** — `Added On` · `Added From` · `Checked` · `Company Summary`
> `Company Summary` is a paragraph. **A paragraph in a column is a paragraph you cannot read.**

### REPLACE (2)
`Workplace Contact` · `Workplace Contact Email` → the four reachability properties in §3.
**Both are singular, both are empty, and neither can hold a one-to-many relationship.**

---

## CONTACTS IN ONE DATABASE — the four properties that do it

173 people, 51 companies, one board:

| property | type | what it is |
|---|---|---|
| **Best Contact** | text | the name at the highest-ranked target title |
| **Best Contact Title** | text | so you see *CEO* vs *Office Manager* at a glance |
| **Reachable** | select | `LinkedIn` · `Email` · `Both` · `None` |
| **Contacts** | number | how many people we know there |

**The full roster lives in the page body** — every person, title, LinkedIn, location, source,
date checked — written by reconcile, same as the fit math.

> **This is better than a relation for company-first work**, because the answer to *"can I act on
> this row?"* is visible in the list without a click. `Reachable = None` is the single most
> useful filter on the board and it does not exist today.

---

## THE VIEWS — six, each one question on one axis

1. **Chase list** — `Status = Prospect` ∧ `Reachable ≠ None`, sorted `Fit Raw` desc
2. **My queue** — `Action Needed` starts with `Joe:` — *empties, which is what makes it a queue*
3. **What moved** — `Changes` non-empty ∧ origin = company
4. **No way in** — `Reachable = None` ∧ `Fit Score` high → *the gap worth closing*
5. **Outgrowing** — `Status = Recently Signed Lease`, sorted by utilisation *(your ruling)*
6. **Pipeline flow** — entries/exits per stage per week

**View 4 is new and it is the one that pays.** A high-fit company you cannot reach is a *specific,
solvable* problem — and today it is indistinguishable from a low-fit company you are ignoring.

---

## WHAT ONE DATABASE COSTS, stated so you are choosing it knowingly

**You lose the person-first view.** You cannot sort 173 humans by title across all companies, or
track per-person state — *called · replied · met* — because a person is not a row.

**Why that is the right trade for you:** you work company-first. You open the chase list, pick a
company, then ask who to call. You do not scan a list of humans. **The person is how you reach
the company, not the unit of work.**

**When to revisit:** the day you want to track outreach per person — who you called, when, what
they said. **That is a per-person state machine, and it cannot live in a company row.** Until
then, one board is correct.

---

## ORDER

1. **The four reachability properties + the roster in the page body.** This is the whole gap —
   173 contacts currently reach the board not at all.
2. **Demote the 26.** Nothing is lost; the store already holds all of it.
3. **View 4 — "No way in".** Free once `Reachable` exists.
4. The funnel re-partition — separate and larger
   *(`reference/funnel-structure-proposal.md`)*.
