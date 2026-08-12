# How Norman works — the complete process

**What this is:** the whole system, end to end — where data comes in, what enriches it, how a
score is computed, how a company gets a status, how Notion stays true to the database, what
protects JD's accounts, and what runs by itself.

**Where it comes from:** the ruling log (65 rounds), `FIT-SCORING-SPEC.md`, the verified command
signatures in `reference/batch-runbook.md`, and the property module in `reference/properties.py`
that was built and run against the live config.

**What it is not:** a read of the CRMx source. This document was written from the brain repo.
**Every claim marked ✅ traces to a round where a number was checked** — anything I could not
trace is marked accordingly, because a process document that describes design as if it were
running is the exact defect this project has spent five days eliminating.

| mark | means |
|---|---|
| **✅ RUNS** | verified in operation, with the round and the number that proved it |
| **🔨 BUILT** | committed and tested, **not** proven to be called in a real run |
| **🔴 BROKEN** | verified defective or verified inert |
| **📐 RULED** | decided, not confirmed built |

---

# 0 · The one-screen version

```
CSV → ingest → enrich → score → route → project → contacts → chase list
```

**Eight stages. Seven are minutes of compute. One is two days of JD's attention.**

> **Nothing in this pipeline starts by itself.** There is no scheduler, no cron, no CI. Every
> stage is a command a human types. **That is the single largest gap in the system** and it is
> §10.

**The architecture, which has not been reversed in five days of building:**

> **SQLite is the truth. Notion is a rebuildable view. One reconcile loop keeps them
> converged.** *(ADR 0001)*

That sentence does more work than any other in the system. It means the board can be deleted and
rebuilt from the store, a bad write is recoverable, and **no decision is ever made by Notion.**

---

# 1 · Follow one company all the way through

**A real trace, so the rest of the document has something to hang on.** Company #94 arrives on a
Crunchbase CSV export of NYC Series-A companies.

**1 · Ingest.** The row carries name, domain, HQ city, funding stage, latest round, total raised,
investors, global employee count. **It does not carry NYC headcount, jobs, or a careers page** —
the three things Norman actually scores on. It lands with `added_from = "crunchbase-csv:series-a-2026-08"`
and status `Research`. **It is not scored yet, and that is deliberate** (§4).

**2 · Industry gate.** Its sector is checked against the 20-industry target list. **Off-list is
not a low score — it is an exit.** Biotech is excluded entirely by JD's ruling; the code was
right and the list was wrong until he corrected it.

**3 · Careers lane.** A browser renders the homepage, finds the careers link, identifies the ATS
(Greenhouse / Lever / Ashby / Comeet), and extracts the board token. **That is the expensive
step and it happens once.** From then on Norman hits the ATS's public JSON API to count jobs —
free, no login, no ban risk. It gets: how many NYC roles are open, whether each is in-office /
hybrid / remote, when each was posted, and what seniority it is.

**4 · Sales Nav headcount.** **This is where the pipeline stops and waits for JD.** There is no
command. He opens Sales Navigator on his own login, at human pace, with his approval for that
session, and reads the NYC-metro headcount. ~2 profile views per company, capped at 80/day.

**5 · The barrier.** The moment all three lanes have a **terminal** result for this one company
— including "blocked" or "no careers page," which are terminal — the company is scored. Not
before. **A company never gets a status on partial evidence**, which is why JD never sees
`Prospect` become `Low NYC Presence` three minutes later.

**6 · Score and route.** Nine components produce a 0–100 Fit. The score maps to a band, the band
maps to a status. `Prospect` at 50+.

**7 · Project.** `reconcile_sweep` writes the company to Notion — but **reads JD's edits first**
and adopts them before writing anything of its own.

**8 · Contacts.** Apollo is queried by domain for people matching the target-title list. Names,
titles, LinkedIn URLs, and where the *person* lives. **No email is ever constructed.**

**9 · Chase list.** The company appears ranked, with a named human next to it.

---

# 2 · Intake — how companies get in

**✅ RUNS.** `ingest_csv <csv> <db> --added-from <source>`

