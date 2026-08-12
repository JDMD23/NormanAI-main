# Norman — complete system map and 360° review

**Two documents in one.** Part I maps every component, every Notion property, every view, every
lane, and how they connect. Part II is the review: **17 findings, ranked by impact.** Several are
defects I introduced.

**Sources:** the live board capture (`reference/captures/notion-board-audit-2026-08-10.json`), the
build spec (`outbox/CODEX-PROMPT-build-notion-views.md`), the approval deltas
(`CODEX-approve-notion-build.md`, `CODEX-answers-notion-build.md`), `FIT-SCORING-SPEC.md`, the
65-round ruling log, and `reference/properties.py`.

**What I could not read:** the CRMx source, and the post-build Notion configuration — the build
report lives on Codex's machine and is not in either repo. **That is itself finding #4.**

---
---

# PART I — THE MAP

---

# 1 · The whole system on one screen

```
┌─ INPUTS ────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Crunchbase CSV        Company websites       Sales Navigator      Apollo   │
│  (manual export)       (public, free)         (JD's login)         (API)    │
│       │                     │                      │                  │     │
└───────┼─────────────────────┼──────────────────────┼──────────────────┼─────┘
        │                     │                      │                  │
        ▼                     ▼                      ▼                  ▼
   ┌─────────┐         ┌────────────┐         ┌────────────┐      ┌──────────┐
   │ ingest  │         │  CAREERS   │         │ SALES NAV  │      │ CONTACTS │
   │  _csv   │         │    LANE    │         │  headcount │      │   LANE   │
   └────┬────┘         └─────┬──────┘         └─────┬──────┘      └────┬─────┘
        │                    │                      │                  │
        │              free · no risk         ATTENDED · 80/day    ~4 credits
        │              minutes               2 days per 50 cos     per 50 cos
        │                    │                      │                  │
        └────────────┬───────┴──────────────────────┘                  │
                     ▼                                                 │
        ┌────────────────────────────┐                                 │
        │   THE PER-COMPANY BARRIER  │  ← score only when ALL lanes    │
        │   all lanes terminal?      │    are terminal for THIS company│
        └────────────┬───────────────┘                                 │
                     ▼                                                 │
        ┌────────────────────────────┐                                 │
        │  SCORE  (9 components/100) │                                 │
        │  ROUTE  (score → status)   │                                 │
        └────────────┬───────────────┘                                 │
                     ▼                                                 │
   ╔═════════════════════════════════════════════╗                     │
   ║          SQLite  —  THE TRUTH               ║ ◄───────────────────┘
   ║   companies · contacts · change log ·       ║
   ║   check ledger · funding_rounds (empty)     ║
   ╚═══════════════════╤═════════════════════════╝
                       │  reconcile_sweep --apply
              ┌────────┴────────┐
              │                 │
       ADOPT ▲│                 │▼ HEAL
    (JD's edits)│               │ (machine columns only)
              │                 │
   ╔══════════╧═════════════════▼══════════════════╗
   ║        NOTION  —  A REBUILDABLE VIEW          ║
   ║  93 rows · 61 properties · 9 views · 4 buttons║
   ║  1 automation, DISABLED                       ║
   ╚═══════════════════════════════════════════════╝
                       │
                       ▼
              ┌─────────────────┐
              │   chase list    │  ranked, with a named human
              └─────────────────┘
```

**Read the two arrows between SQLite and Notion carefully.** They are the whole integrity story:
**ADOPT runs before HEAL, always.** JD's edits go up into the store before any machine value comes
down.

---

# 2 · Infrastructure inventory — every moving part

| component | where it lives | what starts it | risk |
|---|---|---|---|
| **SQLite store** | CRMx repo, local file | — | the single point of truth; **backed up how?** ← unverified |
| **`ingest_csv`** | `norman.tools` | **JD types it** | none |
| **Careers lane** | `contexts/careers` | **JD types it** | none — public APIs |
| **Browser daemon** (careers bind) | `core/lanes` | the careers lane | low — public sites |
| **Sales Nav measurement** | **no command exists** | **JD, manually, per session** | **highest in the system** |
| **`rescore`** | `norman.tools` | **JD types it** | scoring drift if unscoped |
| **`reconcile_sweep`** | `norman.tools` | **JD types it** | writes to Notion |
| **`contacts_lane`** | `contexts/contacts` | **JD types it** | Apollo credits |
| **`chase`** | `contexts/priority` | **JD types it** | none |
| **`session_start`** | `norman.tools` | **JD types it** | none — read-only ritual |
| **Notion database** | `JD Workflow` workspace | — | presentation only |
| **Notion automation** | the board | **would be Friday 8am** | **currently disabled** |
| **Notion buttons ×4** | the board | **JD clicks** | two write fields with problems |
| **Scheduler / cron / CI** | **DOES NOT EXIST** | — | **finding #3** |
| **Board config backup** | **DOES NOT EXIST** | — | **finding #4** |

