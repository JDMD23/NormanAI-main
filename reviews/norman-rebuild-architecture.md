# Norman — ground-up rebuild architecture

The definitive architecture for rebuilding Norman as one system, derived from
`brain/00–10`, the 28 external studies, the automation re-mine, and deep study of
the three Norman repos (crm-core, sales-nav, research). Every design component
below names the brain principles that govern it and the studied repos that supply
its patterns, with how each is used.

---

## 0. Thesis

Norman is a **decision-support automation** whose product is *ranked trust*: an
operator (JD) acts on its output without re-checking it. It discovers companies,
enriches them from many sources, scores their fit as future NYC office tenants,
maps warm-introduction paths, and routes each through a lifecycle of states — all
unattended, on a schedule, against churning logged-in websites. The rebuild's job
is to make that trustworthy and to keep it *running* for a year without a human
noticing it quietly died.

**The shape (settled across two consolidation verdicts — see
`norman-repo-consolidation-adr.md`): one repo, one `core/`, N `contexts/`.** A
modular monolith (brain/02): the three current repos are not sibling systems —
they share a datastore, a browser, and their discipline, and are wired today
through path-imports, subprocess calls, and duplicated machinery (the
distributed-monolith anti-pattern, brain/08). They become bounded-context modules
over a shared substrate.

```
norman/
  core/                         the shared substrate (Section 2)
    entity/                     entity model + identity resolution
    store/                      system of record + Notion projection
    browser/                    persistent supervised browser daemon
    outbox/                     durable state, exactly-once, receipts
    schedule/                   the autonomous loop: leases, windows, dispatch
    lanes/                      BaseLane framework + adapter registry
    trust/                      validation, evidence-clamp, injection defense, provenance
    observe/                    telemetry, silent-failure + drift detection
    guard/                      the single field-level write authority
    contracts/                  typed schema/intake/config contracts (generated)
  contexts/
    discovery/                  (was NormanAI-research) find + qualify → propose
    fit/                        (was crm-core) enrich → score → status state machine
    warm_path/                  (was NormanAI-sales-nav) persona + relationship mapping
    priority/                   second pass: bounded investigation → priority
  operator/                     cards, views, daily review (human + LLM surfaces)
  evals/                        scoring eval harness, property tests, contract tests
  docs/                         rationale.md + generated authority map + runbooks
```

Deployment: one deployable; each context is an **independently-scheduled** lane
family with its own cadence and autonomy policy (Discovery is API-metered and
JD-triggered; Warm-Path reads JD's personal network and is more sensitive; Fit is
the unattended core). Independent *schedules*, one *codebase* — because they share
Chrome, the datastore, and every invariant.

---

## 2. The substrate — `core/`

The substrate is what makes the design in `brain/10` survive contact with real,
scheduled, adversarial websites. Build it once; every context inherits it.

### 2.1 Entity model & identity resolution — `core/entity/`

- **Owns:** the canonical Company (and, v2, Person) entity; resolving
  name/domain/LinkedIn/SN-account to *one* entity **before any write**.
- **Brain:** 04 (model the domain, IDs opaque+stable), 10 #6 (identity is the gate
  the whole system's correctness hangs on).
- **Patterns → how:**
  - **splink** *(pending study)* — probabilistic multi-field record linkage; the
    engine for "are these two sources the same company?" and the `identity conflict`
    Review-Required reason.
  - **rapidfuzz** — concrete fuzzy-name-matching library for the string-similarity
    layer (dedup, rediscovery idempotency) beneath splink; use directly.
  - **ats-scrapers** — identity-first, website-corroboration-before-write.
  - **linkedin-mcp-server** — provable ownership before mutation.
- **Norman:** unifies `entity_identity.py`, `crm_identity_keys.py`, and
  research's "Core owns hard dedup" into one resolver. Rediscovery updates the
  queue, preserves original `Added From`, never duplicates.

### 2.2 System of record & Notion projection — `core/store/`

- **Owns:** the authoritative datastore; Notion as a *projection* of it, not the
  source of truth.
