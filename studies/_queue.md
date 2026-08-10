# Study queue — repos for a brain that thinks, ranked by the Norman defect they address

36 studies done. This queue covers the gaps that **this week's defects** exposed, not general
interest. Each entry names the specific failure it would have prevented.

---

## 1. Graphiti / Zep — temporal knowledge graph, facts with validity windows

**https://github.com/getzep/graphiti**

> Every fact carries a **`valid_from`**, a **`valid_to`** when superseded, and an **`invalid_at`**
> when explicitly contradicted. Temporal reasoning is a first-class feature rather than a layer
> on top of retrieval.

**The Norman defect it addresses — BI2, this week:** *"a ruling was made, the code obeyed it, and
the data never did."* Ten velocity rows written before ruling U-c kept feeding the growth
component for weeks, invisible until someone recomputed all 133.

**And it describes NormansBrain itself.** `reviews/phase1-lane-design-decisions.md` is **a
temporal knowledge graph maintained by hand**: 60 rounds, a topical index, a superseded-rulings
table, and an ID-collision note because `Q1`–`Q4` were used twice. **Every one of those is manual
bookkeeping of what Graphiti does structurally.**

**Highest-value study in the queue.** Read for the *validity-window model*, not to adopt the
database.

---

## 2. Kage — git-native memory for coding agents

**Decisions and fixes stored as repo files, and verified against the codebase.**

**The Norman defect:** the CRMx agent **did not know its own repo contained an Apollo vendor
eval** it had produced two sessions earlier (AT2). A session boundary invalidated everything not
written down — and the thing *was* written down, in `docs/`, and still wasn't found.

**"Decisions as repo files" is exactly NormansBrain's design.** The half Norman doesn't have is
**"verified against the codebase"** — we've been doing that by hand, one round at a time, for
sixty rounds. That is the whole reason the reachability check and the property module exist.

---

## 3. Open Policy Agent — policy as a separate, testable, versioned artifact

**https://github.com/open-policy-agent/opa**

> A declarative language for authoring policy, separated from the code that enforces it, with its
> own test suite.

**The Norman defect — BK1:** `fresh_raise_growth_pts = 14` against a `growth` weight of `10`.
**Not a code bug.** A relationship between two constants in a config file, where nothing owns
relationships. `formula_is_coherent` exists and catches this class; it missed this instance
because coherence rules are written per-case rather than as policy over the config.

**~180 rulings live in `config/*.json` as constants with prose notes.** Read OPA for how a mature
system makes policy **queryable and testable in its own right**, not for Rego.

---

## 4. Dagster — the asset-centric model (read the idea, not the orchestrator)

**https://github.com/dagster-io/dagster**

> Asset-centric rather than task-centric: model the **things produced** and their dependencies,
> not the steps run. Lineage and staleness fall out of the graph.

**The Norman defect — BL1, the biggest of the week:**

```
growth  ←  funding_velocity  ←  funding_rounds  ←  (nothing writes it)
```

A scoring component consumed a value nothing produced, and **no representation of the system made
that visible.** An asset graph shows it at a glance.

**Do not adopt Dagster** — Norman needs one cron, not an orchestration platform (`brain/00`:
complexity must be paid for by a present need). **Steal the asset-dependency model** and the
staleness idea.

---

## 5. Cognee — turning an existing corpus into queryable structure

**https://github.com/topoteretes/cognee**

Where Graphiti is optimised for the *interaction loop*, **Cognee is optimised for turning an
existing body of documents into structured, queryable knowledge.**

**The Norman fit:** 36 studies, 11 brain docs, 60 rounds of rulings, 15 ADRs. **That corpus is
now large enough that finding the applicable ruling is itself a task** — which is why the topical
index had to be written by hand, and why rounds 34–37 got lost.

**Read second, after Graphiti.** The two answer different halves and Graphiti's half is the one
biting.

---

## 6. Survey repos — for breadth, cheap to skim

- **https://github.com/TeleAI-UAGI/Awesome-Agent-Memory** — curated systems, benchmarks, papers
- **https://github.com/DEEP-PolyU/Awesome-GraphMemory** — graph-based agent memory specifically
- **https://github.com/NirDiamant/Agent_Memory_Techniques** — 30 runnable notebooks: episodic vs
  semantic memory, MemGPT, Mem0, Letta, Zep, Graphiti, LoCoMo benchmarks

**Skim these to pick, don't study them.** They are indexes, not architectures.

---

## What is deliberately NOT here

- **Airflow / Prefect** — Norman needs one scheduled lane. An orchestration platform is
  complexity with no present need to pay for it.
- **Mem0** — vector-first with an optional graph. Norman's problem is *supersession over time*,
  which is Graphiti's axis, not Mem0's.
- **LangChain / LangGraph** — already studied.
- **Anything RAG-shaped.** Norman's corpus is small and structured; the problem is *which ruling
  applies and is it still current*, which is a graph question, not a retrieval one.

---

## The order

**Graphiti first.** It is the only one that addresses a defect Norman hit *this week*, and the
model it teaches — **a fact is true over an interval, and supersession is data rather than
bookkeeping** — is the thing both the ruling log and the store are currently doing by hand.