**Three external accounts, three different risk profiles:**

| account | exposure | protection |
|---|---|---|
| **LinkedIn / Sales Nav** | **JD's real identity — a ban costs him his professional network** | dedicated browser profile · per-session approval · 80 views/day · **halt on first challenge, no retry** |
| **Apollo** | credits (money) | dry-run default · `--print-query` before `--apply` · measured 4 credits/50 |
| **Notion** | data integrity | reconcile's three laws · integrity hashes |

---

# 3 · Automation — the complete and honest truth

## What runs on a schedule, anywhere in the system

> **Nothing.**

**That is not a summary. It is the literal inventory:**

| mechanism | status |
|---|---|
| cron | **absent** |
| `.github/workflows/` | **absent** |
| a Norman-side scheduler process | **absent** |
| Notion automations | **one exists, and it is disabled** |
| Notion buttons | **exist — but a button is a human clicking, not automation** |

## What *looks* like automation but is not

**The check ledger.** Norman computes, per company, when each field is next due for a re-check —
`Next Check Due` is a real property with real dates in it. **Something calculates when work is
due. Nothing fires when it comes due.** The ledger is a calendar nobody reads.

**The careers lane's own source comment:**

```python
# src/norman/contexts/careers/fetch.py
# "...which is why it is the first lane cleared to run unattended."
```

**It hits public job-board APIs. No login. No ban risk. Explicitly cleared. And nothing starts
it.**

## The three automations that were designed and deliberately killed

| # | trigger | action | why it was cut |
|---|---|---|---|
| 1 | `Status` → `Top Pursuit` | notify | **JD sets Top Pursuit himself** — notifying him of his own click |
| 2 | `Action Needed` → any `Joe:` | notify | Notion's bell only reaches him **when he is already in Notion**, where he'd see the queue anyway |
| 3 | Page added | notify | **the next CSV would fire 50 notifications in one minute** |

**The reasoning, which is the durable part:** JD's ping-worthy events are **things companies do**
— new funding, leadership change, acquisition, customer win, headcount announcement. Automations
1–3 are **things Norman did.**

> **Notifying him about Norman's bookkeeping is the noise that trains him to ignore the
> notification that eventually matters.**

## The one automation that survived, and its design principle

**Friday 8am → email `joseph.dapice@cbre.com` with a link to the CHANGED view.**

**It must send every Friday unconditionally, including weeks when nothing changed.** If it only
sent when there was news, a silent Friday would mean *either* nothing happened *or* the automation
broke — and those would be indistinguishable.

> **An always-sends digest makes its own failure visible.**

**Status: built, disabled, pending a Gmail/Outlook authorization JD has not granted.** Which means
**zero automations are live.**

## The boundary that governs anything automated

> **Norman writes DATA. Codex configures PRESENTATION. Notion may display anything and decide
> nothing.**

**Formulas and rollups are safe** — they recompute on render and cannot drift out of sync.

**An automation that WRITES a machine-owned property is not safe.** It creates a second source of
truth the reconcile loop cannot see, and reconcile would heal it away **silently, with no error
anywhere.** This is not theoretical — see finding #11.

---

# 4 · The Notion board — every property, what it means, who owns it

**61 properties = 50 original + 7 added in the rebuild + 4 buttons.**

**Ownership is the most important column.** `MACHINE` means reconcile will overwrite your edit.
`HUMAN` means it is adopted and never overwritten. `FORMULA` means it computes on render.

## 4.1 · Identity and funnel position

| property | type | owner | what it means |
|---|---|---|---|
| **Company** | title | machine | the row's name. Identity is actually the **domain**, not this |
| **Status** | select · **14 options** | **HUMAN wins** | funnel position. **Overloaded — see finding #9** |
| **Fit Score** | number | machine | **0–100, rounded.** The headline number |
| **Fit Raw** | number | machine | **unrounded.** The system's own rule says *ranking uses this* — see finding #6 |
| **Fit Drivers** | multi-select · 10 | machine | *why* in plain words: `Big NYC team` · `Hiring hard` · `Fast riser` · `Small NYC team` · `Few NYC roles` · `Slow riser` · `Tiny NYC team` · `No NYC roles` · `Estimate` · `Missing data` |
| **Headquarters** | select · 10 | machine | `NYC · SF · LA · Boston · Austin · Seattle · Chicago · Other US · International · Unknown`. **Load-bearing** — the stall penalty is HQ-conditional |

**The 14 Status values, and the five different questions they answer:**

```
where in the funnel  Research · Prospect · Top Pursuit · Engaged · Active TIM · Client/Dealflow
why it's out         Not a Fit · Low NYC Presence · Do Not Pursue
how cold             Tracking · Watchlist
what's blocking      Needs Review · Needs Angle
a timing event       Recently Signed Lease
```