- **Brain:** 04 (never let a weakly-guaranteed shared store be your contract; one
  boring store; derived copies recomputable from source), 02.
- **Patterns → how:**
  - **claude-mem** — SQLite as truth + a derived, rebuildable index; the exact
    shape to copy (Postgres or SQLite as SoR, Notion rebuilt from it).
  - **twenty** *(pending study)* — a real CRM's relational domain model as
    evidence for the schema.
  - **langgraph** — typed channels as declarative state-merge policy; model each
    field's update semantics (overwrite / accumulate / newest-wins) explicitly.
  - **jsonschema** — the datastore↔Notion mapping is a versioned schema-as-data.
- **The decision this forces (open, Section 6):** today Notion *is* the SoR — a
  shared, mutable, weakly-typed store that two contexts write concurrently. The
  rebuild should make a real datastore the truth and Notion a rebuilt operator
  view. This dissolves the schema-drift and concurrent-write coupling at the root.

### 2.3 Browser automation substrate — `core/browser/`

- **Owns:** one persistent, supervised Chromium the whole system shares.
- **Brain:** 06 (right-size; stateful expensive resources), automation-remine A/B.
- **Patterns → how:**
  - **gstack** — the long-lived browser daemon: ~3s cold, ~100–200ms warm, cookies
    and logins persist across calls. The architecture, directly.
  - **linkedin-mcp-server** — daemon coordination Norman half-built: election,
    lock, lease, liveness/health-check, version auto-restart; **coherence-not-
    invisibility** (the browser must not contradict itself; never inject a
    fingerprint; verify identity by measurement); **locale-independent detection**
    (key on URL patterns / attribute presence, never on displayed text like
    "Connect"/"1st").
  - **scrapling** — **self-healing selectors** (fingerprint + similarity
    relocation) so lanes survive Crunchbase/LinkedIn/SN redesigns unattended; the
    **capability ladder** (HTTP → real browser → stealth), fetch cheap first;
    surface confidence on re-bind (a silent partial match is a phantom fact).
  - **linkedin_scraper** — **session-as-artifact** auth: a setup step mints a
    reusable session; lane code never touches credentials.
- **Norman:** collapses crm-core's `browser_coordination.py`, research's duplicate
  of it, and sales-nav's `lib/chrome.py` into one daemon — ending the cross-repo
  fight for Chrome. `browser-human-pace.json` becomes the daemon's pace policy.

### 2.4 Durable state & exactly-once — `core/outbox/`

- **Owns:** recoverable, crash-safe, exactly-once mutation; the receipt ledger.
- **Brain:** 04 (event-sourced facts), 05 (idempotency keys), 09 (write-ahead
  ledger; disk carries data).
- **Patterns → how:**
  - **Norman's own `causal_outbox.py` is the reference — keep and generalize it.**
    Its intent → verified readback (facts must match intent) → finalized receipt is
    genuinely excellent exactly-once. Promote it from crm-core-specific to a core
    primitive every context uses.
  - **superpowers** — the ledger is recovery truth; trust it and `git log`/receipts
    over recollection after a restart.
  - **langgraph** — checkpoint-at-a-consistent-boundary; ship a **conformance kit**
    for outbox backends (its checkpoint-conformance pattern) so a future
    SQLite/Postgres store is provably correct.
  - **dlt** *(pending study)* — incremental/merge loads + pipeline state; the mature
    form of the outbox+lanes for the enrichment pipeline specifically.

### 2.5 The autonomous loop — `core/schedule/`

- **Owns:** the scheduled sessions (funding watcher 5×/day; Core sessions; closeouts),
  leases, execution windows, duplicate protection, dispatch.