| what | detail |
|---|---|
| **source today** | Crunchbase CSV export. One source tag per batch, e.g. `crunchbase-csv:series-a-2026-08` |
| **identity** | domain is the key. Name matching is fuzzy (rapidfuzz/splink) and **never auto-binds on name alone** |
| **auto-bind bar** | domain match, **or** two independent non-name signals. Below the bar → flagged, not bound *(Q4)* |
| **status on arrival** | `Research` — in the system, not yet judged |
| **dedup** | primary-key dedup on ingest. This was a real bug: every contact was stored twice until round 42 |

**The identity rule exists because of a real failure.** A voice entry of "Cluely" applied 4
headcount to "Clarity" — near-identical to the ear, different domains. **The fix: every manual
entry routes through the same resolver every machine write uses, and echoes back the canonical
identity *with its domain* before writing.** "Applying heads=4 to Cluely, cluely.com, Prospect —
confirm?" *(K5)*

**Ambiguous match forces a pick. No match confirms "new entity" before creating one.**

---

# 3 · Enrichment — four lanes, three instruments, one bottleneck

## 3.1 · The careers lane ✅ RUNS

**The most valuable lane in the system: it is free, it carries the growth signal, and it has
zero account risk.**

**Two phases, and the split is the whole design:**

| phase | cost | frequency | what it does |
|---|---|---|---|
| **BIND** | expensive — a rendered browser | **once per company** | render homepage → find careers link → identify ATS → capture board token. Stored with `bound_at` + `bound_via` |
| **COUNT** | cheap — a JSON API call | every cadence | hit the cached endpoint. No browser, no login, no fragility |

**Why it must be a browser to bind:** the careers link and ATS embed live in JS-rendered DOM on
~70% of homepages. **A static scan finding nothing is never "no board"** — that false zero is
what produced the Brandlight defect. Measured: 5 of 12 Ashby boards were embed-only, which made
the browser bind the **default path, not a fallback** *(M5)*.

**What the lane extracts per NYC role:**

- **Location type — in-office / hybrid / remote.** Load-bearing. **A remote worker needs no
  desk**, so remote roles barely count toward the score.
- **Posting date.** 10 roles posted this week ≫ 10 that have sat open five months — stale
  postings may be filled or abandoned.
- **Seniority.** VP / Director / Head-of beats associate / coordinator: **senior hires mean a
  permanent flag being planted**, not a temporary team.
- **Role type.** "Head of Workplace," "Office Manager," "Facilities" — a direct tell that
  someone is standing up or expanding an office.
- **Sub-geography.** "New York, NY" vs "Jersey City" — see §3.2's ruler problem.

**A 404 on the cached endpoint re-enters BIND, not COUNT.** A broken handle is not a measured
zero. This distinction — *structure absent vs structure present but empty* — recurs in every
lane in the system.

**Negative findings are durable.** When JD says "no careers page," the company moves to
`careers_status = no-page-per-jd` with his provenance and a date, the board stops asking, and
re-discovery is scheduled **+1 month, not immediately.** This was a bug: the ack fired as an
event but no state persisted, so the ask kept coming back *(M6)*.

## 3.2 · Sales Navigator headcount — the bottleneck ✅ RUNS, attended

**No command exists. By design.**

| | |
|---|---|
| **how** | JD's own login, the UI only, human pace, computer-use |
| **gate** | **his approval for each session, individually** *(AZ3)* |
| **cap** | 80 profile views/day; measured at **~2 views per company** (round 28 spent 82 views on 41 companies) |
| **throughput** | **~2 attended days per 50 companies** |
| **prohibited** | no API, no internal endpoints, no XHR interception, no unattended running |
| **on challenge** | **halt immediately. No retry, no refresh, no workaround.** Retrying into a challenge is how accounts get locked |

**This is the pinned ruler** *(K3)* — the one instrument all headcount is measured on, because
**you cannot compare a number from one instrument against a number from another.** When the
measurement moved from geo-chart to Sales Nav, the existing companies had to be **re-measured**,
not converted.

### The ruler is wider than JD's actual target, and that is a scored consequence