## 4.2 · The evidence you rank on

| property | type | owner | what it means |
|---|---|---|---|
| **NYC Employees** | number | machine | **the leading signal.** Sales Nav NYC-**metro** — wider than JD's real target |
| **NYC Δ** ⭐ | number | machine | change since the previous reading. **Blank ≠ 0** — a first measurement has no delta |
| **NYC Open Jobs** | number | machine | open NYC roles from the ATS |
| **Desk Jobs** ⭐ | number | machine | **`in-office + 0.8 × hybrid`.** JD's weighting. **Remote counts zero — a remote worker needs no desk** |
| **Intensity** ⭐ | formula | formula | `Desk Jobs ÷ NYC Employees`, shown as %. *10 jobs on 15 people is a rocket; 10 on 300 is routine* |
| **NYC Band** ⭐ | **select** | machine | `0-20 · 20-40 · 40-60 · 60-80 · 80-100 · 100-150 · 150-200 · 200+`. **Select, not formula — Notion refuses to group by a formula.** The projection must emit one of those exact strings or the API rejects the write |
| **Signal** ⭐ | formula | formula | one-line summary: `47 NYC · +12 · 9 desks`. Renders partial input correctly |
| **Industries** | multi-select · 14 | machine | `AI · Cybersecurity · Healthcare · Fintech · Legal · PropTech · HR · GTM/Sales · Web3 · Data/Analytics · Dev Tools · Consumer · Software · Other`. **Qualification, not a fine tilt** |
| **Funding Velocity** | select · 6 | machine | `Fast · Normal · Slow` **and `Fast (est.) · Normal (est.) · Slow (est.)`** — the `(est.)` suffix is the honesty marker. Most of the board is `(est.)` |

⭐ = **created in the rebuild and written by nothing today.** See finding #13.

## 4.3 · The fit math — eight component columns

`Fit: Employees` · `Fit: Jobs` · `Fit: Growth` · `Fit: Stage` · `Fit: Funding` · `Fit: HQ` ·
`Fit: Industry` · `Fit: Investors` — all number, all machine.

**These also render as a readable block in the page body**, which is where they belong. From a
real company (Remark), verbatim:

```
Employees 6/34 (2 NYC metro) · Jobs 0/26 (0 NYC roles, location-type unknown, 0% of team)
· Growth 2/10 (Slow est.) · Stage 0/8 (2 vs ~18 expected at series-a) · HQ 6/6 (NYC-based)
· Industry 5/5 · Funding 4/8 ($26.3M) · Investors 1/3
```

**That single line is the most valuable artifact on the board** — it shows the score, the weight,
and the *evidence* for every component. Fit Score = 24.

## 4.4 · Funding and investors

| property | type | note |
|---|---|---|
| **Latest Round** | select | **one option exists: `Series A`** — the whole board came from one CSV |
| **Latest Funding $M** · **Total Funding $M** · **Funding Rounds** | number | context, not rankers |
| **Latest Funding Date** | date | **recency is what elevates funding to a growth signal** |
| **Key Investors** | multi-select · **311 options** | see finding #17 |
| **Lead Investors** | multi-select · **161 options** | same |
| **Months: Seed→A · A→B · B→C · Late Stage** | number ×4 | **empty on every row** — see finding #14 |

## 4.5 · Reachability

| property | type | status |
|---|---|---|
| **Reach** ⭐ | select | `Both · LinkedIn · Email · None`. **Written by nothing** |
| **Workplace Contact** · **Workplace Contact Email** | text · email | **superseded, empty, retire candidates** |
| **Best Contact** · **Best Contact Title** · **Contacts** | — | **DESIGNED AND NEVER CREATED — finding #5** |

## 4.6 · Your queue and your notes

| property | type | owner | note |
|---|---|---|---|
| **Action Needed** | select · 7 | mixed | `Joe: paste careers link` · `Joe: decide status` · `Joe: verify NYC count` · **`Joe says: no careers page`** · `Norman: Sales Nav count pending` · `Norman: recheck scheduled` · `Norman: LinkedIn jobs fallback` |
| **Re-check** | checkbox | **human** | you asking for a re-measure |
| **Relationship Notes** · **Current Angle** | text | **human** | never overwritten |
| **Last Touched** ⭐ | date | **human** | written by the `Called today` button. **No matching store field — finding #12** |

> **The `Joe:` vs `Joe says:` distinction is load-bearing.** `Joe:` = *the queue is waiting on
> you*. `Joe says:` = *a fact you already supplied.* A naive prefix match refills your queue with
> the answer you already gave — and it did, once, until it was fixed.

## 4.7 · Provenance and change tracking