- **Brain:** 09 (autonomous experiment loops), 10 (precondition gates, tiered cadence).
- **Patterns → how:**
  - **autoresearch** — the daily maintenance session *is* an autonomous loop; adopt
    its rigor: **frozen judge** (the loop cannot edit the scoring config or eval —
    already true, keep it structurally impossible), **fixed-budget normalization**
    (the 15-min window + lane allowance = the hard kill criterion), **bounded crash
    policy** (trivial→retry, broken→log-and-move, N-fails→stop-and-surface — your
    Blocked/Manual outcomes formalized), **negatives are the record** (log discards
    and crashes as first-class receipts, not just successes).
  - **linkedin-mcp-server** — singleton coordination (lease/lock/liveness) done right.
  - **gstack** — fleet auto-update / declarative context assembly if sessions ever
    span machines.
- **Norman:** unifies `crm_runtime_dispatch.py`, `crm_maintenance_run.py`,
  `crm_signal_watcher.py`, leases and windows. **Tiered cadence** (10 #9): Prospects
  checked often, Watchlist rarely — attention is a metered budget.

### 2.6 The lane framework — `core/lanes/`

- **Owns:** `BaseLane` (identity → fetch → evidence → guarded write → Need-\*
  lifecycle) and the adapter registry every source plugs into.
- **Brain:** 05 (provider-adapter pattern), 10 #7 (operational outcomes ≠ business
  state), 10 #8 (all-or-nothing lanes).
- **Patterns → how:**
  - **ats-scrapers** — **ABC + decorator registry as the only lookup**; a new source
    is one self-registering file; **capability declared as class-attribute data**
    (engine, rate limits, auth mode) consumed by a shared fetcher; **per-adapter
    docstring capturing that source's quirks** (the knowledge-delta); **a contract
    test per source** so upstream drift fails CI red.
  - **langchain** — the middleware seam, and *dogfood it*: every built-in lane goes
    through the same public `BaseLane` seam (proves the seam is real).
  - **rapidfuzz** — capability dispatch (best-first, graceful fall-through) for the
    HTTP→browser escalation.
- **Norman:** the 3 fit lanes + Sales Nav + Discovery's sources all become adapters
  over one `BaseLane`. Success/Partial/Blocked/Manual are **operational** metadata in
  the audit surface — never business Status. The `Need-*` checkbox is the work queue.
  All-or-nothing: a transient failure consumes no allowance, writes no partial
  evidence, stays queued.

### 2.7 The trust boundary — `core/trust/`

- **Owns:** turning untrusted scraped/LLM content into a *fact* only after
  validation; provenance and confidence on every claim. This is the biggest
  unbuilt exposure.
- **Brain:** 09 (evidence-clamping, injection defense, the description/routing
  rules), 10 #4 (facts are claims).