**JD's NYC = Manhattan plus a little Brooklyn. Sales Nav measures NYC-*metro*** — which includes
New Jersey, Westchester, and Long Island.

> **The metro count over-represents his real interest. Treat it as an upper bound.**

So a company whose metro presence is heavily NJ/suburban is **less interesting than its number
suggests** versus a Manhattan-concentrated one. Where granular location exists — job posting
locations especially — **skew Manhattan-centric and discount outer-metro** *(§3b)*.

## 3.3 · The news lane 🔨 BUILT

**Citation-by-construction: the LLM interprets, it never sources** *(F4)*. A claim that cannot
point at a retrieved document does not exist. Watches for the five expansion events JD acts on:
**new funding · leadership change · acquisition · big customer win · announced headcount
increase.** These become **outreach angles**, not score inputs.

## 3.4 · Contacts — Apollo ✅ RUNS

**Cost: ~4 credits per 50 companies. Measured, not estimated.**

```bash
contacts_lane <db> --print-query          # emit the query for review
contacts_lane <db> --apply <response.json> # ingest the response
```

**Queried by company domain**, filtered to the target-title list. Four rulings shape it:

**Title matching is strict, with an explicit shared normalizer.** I originally ruled Apollo's
`include_similar_titles` should be **true** for recall — while calling its expansion "opaque" in
the same paragraph. CRMx set it **false** and wrote an explicit `normalize_title` shared with the
rest of the system instead. **Their reasoning, which is now a standing rule:**

> **Identifying a drawback and then selecting for a different axis is where most bad choices
> live.**

**Person location is captured, never filtered on** *(AP4)*. The CEO decides the NYC lease from
wherever they sit — filtering would silently drop real decision-makers. But **it changes the
action**: a founder in Manhattan is a coffee, a founder in Tel Aviv is a 7am call. It is recorded
as `apollo/person-state` — accurate enough for *New York vs California vs Israel*, and **never
usable as a NYC measurement**, because Apollo's own vendor eval measured it against Sales Nav
ground truth at **60–88%: "not a constant, not correctable."**

**Name-echo before attach.** Apollo's own eval measured **1 of 6 domains misbound** — a
"Something Labs" that was a different company sharing a domain in their index.

**And the hard line:**

> **Norman will never construct an email address.** No `first.last@domain`, no inference, no
> defaulting. **Declared or nothing.**

**The reason is a class distinction worth understanding.** Everything else in Norman assumes
errors are correctable on the next measurement pass — that is what hysteresis, reconcile, drift
correction, and every rescore rest on. **An email address is the first value that escapes that
assumption. Once sent it has left the system and no loop can un-send it.**

> *"A wrong score gets fixed on the next pass. A wrong address gets sent to a stranger."*

**And the gap named at the same time:** every safety mechanism built so far protects JD's
**accounts** — throttles, breakers, write guards. **Nothing yet protects his reputation.**
Contacts are the last read-only step; outreach would be the first write to the outside world, and
that machinery does not exist.

---

# 4 · The barrier — when a company is allowed to be scored

**This is a small design decision that prevents a large trust failure.**

> **Evidence values are written to the board as they land. Score, route and status are computed
> only at the per-company barrier** — when all lanes have a **terminal** result for that company.
> *(R3)*

**Two refinements that make it work:**

1. **The barrier is per-company, not per-batch.** A company scores the moment *its* slowest lane
   lands. The batch does not wait for the slowest company.
2. **"Terminal" includes Unknown, blocked, and no-page.** Otherwise the barrier hangs forever on
   a company that genuinely has no careers page.

**Why it matters:** JD watches data populate live. Without the barrier he would see a company
routed `Prospect` on headcount alone, then demoted to `Low NYC Presence` three minutes later when
the jobs came back zero. **Status flapping on transient partial evidence is exactly the trust
erosion the whole system is built to prevent.**

---

# 5 · Scoring — the Fit model in full

**The thesis, one line:**

> **Norman rewards companies that will need NYC office space soon — measured first by how many
> in-office NYC people they have, then by how fast they're growing that presence, all read
> relative to their funding stage.**