| property | type | note |
|---|---|---|
| **Added On** · **Added From** | date · select | **one source option today:** `crunchbase-csv:series-a-2026-08` |
| **Last Checked** · **Next Check Due** | date | **`Next Check Due` is machine-owned** — a button writing it would be healed away |
| **Checked** | multi-select | which instruments ran: `CB · LI · Careers · News` |
| **Data Status** | select | `Verified · Partial · Review · Bad data` |
| **Changes** | multi-select · 11 | `First check · Fit ↑ · Fit ↓ · New Round · Funding ↑ · Jobs ↑ · Jobs ↓ · Heads ↑ · Heads ↓ · Status Δ · Velocity Δ` |

> **`Changes` mixes two different truths** — *what the company did* (`New Round`, `Heads ↑`) and
> *what Norman did* (`Fit ↑` after a rescore). **That is finding #2, and it is the largest
> user-visible defect on the board.**

## 4.8 · The four buttons

| button | writes | verdict |
|---|---|---|
| **Chase this** | `Status` → `Top Pursuit` | ✅ correct — Status is human-wins |
| **Not a fit** | `Status` → `Not a Fit` | ✅ correct |
| **Called today** | `Last Touched` → today | ⚠️ **no store field — the value dies on a board rebuild** |
| **Not now** | `Status` → `Tracking` **+ `Next Check Due` → +90d** | 🔴 **`Next Check Due` is machine-owned. Reconcile heals it away silently** |

---

# 5 · The nine views — filter, sort, group, size

**Design rules applied throughout:**

1. **One question, one axis.** A view answering two questions answers neither.
2. **Every view declares whether it can EMPTY.** A *queue* empties; a *report* cannot.
3. **Every view declares an expected size.** Blowing past it means **something upstream broke —
   it is not a filter to tune.**
4. **Sort by value**, so clearing half a queue means clearing the half that mattered.
5. **Max 7 columns.** More scrolls sideways and stops being scannable.

| # | view | filter | sort | expect | **actual** |
|---|---|---|---|---|---|
| 1 | **CHANGED** | `Changes` not empty **AND** not containing `First check` **AND** `Last Checked` within past week | `Last Checked ↓` | **5–15** | **🔴 74** |
| 2 | **PROSPECTS** | `Status` is `Prospect` | `Fit Score ↓` → `NYC Open Jobs ↓` → `NYC Employees ↓` | ~51 | ✅ 51 |
| 3 | **TOP PURSUITS** | `Status` is `Top Pursuit` | `Fit Score ↓` | small | 1 |
| 4 | **NEW INTAKE** | `Added On` within past month · **grouped by `Added From`** | `Added On ↓` | — | ⚠️ 93 = whole board |
| 5 | **BY SIZE** | **none** · grouped by `NYC Band`, sub-grouped by `Status` | `NYC Δ ↓` within group | 93 | ✅ 93, all in "No NYC Band" |
| 6 | **HIRING** | `Desk Jobs > 0` | `Desk Jobs ↓` → `Intensity ↓` | — | 🔴 **0 — structurally** |
| 7 | **NEEDS ME** | `Action Needed` starts with `Joe:` **AND** is not `Joe says: no careers page` | `Fit Score ↓` | **<15** | ✅ 2 |
| 8 | **HEALTH** | chart · bar · X=`Status`, Y=count | — | — | ✅ |
| 9 | **HEALTH · NYC BAND** | chart · bar · X=`NYC Band`, Y=count | — | — | ⚠️ one bar |

**Why BY SIZE has no filter — a deliberate change I made to the spec.** It was specified as
`NYC Employees is not empty`. **Removing the filter makes BY SIZE the complete board, grouped —
and the 52 unmeasured companies form their own empty-band group, which makes the measurement
backlog visible instead of hiding it.** An unmeasured company vanishing from a size view is
exactly the silent omission this system exists to eliminate.

**Why PROSPECTS breaks ties on open jobs before headcount.** At equal Fit, **hiring is the company
*acting*; headcount is the company *existing*.** Size leads, growth amplifies — so at a tie,
growth is the tiebreak.

**Why `Action Needed` is shown but not filtered on in PROSPECTS.** A company can be chaseable *and*
owe you a careers link. **Filtering it out would hide a live prospect behind an errand.**

## What was deliberately NOT built

- **No Board (kanban) view** — deal flow isn't built yet
- **No Timeline** — needs lease dates that don't exist
- **No "All Companies"** — that's the default table
- **No per-industry or per-HQ views** — those are filters you apply for thirty seconds
- **No staleness view** — `Next Check Due` and the cadence own that; it's a machine concern

> **Every additional view is a place for the board to disagree with itself.**

---

# 6 · Enrichment — four lanes, three instruments

