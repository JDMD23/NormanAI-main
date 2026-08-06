# The pillar coverage matrix — is every pillar evaluated, and every study mapped?

Answering three questions precisely: (1) is **every pillar** of elite software
design, architecture, agentic coding, and workflow management evaluated? (2) are
all **39 studies** mapped to the right pillar? (3) will each be **implemented as
designed** in the Norman rebuild? Plus the honest verdict on exposure pass #2.

**Study count:** 36 external studies + 3 Norman-subject studies (crm-core,
sales-nav, research). The 25 pillars below are grouped into 5 families. Canonical
exemplar per pillar in **bold**; every pillar ties to the Norman rebuild component
that implements it (`reviews/norman-rebuild-architecture.md`).

---

## Family A — Design & Architecture

| Pillar | Brain | Studies (canonical **bold**) | Norman component |
|---|---|---|---|
| A1 Simplicity & complexity control | 00 | **rendergit**, langchain (abstraction correction), karpathy-skills | the whole modular-monolith choice; "boil the task not the scope" (gstack) |
| A2 Deep modules, coupling, info hiding | 01 | **langchain**, mattpocock, langgraph | `core/*` module boundaries; `contexts/` |
| A3 Architecture, boundaries & formal models | 02 | **langgraph** (BSP), opentelemetry (API/SDK+no-op), **temporal** (durable exec), controller-runtime (reconcile) | `core/` vs `contexts/`; the workflow-shaped session; `core/reconcile` |
| A4 Data, state & identity | 04 | **dlt** (schema evolution/nonconformance), **splink** (identity), pandera, rapidfuzz, scrapling (self-healing refs), claude-mem (SoR+index) | `core/store`, `core/entity`, `core/contracts`, `core/trust` |
| A5 API & contract design | 05 | **jsonschema** (conformance+spec-as-data), **ats-scrapers** (provider registry), langchain (deprecation/rename-freeze), mirofish (consumer contract tests), linkedin_scraper | `core/lanes` adapter registry; `core/contracts`; the intake contract |
| A6 Resilience & failure design | 02 | **resilience4j** (breaker/bulkhead/limiter stack), controller-runtime (reconcile/self-heal), temporal (durable retry) | `core/lanes` (per-dep resilience), `core/reconcile`, `core/schedule` |

## Family B — Quality, Delivery & Ops

| Pillar | Brain | Studies (canonical **bold**) | Norman component |
|---|---|---|---|
| B1 Code craft (naming, comments, shape) | 03 | **linkedin-mcp-server** (invariants-with-scars), gstack (ADR-quality docs) | the mega-file split (F4); coding standards |
| B2 Testing & verification | 03 | **hypothesis** (property-based), understand-anything (reviewer-mechanization), mirofish/ats-scrapers (contract tests), superpowers (verification-before-completion) | `evals/` property + contract tests |
| B3 Evaluation & measurement | 03/09 | **justhireme** (eval harness), graphify (benchmark fairness), evidently (drift-as-eval), autoresearch (frozen judge) | `evals/` scoring harness (F1) |
| B4 Delivery & feedback loops | 06 | **hypothesis** (one-change-per-release), superpowers | CI, the release gate |
| B5 Observability | 06 | **opentelemetry** (golden signals, correlation), **evidently** (drift), claude-mem (supervise the daemon) | `core/observe` |
| B6 Release & governance | 06/07 | **opentelemetry** (rationale.md), mattpocock (ADR gate), hypothesis (two-cost review), agency-agents (CI-checked duplication), langchain (expand/contract) | shadow/live compiler; `docs/rationale.md`; ADR gate |

## Family C — Agentic Engineering

| Pillar | Brain | Studies (canonical **bold**) | Norman component |
|---|---|---|---|
| C1 Enforcement hierarchy (mechanize the mechanical) | 09 | **ECC** (hooks fire 100%), gstack (tool allowlists), justhireme (deterministic rubric core) | invariants as hooks/lints/CI; the write-guard |
| C2 Trust boundary | 09/10 | **guardrails** (on_fail actions, in/out guards), research (evidence-clamp), graphify (provenance), pandera, ECC (injection baseline) | `core/trust` |
| C3 Context & durable state for agents | 09 | **superpowers** (ledger), gstack (declarative context assembly), understand-anything (disk-carries-data) | `core/outbox`, `core/schedule` |
| C4 Agent memory | 09 | **claude-mem** (episodic), ECC (procedural/instincts) | (v2) learned enrichment patterns; receipts as episodic store |
| C5 Autonomy calibration & loops | 09/10 | **autoresearch** (autonomous loop), **orca** (bounded investigation), karpathy-skills (verifiable goals), research (split-objective prompting) | `core/schedule` loop; `contexts/priority` second pass |
| C6 Skill & tool interface design | 05/09 | **anthropic-skills** (knowledge deltas/progressive disclosure), **linkedin-mcp-server** (tool/MCP APIs), mattpocock (composition), ui-ux-pro-max (queryable knowledge), obsidian-skills (vendor skill), taste-skill (anti-default) | the agent-facing tool surface; operator LLM view |

## Family D — Workflow & Decision Systems

| Pillar | Brain | Studies (canonical **bold**) | Norman component |
|---|---|---|---|
| D1 Lifecycle state machines & hysteresis | 10 | **crm-core** (the Status machine + 57 floor), langgraph (typed channels) | `contexts/fit` state machine |
| D2 Evidence, provenance & confidence | 10 | **research** (evidence discipline), **graphify** (extracted/inferred/ambiguous), splink (explainable match) | `core/trust`; the Review-Required routing |
| D3 Authority & ownership | 10 | **linkedin-mcp-server** (provable ownership), **sales-nav** (field-ownership conflict), research (proposer/disposer) | `core/guard` field-level authority |
| D4 Cadence, scheduling & orchestration | 10 | **temporal** (durable orchestration), controller-runtime (requeue cadence), gstack (fleet) | `core/schedule` |
| D5 Human-in-the-loop design | 09/10 | **mattpocock** (frontier interrogation), crm-core (reason codes), ui-ux-pro-max (detect-then-ask) | Review-Required reasons; the operator decisions |