**Nine components, weights in `config/fit-score.json`:**
`employees` · `jobs` · `growth` · `industry` · `funding` · `investors` · `stage_fit` · `hq`
(+ role/seniority bonuses inside jobs).

## 5.1 · The primary drivers

**NYC in-office headcount leads.** Absolute size is the main driver — **bigger wins.** JD ranked
40-NYC Series B > 15-NYC Series A > 6-NYC seed *even though the smaller ones had higher growth
ratios.* Points keep accruing past ~50 with **no hard plateau**. **Only in-office and hybrid
count fully.**

**A growth signal is REQUIRED to reach the top tier.** This is a hard gate, not a bonus:

> **No growth signal caps at "medium," no matter how big.** 200 NYC people with no jobs and no
> fresh funding → *"only medium."* 100 NYC + a PE round + 0 jobs → *"medium."*

**A growth signal is one of two things:**

- **Active in-office NYC hiring** — scored on **both** the absolute count **and** the
  jobs-to-headcount ratio. *10 jobs on 15 people is a rocket; 10 on 300 is routine.* Strongest
  when both are high. At equal size, hiring intensity makes a **big** gap: 30-NYC with 15 jobs ≫
  30-NYC with 3 jobs.
- **OR a fresh substantial raise** — a large recent round is itself a leading signal. JD would
  pursue a just-raised-$40M NYC company with 20 people **now, before any jobs appear.** *Contrast:
  an old late-stage or PE round with no jobs is not growth — it reads as settled.*

## 5.2 · The stage lens — everything is read against funding stage

**Expected headcount scales with stage. The question is whether a company is exceeding or failing
its own stage.**

| situation | reads as |
|---|---|
| **Seed with 25 NYC people** | **beats** a Series B with 25 — exceeding-stage wins |
| **Young + seed + funded $5M+ + hiring hard** | **early-rocket redemption** — small headcount is *not* penalized |
| **NYC-HQ, Series C, 8 people** | **stall / red flag** — they should be much bigger by now |
| **SF-HQ, Series C, 8 NYC, 5 in-office roles** | **a brand-new NYC satellite being built — get in early.** Not a stall at all |
| **Series D, 300 NYC, 20 in-office jobs** | **top prospect.** Late stage does not cap a grower |

**The stall penalty is HQ-conditional and JD will not read it without HQ.** Small-and-mature means
opposite things depending on where the company is headquartered. **HQ is the disambiguator.**

**Verified working.** I exercised the stage lens against synthetic Seed/A/B/C/late companies:
at a constant 18 heads the scores ran **64·64·59·55·54** (declining with stage, correct); at each
stage's own expectation, **45·50·59·66·71** (rising, correct). Early-rocket fires. Stall fires.
**Green.**

## 5.3 · HQ and the NYC-native question

**NYC-HQ earns real points, not a tiebreak** — at identical NYC hiring JD calls the NYC-HQ company
"clearly better." **But modest enough that a large momentum gap overcomes it**: he took an SF-HQ
company growing 10-NYC-plus-50-Austin over a smaller NYC-centered one.

**What is penalized is thin/token presence** — 6 NYC people with **0** jobs is *"low, but keep
it."* **Scored low, kept on the board, not shelved.**

## 5.4 · Secondary — down-weighted deliberately

**Funding size, sector, and investor tier are context, not rankers.** JD refused to rank two
companies on funding without first knowing "NYC headcount, HQ, and roles."

**Industry is a qualification taxonomy, not a fine tilt.** In-list = target; **off-list = exit**.
Core beats expansion as a coarse tier. Among qualified targets, industry does **not** re-rank —
concrete NYC demand does.

## 5.5 · The edge cases, where the model earns its keep