| lane | instrument | cost | account risk | what it produces |
|---|---|---|---|---|
| **Careers** | public ATS APIs (Greenhouse, Lever, Ashby, Comeet) | **free, minutes** | **none** | NYC roles · in-office/hybrid/remote · posting dates · seniority · role type · sub-geography |
| **Sales Nav** | JD's LinkedIn, UI only | **2 attended days / 50 cos** | **highest** | NYC-metro headcount |
| **News** | retrieval + LLM-as-interpreter | low | none | the five expansion events, as **outreach angles** |
| **Contacts** | Apollo API | **~4 credits / 50 cos** | credits | names · titles · LinkedIn · person location |

## 6.1 · The careers lane's two-phase shape — the highest-leverage design in the system

| phase | cost | frequency |
|---|---|---|
| **BIND** — render homepage → find careers link → identify ATS → capture board token | expensive: a browser | **once per company** |
| **COUNT** — hit the cached endpoint | cheap: a JSON call | every cadence |

**The recurring cost and the fragility both live in the once-per-company step.** The daily budget
spends API calls, not browser sessions.

**Measured: 5 of 12 Ashby boards were embed-only**, which made the browser bind the **default
path, not a fallback**. A static scan finding nothing is **never** "no board" — that false zero is
what produced the Brandlight defect.

**A 404 on the cached endpoint re-enters BIND, not COUNT.** A broken handle is not a measured zero.

## 6.2 · The instrument problem, stated once

> **You cannot compare a number from one instrument against a number from another.**

When headcount measurement moved from LinkedIn's geo-chart to Sales Navigator, the existing
companies had to be **re-measured, not converted.**

**And the pinned ruler is wider than JD's real target:**

| | |
|---|---|
| **JD's NYC** | Manhattan + a little Brooklyn |
| **Sales Nav's NYC** | the **metro** — includes NJ, Westchester, Long Island |

> **Treat the metro count as an upper bound.** A company whose presence is heavily NJ/suburban is
> less interesting than its number suggests. Where granular location exists — **job posting
> locations especially** — skew Manhattan-centric.

## 6.3 · Apollo's measured limits, from its own vendor eval

- **Person geography is state-ish "New York"** — no metro vocabulary, excludes NJ/CT, includes
  upstate. Against Sales Nav ground truth: **60–88%. "Not a constant, not correctable."** Usable
  for *New York vs California vs Israel* — **never as a NYC measurement.**
- **1 of 6 domains misbound** in their own test. Hence **name-echo before attach.**
- **Person location is captured, never filtered on.** The CEO decides the lease from wherever they
  sit — **but a founder in Manhattan is a coffee and a founder in Tel Aviv is a 7am call.**

**And the hard line:** **Norman will never construct an email address.** Declared or nothing.

---

# 7 · Scoring — the verified weight table

**Read off a live company page, and it sums to exactly 100:**

| # | component | weight | what earns it |
|---|---|---|---|
| 1 | **Employees** | **34** | absolute NYC in-office headcount. Ladder keeps accruing past 50, **no plateau** |
| 2 | **Jobs** | **26** | open in-office NYC roles — **both the count and the jobs-to-headcount ratio**, plus freshness, seniority, and role-type bonuses |
| 3 | **Growth** | **10** | funding velocity / fresh raise |
| 4 | **Stage fit** | **8** | headcount vs what's expected at that funding stage |
| 5 | **Funding** | **8** | size, as context |
| 6 | **HQ** | **6** | NYC-HQ earns real points |
| 7 | **Industry** | **5** | coarse tier among qualified targets |
| 8 | **Investors** | **3** | context only |
| | | **100** | |

## The most important structural fact about this table

> **Employees + Jobs = 60 of 100. Everything else together is 40.**

**And the "growth is required for the top tier" rule is not a coded cap — it is arithmetic.**
Jobs (26) + Growth (10) = **36 points that only a growing company can earn.** A company with no
open roles and no fresh raise is structurally capped around **64**, no matter how big.

**That is why JD's rule reads the way it does** — *200 NYC people, no jobs, no fresh funding →
"only medium."* The model produces that answer without anyone writing a cap.

**It is also why finding #1 is the most serious item in this document.**

## The stage lens, worked

| situation | reads as |
|---|---|
| Seed with 25 NYC | **beats** Series B with 25 — exceeding-stage wins |
| Young + seed + $5M+ + hiring hard | **early-rocket** — small headcount not penalized |
| **NYC-HQ**, Series C, 8 people | **stall / red flag** |
| **SF-HQ**, Series C, 8 NYC, 5 in-office roles | **new NYC satellite — get in early.** Not a stall |
| Series D, 300 NYC, 20 in-office jobs | **top prospect** — late stage doesn't cap a grower |

**HQ is the disambiguator.** The same facts mean opposite things depending on it.