- **Patterns → how:**
  - **NormanAI-research (own repo, exemplary — generalize it)** — **evidence-
    clamping**: the *system* decides the label from the cited evidence and overrides
    the model when unsupported (`fitHint` clamped to `none` unless `nycEvidence`
    quotes it); `keywordHits` = exact phrases or no candidate; **Unknown ≠ 0**; no
    source URL = reject. Lift this from Discovery into a core primitive every
    LLM-touching stage uses.
  - **guardrails** *(pending study)* — validate/constrain LLM output structurally
    before it becomes a written fact; the framework form of research's hand-rolled
    clamp.
  - **graphify** — **provenance labels** (extracted / inferred / **ambiguous**),
    auto-routing *ambiguous* to Review Required; **deterministic-first extraction**
    (parse structured Crunchbase data for free; reserve the LLM for genuine
    interpretation — cuts cost *and* hallucination surface).
  - **pandera** *(pending study)* — data-quality contracts at the boundary
    (parse-don't-validate over tabular enrichment data).
  - **ECC** — the prompt-injection defense baseline (scraped page content is
    untrusted input that can carry adversarial instructions).
  - **linkedin-mcp-server** — coherence; treat inbound pages as attack surface.
  - **orca** — grounding: every claim cites evidence; never fabricate.

### 2.8 Observability — `core/observe/`

- **Owns:** knowing when a lane goes *quiet*, and when scores/inputs *drift* —
  before the operator acts on a stale board.
- **Brain:** 06 (four golden signals; alert on symptoms users feel), 09.
- **Patterns → how:**
  - **opentelemetry** — a **correlation ID per company per session**, traces across
    lanes, the golden signals; the **API/SDK-with-no-op-default** shape so
    instrumentation is zero-cost when unconfigured; a standing **rationale.md**.
  - **evidently** *(pending study)* — score-distribution and input drift monitoring
    (is the Fit Score distribution moving? are NYC-head counts trending oddly?).
  - **claude-mem** — a capture daemon is a distributed system: **supervise it or it
    silently stops** — the exact failure mode of scheduled enrichment.
- **Norman:** upgrades receipts (forensics after the fact) with real-time alerting
  and drift detection. "Did the 12:00 LinkedIn closeout run, and did throughput
  drop?" answerable in seconds.

### 2.9 The single write authority — `core/guard/`

- **Owns:** the *one* path through which any Notion/SoR write passes; field-level
  authority enforcement.
- **Brain:** 04 (one writer per value), 10 #3 (conditional authority: `(field ×
  state) → owner`; refuse writes you don't own rather than guess).
- **Patterns → how:**
  - **linkedin-mcp-server** — the `_owned()` model: every destructive/mutating op
    routes through one ownership check; make `notion_write_guard` the **only** write
    path, enforced (a test/lint that no write bypasses it), not conventional.
  - **Norman** — resolves the field-ownership conflicts already flagged across
    repos (Sales Nav vs the LinkedIn lane over headcount; Research never-writes-
    Notion; the scorer owns Status; humans own protected relationship Statuses) in
    one guard instead of across three codebases. Uses crm-core's already-good
    **verified writes** (`patch_page_properties_verified`: write → read back →
    confirm) as the commit primitive.

### 2.10 Contracts as data — `core/contracts/`

- **Owns:** the typed, versioned contracts that were hidden agreements: the
  intake CSV/funding-event schema, the Notion property map, the Fit formula.
- **Brain:** 05 (spec-versions-as-data; serialization formats are contracts), 01.
- **Patterns → how:**
  - **jsonschema** — spec/versions as data built by a factory, not a class tree;
    schema-validate the config and the Notion payloads; a shared conformance suite.
  - **justhireme** — the Fit formula stays a **deterministic rubric in config**
    (`fit-score-weights.json` is already this — keep).
  - **agency-agents** — **CI-checked duplication**: where a fact must live in two
    places, a build check fails on disagreement (the fix for crm-core's three-
    conflicting-catalog-counts and the F3 authority-map).
  - **ats-scrapers / mirofish** — the intake CSV columns and each source's shape
    become contract-tested modules, not the hidden `CSV_ALIASES` agreement Research
    depends on today.
  - **mattpocock** — a single **CONTEXT.md glossary** for Norman's heavy vocabulary
    (Status meanings, Need-\* markers, reason codes) so every doc/prompt/property
    name stays consistent.

---

## 3. The contexts — `contexts/`

Each context is a bounded model (Evans/DDD) with field-level write authority,
built entirely on the substrate above.

### 3.1 Discovery — `contexts/discovery/` (was NormanAI-research)
- **Owns:** finding + qualifying candidates; **proposing** them to intake (never
  mutates — Core owns commit + dedup). Preserve this proposer/disposer split as an
  internal contract.
- **Patterns → how:** research's **split-objective prompting** (separate broad-recall
  and tight-precision prompts, never one prompt for both — brain/09) and
  **evidence-clamping** (2.7); **orca** (bounded investigation: cheap deterministic
  baseline, budgeted LLM drill-down, cost in tool descriptions, read-through cache);
  **autoresearch** (the Grok-Automations no-code test — validate the searches find
  good companies *before* building the writer); **graphify** (deterministic-first,
  provenance); **ui-ux-pro-max** (detect-then-ask, never default the mode silently).

### 3.2 Fit — `contexts/fit/` (was crm-core)
- **Owns:** enrich → Fit Score → **Status state machine**.
- **Patterns → how:** **brain/10 is the spec** — explicit total state machine;
  **hysteresis** (the 57 demotion floor — asymmetric enter/exit so 60↔59 doesn't
  flap); protected/human-owned states the machine may refresh but not route.
  **justhireme** (the scoring **eval harness** — labeled cases through the real
  scorer, invariant cases that fail CI alone, directional bounds; you already have
  the labeled calibration data); **hypothesis** (property-test the invariants:
  score ∈ [0,100], renormalize-on-missing, Unknown≠0, no illegal transition);
  **langgraph** (status/score as typed channels); **jsonschema** (config-as-formula).

### 3.3 Warm-Path — `contexts/warm_path/` (was NormanAI-sales-nav)
- **Owns:** persona targets, mutual-connection warm paths, intro-node ranking,
  connection tiers; writes only warm-path fields.
- **Patterns → how:** **linkedin-mcp-server** (Sales Nav is LinkedIn — coherence,
  session-as-artifact, locale-independent detection, tool-interface discipline);
  **scrapling** (self-healing selectors on the Relationship Explorer);
  **splink/rapidfuzz** (person identity + intro-node dedup). Its people graph
  (SQLite today) becomes a promoted Person entity in `core/entity/` when v2 needs it.

### 3.4 Priority — `contexts/priority/` (crm-core Second Pass)
- **Owns:** for already-qualified companies (Fit 50+), verifying *how urgently* to
  pursue — Priority Score/tier, not Fit; never mutates Fit/Status/relationships.
- **Patterns → how:** **orca** is the exact shape — deterministic baseline (Fit)
  already ran; Second Pass is the **budgeted LLM drill-down** with cost-priced tools
  and a read-through cache; **guardrails** validate the priority output;
  **brain/09** bounded-investigation discipline.

---

## 4. Operator surface — `operator/`
- **Owns:** the cards (CURRENT/WHY/DATA/NEXT), the ~11 daily views, the daily review.
- **Brain:** 10 #11 (surface score-change AND state-change as distinct truths).
- **Patterns → how:** **rendergit** (**dual-reader**: a human card *and* an LLM view
  of board state, so an agent can consume it cheaply); **ui-ux-pro-max + taste-skill**
  (card design; **anti-default** discipline if cards ever leave Notion);
  **mattpocock** (the vocabulary glossary drives the card copy); **anthropic-skills**
  (progressive disclosure — the card is the metadata tier, Full Audit the deep tier).
  Views are **windows for the human only**; machine work is driven by guarded
  properties and receipts, never by reading a view.

---

## 5. Cross-cutting — `evals/` and governance

### 5.1 Testing & eval — `evals/`
- **justhireme** — the CI-gated scoring eval harness (the single highest-leverage
  correctness win; you already have the labeled data in `crm_calibration_compare.py`).
- **hypothesis** — property tests on scorer + outbox invariants.
- **ats-scrapers / mirofish** — a **contract test per source and per external
  dependency** (Notion, Grok, Crunchbase/LinkedIn shapes) so drift fails CI red.
- **langgraph / jsonschema** — a **conformance kit** for lane adapters and outbox
  backends.

### 5.2 Release & governance — `docs/`
- **opentelemetry** — a standing **rationale.md** (why the outbox, the shadow/live
  compiler, identity-first, the state machine); **stability encoded in structure**.
- **hypothesis** — **one user-visible change per release**; the **two-cost review**
  question (does this hurt users? maintainers?).
- **mattpocock** — the **three-condition ADR gate** (hard-to-reverse ∧ surprising ∧
  real-tradeoff).
- **langchain** — **rename-and-freeze / expand-contract** when evolving the schema
  or a contract.
- **agency-agents** — CI-checked config duplication; **JustHireMe** — **tombstone**
  superseded docs (crm-core's 13 archived FABLE prompt files) instead of leaving
  them to mislead. Kill the doc sprawl: generate the authority map from a manifest.
- **Norman** — the shadow/live compiler, one-mode invariant, and release-readiness
  gate are already good; keep them, and make the "safety refuses uncertain writes"
  rule (2.9) the enforced default.

### 5.3 Security & compliance — the hard problem
- **ats-scrapers** — the **legitimacy ceiling**: your careers/ATS lane hits public
  endpoints and is durable; the logged-in Crunchbase/LinkedIn/Sales-Nav lanes are
  the fragile, ToS-adverse, redesign-brittle base under your most valuable signals.
- **orca / justhireme** — both routed LinkedIn data through **compliant providers**
  rather than logged-in sessions; make the official/API path the default and the
  scrape the graceful-degradation fallback (capability ladder, 2.3) where the data
  justifies the cost. This is the single decision with the largest effect on whether
  Norman is running in a year.
- **linkedin-mcp-server** — credential/session security; **linkedin_scraper** —
  session-as-artifact; **guardrails/PII** — you store dossiers on individuals
  (founders, employees) → real GDPR/CCPA exposure to design for.

---

## 6. How to *build* it (the meta-layer)

The rebuild itself is an agentic engineering project; use the studies for the
*method*, not just the product (brain/09; two-level programming — autoresearch):
- **superpowers** — brainstorm → spec → plan → **subagent-driven execution** with
  per-task review + verification-before-completion; write-ahead ledger for the build.
- **mattpocock** — frontier interrogation to lock each context's spec; ADR gate.
- **ECC / gstack** — **mechanize the mechanical**: the invariants (write-guard,
  Unknown≠0, no-write-bypass, one-mode) become hooks/lints/CI that fire 100%, not
  prose that's followed 50–80%.
- **karpathy-skills** — surgical, verifiable-goal-shaped changes; **hypothesis /
  justhireme** — every behavior change lands with a property or eval case.
- **This brain repo (NormansBrain)** stays separate as the thing that *informs* the
  build — never merged into the runtime (the first rule the brain teaches).

---

## 7. Sequenced build plan

**Phase 0 — foundations (get these right first; they're irreversible):**
1. `core/store/` decision: real datastore as SoR, Notion as projection (Section 2.2).
2. `core/entity/` identity resolver (rapidfuzz now, splink after its study).
3. `core/contracts/` the intake/Notion/formula schemas as typed modules.
4. `core/guard/` the single verified write path with field-level authority.
5. `core/outbox/` promoted from crm-core's causal outbox to a core primitive.

**Phase 1 — the automation substrate (what keeps it alive unattended):**
6. `core/browser/` the persistent supervised daemon + self-healing selectors.
7. `core/lanes/` BaseLane + adapter registry.
8. `core/trust/` evidence-clamp + provenance + guardrails, generalized from Research.
9. `core/observe/` telemetry + silent-failure + drift.
10. `core/schedule/` the autonomous loop with autoresearch discipline.

**Phase 2 — the contexts, over the substrate:**
11. `contexts/fit/` (the state machine + scoring + the eval harness first).
12. `contexts/discovery/` (proposer into intake).
13. `contexts/priority/` (bounded investigation).
14. `contexts/warm_path/` (the scaffold, built right on day one).
15. `operator/` cards + views + dual-reader review.

**Phase 3 — governance & derisking:**
16. rationale.md, ADR gate, one-change-per-release, tombstone the old docs.
17. Pilot a compliant data path (the legitimacy hard problem).

**Gate before Phase 0:** the five domain studies (dlt, splink, guardrails,
evidently, pandera) — they directly inform store/outbox (dlt), entity (splink),
trust (guardrails/pandera), and observe (evidently). Running them first is the
last step to a genuinely elite brain for this build.

---

## 8. Open decisions for JD
1. **System of record:** move truth off Notion to a real datastore (recommended),
   or keep Notion as SoR and accept its coupling/typing limits?
2. **Compliant data:** invest in official Crunchbase/LinkedIn data paths to derisk
   the legitimacy ceiling, or accept the logged-in-scrape base?
3. **The five domain studies:** run them before Phase 0 (recommended), or build
   from the current brain and fold their lessons in as we go?
4. **Repo:** confirm the rebuild is a *fresh* repo (recommended), with NormansBrain
   staying separate as the informing knowledge base.