| case | ruling |
|---|---|
| **Shrinking headcount** (30→25, 0 jobs) | **near-deal-breaker.** A contracting company sheds space |
| **Very high jobs-to-headcount** (8 people, 20 roles) | **loved, not doubted.** "Exactly what I want." Skepticism about whether it's *real* lives in the data-quality layer — **never in the scoring** |
| **Big fresh raise, 5 NYC, 0 jobs** | **prospect now.** That cash means imminent hiring |
| **Grew 10→20 over the year, 0 open jobs today** | **"watch — need current hiring."** History supports; **live hiring earns the top tier** |
| **No funding record at all** | **does not penalize.** 25 NYC + 8 in-office jobs → *"heads and jobs carry it"* |
| **Bootstrapped, <$2M, 40 people, 12 roles** | **strong prospect.** The funding floor applies only to early companies where traction isn't visible — **the hiring proves it** |
| **Down round** | **yellow flag.** Valuation *level* is context; valuation *direction* is a signal |
| **Layoffs** | **read relative to NYC.** Cuts elsewhere *while hiring in-office NYC* = consolidating toward NYC = **positive**. Cuts that hit NYC = avoid |
| **Everything maxed at once** | **chase-today urgency tier** — surfaced above normal top Prospects |

## 5.6 · Two axes, kept separate

> **Fit is the company's signals. Urgency is whether a warm path is available now.**

A warm intro is what makes JD act *today*; it says nothing about whether the company is a good
target. **Conflating them would let a mediocre company with a friendly contact outrank a great
one with none.**

## 5.7 · The scoring change process — non-negotiable

```
principled change (never tune numbers to pass the pairs)
  → re-run the oracle against JD's 23 blind labels
  → confirm tier-match holds 7/7 and pairwise concordance holds or improves
  → confirm no previously-correct pair broke
  → review the delta with JD, by name
  → only then freeze the baseline
```

**100% concordance is not the goal. Eliminating the systematic lean is.**

**And the review gate has teeth.** When a global rescore moved 43 companies, the ruling was
*approve — but show JD the one status change first, by name.* **That condition is what surfaced
the next defect.**

---

# 6 · Routing — score becomes status

**Bands map score to status.** `Prospect` at 50+.

## 🔴 The rounding defect — a real company's band is decided by an artifact

**Verified in code:** `route_status` binds `score = result.score` — the **integer** — and every
band comparison uses it. Meanwhile `FitResult.raw` is documented *"unrounded — RANKING uses
this."*

> **So ranking uses the raw score and routing uses the rounded one. The effective Prospect line
> is 49.5, not 50.**

**Brandlight is a live Prospect only because 49.84 rounds up.**

**This is not a bug — it is a mechanism nobody ever decided**, and it is currently deciding a
real company's band. 📐 **Ruled preferred: route on `raw`**, so a configured 50 means 50 and the
integer is purely display. **Gated** — switching drops Brandlight out of Prospect, so it needs an
oracle re-run and JD's review. It also interacts with the frozen baseline, since the threshold was
anchored on the labeled distribution *under rounding*.

## The status vocabulary is overloaded — 14 values, 5 questions, one field

| axis | values |
|---|---|
| **where in the funnel** | Research · Prospect · Top Pursuit · Engaged · Active TIM · Client |
| **why it's out** | Not a Fit · Low NYC Presence · Do Not Pursue |
| **how cold** | Tracking · Watchlist |
| **what's blocking** | Needs Review · Needs Angle |
| **a timing event** | Recently Signed Lease |

> **A Prospect that needs review must pick one — and the operational state overwrites the funnel
> position, silently removing it from the chase list.**

📐 **Ruled fix (not confirmed built):** split into **Stage** (an ordered state machine, nothing
else in it) · **Disposition** (blank for everything in play, so a disqualification never destroys
the funnel position it had) · **Action Needed** · **attention tier** (derived, never typed).

**Watchlist was never a stage — it was a cadence.** Attention is a budget; cadence should be a
function of tier and freshness.

**And `Recently Signed Lease` is an event with an expiry, not a state.** JD's own correction —
*"companies outgrow their space quickly"* — means the clock is **growth, not time**. A 2026
signing on a 5-year term is a prospect again well before 2031, and **nothing currently brings it
back.**

## Exits are tombstones, not deletions