**Verified working.** Synthetic companies at constant 18 heads scored **64·64·59·55·54** across
stages (declining, correct); at each stage's own expectation, **45·50·59·66·71** (rising,
correct). Early-rocket fires. Stall fires. **Green.**

---
---

# PART II — THE 360° REVIEW

**17 findings, ranked by impact. Six are mine.**

---

## 🔴 1 · Growth cannot compute for CSV companies — and the formula silently renormalizes

**The chain, traced end to end:**

```
compute_velocity  needs dated funding rounds
    ← funding_rounds table
        ← written ONLY by add_funding_round
            ← which has NO CALLER in any commit
                ← and the Crunchbase CSV carries a round NAME and a COUNT, no dates
```

**The inputs cannot be supplied. Not "aren't yet" — cannot.**

**Here is the part that makes it severe.** When a component is missing, the scorer **renormalizes
over the remaining weights.** Drop growth and the other 90 points are rescaled to 100:

| component | weight WITH growth | weight WITHOUT growth |
|---|---|---|
| Employees | 34.0 | **37.8** |
| Jobs | 26.0 | **28.9** |
| Stage fit | 8.0 | **8.9** |
| Funding | 8.0 | **8.9** |

> **Every remaining component silently inflates by ~11%.**

**So a new CSV company is not scored slightly differently. It is scored by a different formula —
and then ranked against a board scored by the other one.** The board's ranking is the product;
interleaving two formulas corrupts the product itself.

**And the eval corpus cannot detect it**, because every frozen record carries velocity. **The
gate is structurally blind to this exact failure.**

**Fix:** E1 in loop 4. **This is a precondition for the next CSV, not an improvement to it.**

---

## 🔴 2 · CHANGED shows 74 rows against an expected 5–15 — and the fix is a filter I dropped

**This is the view JD is meant to check weekly. It is the one the Friday email links to.**

**My original five-view spec had the right filter:**

```
Changes is not empty  AND  change origin = company   (not system)
```

**The build spec I wrote later replaced it with:**

```
Changes is not empty  AND  Changes does not contain "First check"
```

> **`First check` is not the same predicate as `origin = system`.**

**A global rescore stamps `Fit ↑` / `Fit ↓` on dozens of companies at once. None of them is
`First check`, so all of them survive the filter and appear as "what companies did."**

**The consequence is precise:** 74 of 93 companies appear to have changed in a week. **The view
answers "what moved?" with "almost everything," which is the same as answering nothing.** My own
spec predicted this exact failure — *"a formula change that moves 43 scores is not 43 companies
changing"* — and then the build prompt dropped the guard.

**Fix:** add a change-origin field (`company` / `system`) to the change log and filter on it.
**The change log already records enough to derive it.**

---

## 🔴 3 · Nothing in the entire system runs on a schedule

**No cron. No CI. No scheduler. One Notion automation, disabled.**

**The check ledger computes what is due and nothing fires.** The careers lane is annotated in its
own source as cleared to run unattended, hits public APIs, carries zero ban risk — **and only runs
when JD types the command.**

> **If that one lane ran on a timer, every new company would self-enrich on the free axis and
> Sales Nav would be the only human-gated step in the whole pipeline.**
>
> **That is the difference between a batch being "a day of work" and "a day of waiting."**

**Open since day one.** Contacts closed, priority closed, **unattended operation never started.**

---

## 🔴 4 · The board's configuration exists in exactly one place, and it is not version control

**ADR 0001 says Notion is a rebuildable view. That is true of the ROWS and false of the VIEWS.**

**If the board were deleted today:** the 93 rows rebuild from SQLite. **The nine views, their
filters, their sorts, their groupings, the four buttons and the eight NYC Band options would have
to be rebuilt by hand from a spec in a different repo.**

**Worse: nothing detects drift.** If a filter is edited in the Notion UI tomorrow, no check
notices. The build report that recorded the as-built configuration lives at
`~/Downloads/build-report.json` on Codex's machine — **untracked, unbacked-up, and already the
only record.**

**Fix, cheap:** a read-only API pass that dumps views/filters/sorts/properties to JSON, committed
on every change. **The capture that produced half of this document is exactly that mechanism, run
once, by hand.**

---

## 🔴 5 · Three of the four reachability properties were designed and never created — mine

**`reference/notion-one-board-design.md` specifies four:**