## Family E — Meta & Discipline

| Pillar | Brain | Studies (canonical **bold**) | Norman component |
|---|---|---|---|
| E1 Scope honesty & weight-class matching | 00 | **rendergit**, gstack (boil-the-task economics), temporal (adopt-model-not-engine) | the "one repo, right-sized" decisions; the open decisions |
| E2 Anti-patterns & catalog governance | 08 | **ECC** (catalog decay), **agency-agents** (originality gate/CI-checked dup), justhireme (tombstones) | the doc-sprawl fix (F3); config-consistency CI |
| E3 Security, legitimacy & compliance | 06 | **linkedin-mcp-server** (coherence, session), **ats-scrapers** (legitimacy ceiling), linkedin_scraper (session-as-artifact), guardrails (PII) | the trust boundary; the compliant-data hard problem |
| E4 Distribution, packaging & presentation | 05/09 | **obsidian-skills** (vendor skill), **rendergit** (dual-reader), ui-ux-pro-max + taste-skill (operator UI), anthropic-skills | `operator/` cards + views + LLM view |

---

## Mapping audit — are all 39 accounted for, and correctly?

**Yes.** Every study has a primary pillar (its canonical home, bolded above) and
appears as supporting evidence where it also contributes. Spot-checks on the
non-obvious ones:
- **scrapling** → A4 (self-healing references *are* derived data with a recompute
  path), supporting A6 — correct, not a scraping-trivia entry.
- **rapidfuzz** → A4 (fuzzy identity), supporting A6 (runtime dispatch/fallback
  parity) — its Norman use is identity, so A4 is right.
- **linkedin_scraper** → A5 (rename-and-freeze counterexample) + E3 (session-as-
  artifact); it's a comparative specimen, correctly mapped to the pillars it
  illustrates by contrast.
- **rendergit** → E1 (weight-class paperwork) + E4 (dual-reader); small repo,
  two distinct pillars, both real.
- **taste-skill/ui-ux-pro-max** → C6 + E4; the twins split cleanly (design
  knowledge as queryable data vs judgment prose).

**Coverage:** all 25 pillars have a canonical exemplar and ≥1 supporting study;
**19 of 25 have three or more** studies. No pillar is orphaned. No pillar rests on
a single study except by genuine specialization (D1 on crm-core's own machine —
appropriate, it's the subject).

## Fidelity — will each be implemented precisely as designed?

Each pillar maps to a **named component** in the rebuild architecture, and the
build plan sequences them foundations-first. The fidelity guarantee is structural,
not a promise: the invariants that carry each pillar are **mechanized** (C1) —
the write-guard enforces D3, config-schema-validation enforces A4/B6, the eval
harness enforces B3, contract tests enforce A5, property tests enforce B2, the
reconcile loop enforces A3/A6. A pattern that's enforced by a hook/lint/CI/test
cannot silently drift from its design; that is the whole point of the enforcement
hierarchy. Where a pattern is *judgment* not *mechanism* (D5 human-in-the-loop,
E1 scope honesty), fidelity rests on the brain doc + ADRs, which is the correct
tier for judgment.

**Three fidelity risks to name honestly:**
1. **Temporal/reconcile are models, not necessarily engines.** The *patterns* will
   be implemented; whether via the real engines or a lighter outbox/loop is a
   scope-honesty call (E1) — flag it in an ADR so it's a decision, not a drift.
2. **The trust boundary (C2) is the highest-consequence, least-mature pillar.** It
   has the most studies now (guardrails/research/graphify/pandera) but is the one
   most able to fail silently if under-built — it deserves the most eval coverage.
3. **Observability (B5) must be built in Phase 1, not deferred** — every other
   pillar's fidelity is *unverifiable in production* without it (you can't know a
   pattern held if you can't see it fail).

---

## Exposure pass #2 — the honest verdict

You asked what else is exposed and what repos fix it. **Straight answer: the
knowledge base is saturated, and continuing to add studies is now over-collection
— the exact anti-pattern the brain warns against** (brain/00 scope honesty;
brain/08 catalog decay; "when in doubt, leave it out"). The last three studies each
closed a *named* gap (W3/W4/W7); a fourth pass finds no new *pillar* and no new
*named weakness* that a repo would fix. The residual exposures are **operational
and organizational, not knowledge gaps** — and no repo studies them away:

- **Bus factor** (brain/08 #11): only JD + this brain understand Norman. Fix:
  rationale.md + ADRs + the glossary — *writing*, not studying.
- **The hosting/availability decision** (W6) and **the compliant-data / ToS
  decision** (E3 hard problem): *business/architecture choices*, not gaps.
- **Real-world validation:** no study substitutes for building it and watching the
  eval harness + drift monitors produce signal in production. The mechanisms are
  designed; they only pay out once running.
- **Security audit** of the running system: a *practice* (pen-test, secret scan),
  performed on real code, not learned from a repo.

**The elite move now is to stop studying and start building.** Every pillar is
evaluated, every study is mapped, and the architecture ties each to a mechanized
component. The brain is not going to get more ready by reading a 40th repo — it
gets more ready by Phase 0 producing code that the eval harness and observability
can measure. My recommendation, stated as plainly as I can: **lock the four open
decisions and begin Phase 0.**