**"Do Not Pursue" and "Drop" are both tombstones, distinguished by reason type** — a qualified
business rejection of a real candidate versus a data-quality removal. **Nothing is ever deleted**,
because a deleted company silently reappears on the next CSV.

## Hysteresis — the exit and re-entry thresholds differ on purpose

**Exit to `Low NYC` at heads ≤ 4; return to `Tracking` at heads ≥ 7.** The gap prevents a company
oscillating across a boundary on measurement noise. **Routing to Do Not Pursue requires more than
a single confirming check** — a terminal state deserves more evidence than a reversible one.

---

# 7 · Projection and reconcile — how Notion stays true

**✅ RUNS.** `reconcile_sweep <db> --apply`

**The loop is level-triggered, not event-driven** — it looks at current state and drives toward
the desired state, rather than reacting to a stream of changes. **It is safe to run repeatedly and
safe to interrupt.**

## Reconcile's three laws, verbatim from the code

> **1 · Adopt before heal.**
> **2 · Heal machine columns only — human fields are read to adopt them.**
> **3 · Every action is logged.**

**Law 1 is the one that makes the board trustworthy.** Before Norman writes anything, it reads
what JD changed and takes those changes into the store. **His edits are never overwritten by a
later machine measurement** — a disagreeing measurement surfaces as a delta for him to see, not a
silent revert.

**Provenance ranking:** `jd-manual > machine-verified > machine-partial`

## A JD correction does two jobs, not one

1. **It is adopted**, with his provenance, and outranks the machine for that field permanently.
2. **It is treated as a drift signal on the instrument.** JD supplying a value the machine got
   wrong is *evidence the instrument underperformed* — logged so that a **pattern** of the same
   miss becomes countable rather than anecdotal.

**That is how "the geo-chart is unreliable" got learned from data instead of noticed by luck** —
two companies both failing the same way became a measurement, and the measurement retired the
instrument.

**On a dispute, Norman also forces a recheck of that field on the best instrument** and records
whether JD and the machine agreed. **That agreement rate is the instrument-calibration metric.**

## During a concurrent batch

**A sweep at the start, plus a field-level adopt-check immediately before each individual board
write** *(R8)*. A batch that takes 40 minutes cannot rely on a snapshot taken at minute zero.

## The presentation boundary — absolute

> **Norman writes DATA. Codex configures PRESENTATION. Notion may display anything and decide
> nothing.**

Formulas and rollups are fine — they recompute on render and cannot drift. **Any automation that
writes a machine-owned property creates a second source of truth the reconcile loop cannot see,
and reconcile would heal it away silently.** This is not hypothetical: a proposed "Not now" button
would have written a machine-owned `Next Check Due`, and the value would have vanished on the next
sweep with no error anywhere.

**The board today:** 93 rows · 61 properties · 9 views · 4 buttons · one automation, disabled.
**Integrity proof: 4,650 SHA-256 hashes, identical before the build, after property creation, and
after view creation — no row value was touched.**

---

# 8 · The chase list

**✅ RUNS.** `chase <db> --limit 20`

**This is the layer that turns a board into a decision**, and for twelve rounds it did not exist —
`contexts/priority` was absent from the repo entirely while 51 of 95 companies sat as Prospects
with no ranked surface. **That was a weight-class mismatch:** maximum rigor was going into a
scoring component worth 6 of 100 points while the layer that makes the board usable had never been
started.

**It ranks by Fit, surfaces the urgency tier above it, and attaches a named human.** A bug found
by *looking at its output* rather than by a test: **every contact appeared twice.**

---

# 9 · Safety — what protects what

## The breaker taxonomy — four failures that look alike and must be handled oppositely

| signal | what it means | response |
|---|---|---|
| **`/checkpoint/`, `/challenge/`, authwall, `401`** | **LinkedIn identity challenge** | **HALT-AND-ALERT. Stop the lane, do not retry, page JD.** Retrying into a challenge is how accounts get locked |
| **`cf-ray` / `cf-mitigated`, `403`/`503` + challenge body** | Cloudflare interstitial — infrastructure, not identity | **Halt and back off** with jitter. No page — but no hammering |
| **`200` + logged-in shell + expected structure MISSING** | Selector break — you're in, the page moved | **Self-heal re-bind.** Do **not** back off — the site is fine |
| **`200` + logged-in shell + structure PRESENT + implausibly empty** | Soft-block: they're serving a hollow page | **Back off. DO NOT WRITE. DO NOT RE-BIND.** ← **the dangerous one** |