| property | designed | built |
|---|---|---|
| **Reach** | ✅ | ✅ (as `Reach`, spec'd as `Reachable`) |
| **Best Contact** | ✅ | ❌ |
| **Best Contact Title** | ✅ | ❌ |
| **Contacts** (count) | ✅ | ❌ |

**I wrote the design, then wrote a build prompt that omitted three of its four properties.**

**The user-visible harm is exact.** PROSPECTS shows `Reach`. So once the projection runs, JD will
see that a company is reachable — **and no way to see by whom.** The roster isn't in the page body
either. **173 people exist in SQLite and there is currently no path by which any of them appears
in Notion.**

**Fix:** create the three properties and write the roster into the page body — Band C of loop 4,
plus three properties that band does not currently mention.

---

## 🔴 6 · Every view sorts on the rounded score, while the system's rule says rank on raw — mine

**`FitResult.raw` is documented in code as *"unrounded — RANKING uses this."*** My five-view spec
sorted on `Fit Raw ↓`. **The build spec I wrote sorts every view on `Fit Score ↓` — the rounded
integer.**

**Consequence:** 93 companies compressed onto ~50 integers means **heavy ties**, broken
arbitrarily by Notion. PROSPECTS has secondary sorts and partly survives; **TOP PURSUITS sorts on
`Fit Score` alone.**

**And `Fit Raw` is a real property on the board (#48) — so the correct sort key is already
there.** It was specified as hidden-but-present precisely so it could be the sort key.

**Fix:** change the sort key on every ranked view to `Fit Raw ↓`. **Presentation-only — Codex, not
Norman. No data changes.**

---

## 🔴 7 · Routing uses the rounded score, so the real Prospect line is 49.5

**Verified in code:** `route_status` binds the **integer**; every band comparison uses it.

> **Brandlight is a live Prospect only because 49.84 rounds up.**

**Not a bug — a mechanism nobody ever decided**, currently deciding a real company's band.

**Ruled preferred: route on `raw`.** **Gated** — switching drops Brandlight out of Prospect, so it
needs an oracle re-run and JD's review, and the threshold was anchored on a distribution measured
*under rounding*, so re-anchoring must use the rule it freezes.

---

## 🔴 8 · `fresh_raise_growth_pts = 14` inside a component weighted 10

**Found by the property module, running against the live config:**

```
FAIL  P4 floor<=ceiling   fresh_raise_growth_pts=14 exceeds the 'growth' weight of 10
FAIL  P2 discriminates    growth: its input changed and its contribution did not
```

**The first means every company at or above that floor scores identically on growth — the signal
beneath it is erased.** A relationship between two constants that nobody owned.

**The second is stranger and worth stating precisely:** growth **does** emit a number (Remark
shows `Growth 2/10 (Slow est.)`) — **and that number does not respond to changes in its own named
input.** Velocity moved from Fast to Slow and the contribution did not move.

---

## 🔴 9 · One select field is being filtered on five different questions

```
where in the funnel  Research · Prospect · Top Pursuit · Engaged · Active TIM · Client
why it's out         Not a Fit · Low NYC Presence · Do Not Pursue
how cold             Tracking · Watchlist
what's blocking      Needs Review · Needs Angle
a timing event       Recently Signed Lease
```

**The forced choice is real and it has a cost:** a Prospect that needs review must pick one, **and
the operational state overwrites the funnel position — silently removing it from the chase list.**

> **The views feel hard to design because one field is answering five questions.**

**Ruled fix:** **Stage** (an ordered state machine, nothing else in it) · **Disposition** (blank
for everything in play, so a disqualification never destroys the funnel position it had) ·
**Action Needed** (exists) · **attention tier** (derived from stage + fit, never typed).

**Watchlist was never a stage — it was a cadence.**

**And `Recently Signed Lease` is an event with an expiry, not a state.** Per JD's own correction —
*companies outgrow their space quickly* — **the clock is growth, not time**, and **nothing
currently brings a signed company back.**

---

## 🔴 10 · HIRING returns zero rows, and cannot return any

`Desk Jobs > 0`, and **`Desk Jobs` is written by nothing.**

**This is the distinction the whole system is built on, appearing on the board itself:** an empty
queue means *the work is done*; **a structurally empty view means the plumbing was never
connected** — and they look identical.

---

## 🔴 11 · The `Not now` button writes a machine-owned property

**`Not now` sets `Status → Tracking` (fine, human-wins) and `Next Check Due → +90 days`.**

**`Next Check Due` is machine-owned.** The next reconcile sweep heals it back to the ledger's
computed value — **silently, with no error anywhere.** JD would push a company out 90 days, watch
it come back, and have no way to know why.

**This is the exact defect the presentation boundary exists to prevent**, and it made it into a
build spec anyway.

**Fix:** either drop the `Next Check Due` write, or add a human-owned `Snooze Until` that the
ledger *reads* and respects.

---

## 🔴 12 · `Called today` writes a field with no store column

**`Last Touched` exists in Notion and has no counterpart in SQLite.** Reconcile cannot adopt what
has no field to adopt into. **The value survives until the next board rebuild and then is gone.**

**Fix is Band C3 of loop 4:** company-level `last_touched_on` — entity field, store column,
reconcile field map, blank-is-an-adoption list. **All four, or it is not adopted.**

---

## 🔴 13 · Four columns computable today, written by nothing

`NYC Δ` · `Desk Jobs` · `NYC Band` · `Reach` — **all four derive from data already in the store.**
Three views depend on them.

**One expectation to set now:** `NYC Δ` will populate on **~4 of 134 rows** even once written,
because `prev_nyc_employees` is non-null on only four companies. **That is not a failure — the
delta needs two readings and almost nothing has been measured twice.** `Desk Jobs` should land on
~48.

---

## 🔴 14 · Thirteen fields empty on every row — four of them are board columns

**The sharpest pair: `nyc_jobs_senior` and `nyc_jobs_facilities`.** The desk-role classifier
computes role types **and nothing stores them.** *"Head of Workplace as a buy signal"* was the
entire point of that work.

**And `down_round` / `layoffs_hit_nyc` are scoring inputs empty everywhere** — inert components
sitting inside a live formula.

**The four `Months:` columns are downstream of `funding_rounds`, which nothing feeds** — near-forced
RETIRE from the board (the store keeps them).

> **A column empty on every row is a promise the system is not keeping.**

---

## ⚠️ 15 · Two views return the whole board, against the build's own rule

**Rule 5 of the build spec, which I wrote:** *"No view may return the whole board. If one does,
the filter is wrong — do not widen it, report it."*

| view | rows | verdict |
|---|---|---|
| **NEW INTAKE** | 93 = all | **correct today** — the whole board *was* added in the past month. Self-corrects in September |
| **BY SIZE** | 93 = all | **correct by design** — I removed its filter deliberately so the unmeasured 52 stay visible |

**The finding is not that either view is wrong. It is that rule 5 can no longer be a mechanical
check**, because two legitimate views violate it. **A tripwire that fires on correct behavior gets
disabled, and then it is not there when something is actually wrong.**

**Fix:** restate rule 5 as *"a view returning the whole board must declare why."*

---

## ⚠️ 16 · The system has stock views and no flow view

> **Every view shows what IS. None shows what MOVED between stages.**

**A funnel's health is flow, not stock.** Entries and exits per stage per week: inflow drying up,
a stage nothing ever leaves, disqualifications spiking on one reason.

**The change log already holds everything this is computed from.** And **it cannot be a Notion
view** — a view filters rows; this counts transitions over time. **Norman writes it weekly into a
page.**

---

## ⚠️ 17 · Two multi-selects have 311 and 161 options

**`Key Investors`: 311. `Lead Investors`: 161.** Every investor on every company became an option.

**Not urgent — but two consequences worth knowing:** the filter dropdown is unusable as a picker,
and **investor is a 3-point context component**, so the storage cost is buying very little ranking
value. **If investor tier ever becomes a real signal, it needs a tier mapping, not 311 flat
options.**

---

# THE RANKED FIX LIST

| # | fix | who | effort | unblocks |
|---|---|---|---|---|
| 1 | **Growth redesign + renormalization** | CRMx | days, **gated on JD** | **the next CSV** |
| 2 | **Change-origin field → fix CHANGED** | CRMx | hours | the weekly review, the Friday email |
| 3 | **Project the four columns + the contact roster** | CRMx | hours | 3 views, 173 people |
| 4 | **Schedule the careers lane** | CRMx | hours | **every future batch** |
| 5 | **Create Best Contact / Title / Contacts** | Codex | minutes | the chase decision |
| 6 | **Sort every ranked view on `Fit Raw`** | Codex | minutes | correct ranking |
| 7 | **Fix the `Not now` button** | Codex | minutes | silent heal-away |
| 8 | **`last_touched_on` in the store** | CRMx | hours | the `Called today` button |
| 9 | **Commit a board-config capture** | either | ~1 hour | drift detection, rebuildability |
| 10 | **Decide the rounding question** | CRMx, **gated** | hours | the 49.5 line |
| 11 | **Split Status into Stage + Disposition** | CRMx | days | the whole view layer |
| 12 | **The flow page** | CRMx | days | funnel health |

**Items 5, 6 and 7 are presentation-only, take minutes, and need no Norman changes.** They are the
cheapest real improvements available today.

---

# THE ONE-PARAGRAPH VERDICT

**The architecture is sound and has not needed reversing in five days** — SQLite as truth, Notion
as a rebuildable view, one level-triggered loop between them. **The scoring model is genuinely
good**: 60 of 100 points on the two things JD actually ranks on, a stage lens that has been
exercised and works, and edge-case rules that read like him.

**Every serious finding in this document is a connection, not a component.** Growth's producer has
no caller. The change log has no origin field. The classifier's output has no column. 173 contacts
have no property to land in. The board config has no backup. **Nothing has a scheduler.**

> **The parts are built. The wiring is where the defects live — and a unit test cannot see a
> wire.**
