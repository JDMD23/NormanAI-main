# Four days, 22 defects — which repo would have prevented each, and the uncomfortable finding

Every defect below is real and was found this week. **The uncomfortable part is in §3.**

---

## 1. THE MAPPING

| # | defect | prevented by | how |
|---|---|---|---|
| 13 | `velocity.py` never wired | **Dagster asset model** | a node with no producer is visible on the graph |
| 22 | `funding_rounds` never written — growth's true root cause | **Dagster asset model** | same; the chain `growth ← velocity ← rounds ← nothing` is one glance |
| 11 | `workplace_contact` plumbed, never written | **Dagster asset model** | asset with no producer |
| 12 | `read_headcount` no caller, no storage field | **Dagster asset model** | asset with no consumer *or* producer |
| 14 | `changes_tags` never called | **Dagster asset model** | the Changes column is an asset nothing materialises |
| 18 | 10 rows violating ruling U-c for weeks | **Graphiti** | a fact carries `valid_to`; the stale cohort is a query, not an archaeology dig |
| 16 | `hq_city` constant across all 93 | **Graphiti** *(partly)* | "constant since when" becomes answerable; **fully caught by property tests** |
| 17 | `funding_stage` constant across all 133 | **property tests** | no repo needed — one assertion |
| 21 | `fresh_raise_growth_pts` 14 > weight 10 | **OPA** | policy has its own test suite; the *relationship* between constants has an owner |
| 10 | config said the opposite of what ran | **OPA** | policy is queried, not transcribed — the config *is* the behaviour |
| 3 | throttle reported, could not enforce | **OPA** | decide/enforce split is a boundary, not a convention |
| 5 | throttle had no callers at all | **Kage** / reachability | decisions verified against the codebase rather than asserted |
| 15 | `status_owner` a dead alias | **Kage** / reachability | two expressions of one rule, found mechanically |
| 8 | duplicate contacts — no natural key | **dlt** ← *already studied* | "incremental cursor + primary-key dedup = idempotent ingestion" |
| 9 | migration could not run against the state it diagnosed | **dlt** ← *already studied* | schema evolution with explicit upgrade paths |

---

## 2. THE ONES NO REPO WOULD HAVE PREVENTED

| # | defect | why no repo helps |
|---|---|---|
| 1 | J1 hysteresis inversion — a *missing* measurement demoted two bands | domain logic. Found by **running it**, not by reading it |
| 2 | eval why-gate whose regexes could never match | found by running the regexes against real output |
| 4 | throttle jammed shut — a source string passed into a timestamp slot | two adjacent same-typed positional args. **Keyword-only arguments** prevent it; no repo does |
| 6 | AE4 recording nothing — raising per company, silently | *"found by running it rather than reviewing it"* |
| 7 | AE4 recording only on heal | a category error about what an ancestor is |
| 19 | bare tokens — HEAD WAITER as the best contact | a judgment call about JD's own list |
| 20 | alphabetical "best contact" put an HR Manager above the CEO | a cut feature returning as a display detail |

**Seven of twenty-two. Every one found by executing something.**

> **Repos fix CLASSES. Running fixes INSTANCES.** No architecture prevents a wrong threshold or a
> mis-ordered argument — only meeting it does. **This is the argument for the scheduler being the
> highest-leverage item**, and it is why "more repos" is not the whole answer to JD's question.

---

## 3. THE UNCOMFORTABLE FINDING

**Two of this week's defects were already covered by studies we had already done.**

`studies/dlt.md`, written weeks ago, records:

> *"Incremental cursor in persistent state + primary-key dedup = idempotent ingestion."*

**Defect 8 is that sentence, violated:** `person_id` was generated per call, so re-running the
contacts lane inserted all 173 people again. The lesson was in the brain, in writing, with a
Norman application named beside it — *"the funding watcher and every scheduled source,
generalized."*

The same file records **schema evolution with explicit upgrade paths**, which is defect 9.

> **The gap was not missing knowledge. It was knowledge that had been recorded and never
> applied.** 36 studies, 11 brain docs — and the binding constraint is retrieval and application,
> not acquisition.

**This is why Cognee sits at #5 in the queue and not #1.** *"Turning an existing corpus into
structured, queryable knowledge"* is now a real need: the corpus is large enough that finding the
applicable lesson at the moment of building is itself a task. **The topical index in the ruling
log was the hand-made version of that, and it exists because the problem is already here.**

---

## 4. WHAT TO IMPLEMENT, RANKED BY DEFECTS PREVENTED

| rank | what | defects | cost |
|---|---|---|---|
| **1** | **Property tests + the scheduler** *(loop 3, spec'd)* | 16, 17, and **all seven of §2, faster** | days |
| **2** | **Asset graph — the model, not Dagster** | 11, 12, 13, 14, 22 | hours: write the eight derived values and their dependencies on one page |
| **3** | **Bi-temporal facts — the model, not Graphiti** | 18, and every future ruling change | a `valid_to` column and the discipline to set it |
| **4** | **Config coherence tests — the idea, not OPA** | 21, 10, 3 | one test file over `config/*.json` |
| **5** | Corpus retrieval *(Cognee-shaped)* | the §3 finding | later; the index works for now |

**Ranks 2, 3 and 4 are each a model to adopt and a tool to decline.** `brain/00`: *complexity
must be paid for by real, present needs.* Norman's present needs are eight derived values, one
ruling log and 21 config constants — **the models are free; the platforms are not.**