**Row four is why this table exists.** A company that had 40 people showing 0 is not a
measurement. **Writing it would corrupt the store with a plausible-looking number**, and re-binding
would treat a defence as a layout change.

## Account protection

- **A dedicated managed browser profile — never JD's daily driver.**
- **Per-session human approval for Sales Nav**, reinstated after being wrongly removed in round 45.
- **Interleave-by-company execution order**, which paces the risky lane for free.
- **The real danger is not daily volume — it is inhuman regularity.** A budget waiver only holds
  if monitoring replaces the quota.

## Write protection

- **Everything defaults to dry-run. `--apply` writes.** And the rule that makes it meaningful:
  **the dry run must be the apply path**, or it is testing a different program.
- **Tombstones, never deletions.**
- **Append-only change log** — "why did this change?" is always answerable, and reconcile never
  acts invisibly.

## 🔴 One safety gap, named

**Every mechanism above protects JD's accounts. Nothing protects his reputation.** See §3.4.

---

# 10 · Automation — the honest answer

> **Nothing runs by itself. There is no scheduler, no cron, no CI, and no `.github/workflows/`.**

**The check ledger computes what is due. Nothing fires when it comes due.**

**And the lane that should be automatic is annotated in its own source as ready:**

```python
# src/norman/contexts/careers/fetch.py
# "...which is why it is the first lane cleared to run unattended."
```

**It hits public job-board APIs. No login, no ban risk, explicitly cleared — and nothing starts
it.**

> **If that one lane ran on a timer, every new company would self-enrich on the free axis, and the
> only human-gated step in the entire pipeline would be Sales Nav.**
>
> **That is the difference between a batch being "a day of work" and "a day of waiting."**

**This has been true and unaddressed since day one.** It is the last of three findings from the
operational review still open — contacts closed, priority closed, **unattended operation never
started.**

## What a batch actually costs today

| work | cost |
|---|---|
| ingest · score · route · project · chase list | **minutes** |
| careers lane | **minutes, free, zero account risk** |
| contacts | **~4 Apollo credits per 50 companies** |
| **Sales Nav headcount** | **~2 attended days per 50 companies** |

**Everything except Sales Nav is minutes.**

---

# 11 · What is broken right now

**Ordered by what it costs.**

### 🔴 1 · Growth cannot compute for any CSV company

**Traced completely.** `compute_velocity` needs dated funding rounds → `funding_rounds` is written
only by `add_funding_round` → **that method has no caller in any commit** → and the Crunchbase CSV
carries `latest_funding_round` (a string) and `funding_round_count` (an int), **no dates.**

> **The inputs cannot be supplied. Not "aren't yet" — cannot.**

**Why it outranks everything:** growth is a **required gate to the top tier** (§5.1). Without it,
every company on the new batch arrives with growth **excluded** and is scored on a **renormalized
formula relative to the board it joins.**

> **That is not a wrong score. It is a different formula — and the board's ranking is the
> product.**

**And the eval corpus cannot notice**, because the frozen records all carry velocity. The gate is
structurally blind to this.

### 🔴 2 · Two property violations in the live scoring config

Built and run against the real config:

```
FAIL  P2 discriminates   growth: its input changed and its contribution did not
FAIL  P4 floor<=ceiling  fresh_raise_growth_pts=14 exceeds the 'growth' weight of 10
```

**The second is the more instructive.** A bonus floor of 14 inside a component capped at 10 means
**every company at or above that floor scores identically** — the signal beneath it is silently
erased. **A relationship between two constants that nobody owned.**

### 🔴 3 · Four Notion columns computable today, written by nothing

`NYC Δ` · `Desk Jobs` · `NYC Band` · `Reach` — **all four derive from data already in the store.**
Three views are empty because of it. **`NYC Δ` will only populate on ~4 of 134 rows** even once
written, because almost nothing has been measured twice yet.

### 🔴 4 · Thirteen fields empty on every single row

Including `nyc_jobs_senior` and `nyc_jobs_facilities` — **the desk-role classifier computes role
types and nothing stores them.** "Head of Workplace as a buy signal" was the entire point of that
work. And `down_round` / `layoffs_hit_nyc`, both **scoring inputs that are empty everywhere** —
which makes them inert components.

> **A column empty on every row is a promise the system is not keeping.**

### 🔴 5 · 173 contacts exist in SQLite and are projected nowhere

The lane runs, the people are stored, **and JD cannot see them.**

### 🔴 6 · 39 companies in the store are on no board

All status `Research`. **Substantially** the ~40 first-scorings JD deliberately deferred — **but
that has not been proven by name**, and three counts that should be one number (39 unprojected, 40
deferred, 41 unscored) disagree.

### 🔴 7 · `rescore` has no scope flag

**`--apply` in a batch pipeline would land the 40 deferred first-scorings** — a decision nobody
would be taking.

### 🔴 8 · The funnel has stock views and no flow view

**Every view shows what IS. None shows what MOVED.** A funnel's health is flow — entries and exits
per stage per week, a stage nothing ever leaves, disqualifications spiking on one reason. **The
change log already holds everything this is computed from.**

---

# 12 · The defect classes worth knowing by name

**Five days produced ~18 real defects. Roughly half were the same shape.**

| class | what it looks like |
|---|---|
| **Declared but inert** | a rule present in config, code, or docs that **cannot fire, reporting green.** The dominant class in this project |
| **Built but unreachable** | a mechanism with passing tests and **no caller.** Four shipped this way. **An export is not a call site** |
| **Fail-closed** | a control jammed permanently shut. **Worse than an absent control**, because it converts "no protection" into false confidence |
| **Unknown treated as 0** | a missing measurement sorting, scoring, or displaying as a bad one |
| **False zero** | *structure absent* confused with *structure present but empty*. A 404 is not "no jobs" |
| **Same predicate, two layers** | a rule defined twice drifts. **Any predicate in two places must be defined once** |

**And the one number that explains why tests did not catch them:**

> **548 passing unit tests caught none of the three worst defects. A unit test is a contract on a
> function — it is not evidence the function is in the graph.**

---

# 13 · Where the truth lives

| question | file |
|---|---|
| **what a score means** | `FIT-SCORING-SPEC.md` §1–§8b — every rule traces to something JD said |
| **why any decision was made** | `reviews/phase1-lane-design-decisions.md` — 65 rounds, **read the topical index first** |
| **how JD thinks** | `brain/jd-operator-profile.md` |
| **funnel / cadence / human-in-the-loop theory** | `brain/10-workflow-and-decision-systems.md` |
| **what a batch costs** | `reference/batch-runbook.md` |
| **the non-degeneracy checks** | `reference/properties.py` — built and run, found two live bugs |
| **the board as designed** | `reference/notion-one-board-design.md`, `notion-views-spec.md` |
| **architecture that cannot be cheaply reversed** | CRMx `docs/adr/` — **0001 is load-bearing** |
| **defects seen and deliberately left** | CRMx `docs/found-not-fixed.md` |

---

# 14 · The shortest true summary

**Norman ingests companies, enriches them on three instruments, scores them against a
JD-calibrated model that reads every company relative to its funding stage, routes them into a
funnel, projects them to a Notion board it can rebuild from scratch, and attaches named humans.**

**Its architecture held for five days without a reversal.** SQLite is truth, Notion is a view,
one loop keeps them converged — **none of that has needed to change**, which is the strongest
available evidence the shape was right.

**Its weakness is not wrong code. It is disconnected code** — mechanisms built, tested green, and
called by nothing. **That is why the standard of proof here is an observable the artifact
produces, and never a description of its design.**

**And its single largest gap is that nothing starts by itself.**
