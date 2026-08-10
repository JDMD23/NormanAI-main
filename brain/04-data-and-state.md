# 04 — Data and state

## Model the domain, not the UI and not the framework

Data models designed from screens ("we need a field for this page") or from framework
convenience (whatever the ORM scaffolds) rot immediately. Model the *domain*: what
are the entities, what identifies them, what facts are true about them, which facts
change together, which are immutable history. The screens will change every quarter;
the domain changes when the business does.

Key modeling calls that pay compound interest:
- **Immutable facts vs mutable state.** An order's line items at purchase time are
  history — never edit them in place; a user's display name is state. Storing history
  as mutable rows (or state as append-only logs) causes both correctness bugs and
  needless complexity. Money, especially, is event-shaped: append entries, derive
  balances.
- **IDs are opaque and stable.** Natural keys (email, username, SKU) leak into URLs
  and foreign keys, then someone needs to change one. Surrogate keys + unique
  constraints on natural keys.
- **When there's no shared unique ID, identity is probabilistic evidence-weighing,
  not string equality** (splink / Fellegi-Sunter). The pipeline: **block**
  (generate candidate pairs by a cheap key so you never compare all N², e.g. same
  domain / name-prefix) → **compare each field at graded levels** (exact / fuzzy /
  different, not a boolean) → **weight the evidence** (each level carries a learned
  match weight; rare-value matches count more than common ones — term-frequency
  adjustment) → **threshold and cluster** links into one canonical entity. Weigh
  *multiple non-correlated* fields (name + domain + handle + location), and make the
  match *explainable* so a human can adjudicate the uncertain ones. This is the
  engine behind "resolve identity before the first write" (brain/10 #6) and the
  identity-conflict decision.
- **Nullability is a modeling statement.** A nullable column means "this fact may
  legitimately not exist" — not "I didn't want to write a migration." Every nullable
  field forces a branch in every consumer forever.
- **Enums and status fields:** model state machines explicitly. List the states,
  list the legal transitions, enforce them in one place. Most "impossible" production
  data is an unenforced state machine.

## The database is a competence, not a black box

Elite teams treat SQL and the database as a first-class part of the system:
- Constraints (foreign keys, uniques, checks) are non-negotiable — they are the only
  invariant enforcement that survives every code path, including the bugs and the
  manual fixes. "We enforce it in the app" means it isn't enforced.
- Indexes follow query patterns, verified with `EXPLAIN`, not superstition. The
  classic failure is N+1 queries hidden by an ORM — reviewable only if someone looks
  at the actual query log.
- Transactions delimit *invariants*, not functions: everything that must be true
  together commits together, and nothing else joins the transaction (no HTTP calls
  inside transactions — ever).
- Prefer one boring relational database until a *measured* workload says otherwise.
  Polyglot persistence multiplies operational surface and destroys transactional
  guarantees; adopt a second store for a proven access pattern (search, large blobs,
  true key-value scale), never for novelty.

## State in application code

- Default to immutability; create new values instead of mutating shared ones. Most
  "spooky action at a distance" bugs are shared mutable state with unclear ownership.
- Every piece of mutable state gets exactly one owner. Two writers to one value is
  a design bug even when a lock makes it "safe." Where multiple writers are the
  design (fan-in, parallel workers), attach a *declared merge policy* to the state
  cell itself — overwrite-last / accumulate / reduce-with-operator / barrier —
  rather than scattering conflict resolution across call sites (LangGraph's typed
  channels are the reference implementation; see studies/langgraph.md).
- Derived state (caches, denormalized counts, materialized aggregates) must be
  *recomputable from source*. If the derived copy can drift and nothing can rebuild
  it, data corruption is a matter of time.
- References into structure you don't control (CSS selectors, API response paths,
  UI-test locators) are derived data that *will* break: store a fingerprint of
  the target at bind time and re-derive by similarity when the structure shifts —
  deterministic matching beats "ask an LLM to find it again" (offline, cheap,
  explainable). Surface confidence when re-binding; a silent partial match is a
  new bug wearing the old name. (Reference implementation: Scrapling's adaptive
  selectors — studies/scrapling.md.)
- Global state (singletons, module-level mutables, thread-locals) couples everything
  it touches and makes tests order-dependent. Thread state explicitly, or scope it
  to a request/job context object.

## Data crossing boundaries

- Validate at the boundary, then trust internally. Parse, don't validate: convert
  raw input into a rich internal type *once*, at the edge, so interior code never
  re-checks (`parse_order(json) -> Order`, not `is_valid(dict)` sprinkled everywhere).
- **Validation is a declared nonconformance policy, not a boolean.** Three mature,
  independent frameworks converged on this — a data loader (dlt), an LLM guard
  (guardrails), a dataframe validator (pandera): when data doesn't conform, you
  don't just "reject" — you apply a *declared policy per rule* drawn from a small
  universal vocabulary:
  - **accept & evolve** (dlt `evolve`) — widen the schema to fit the new shape;
  - **coerce/fix** (pandera `coerce`, guardrails `fix`) — repair to a conforming value;
  - **discard the value** (dlt `discard_value`, guardrails `filter`) — drop the field, keep the record;
  - **discard the record** (dlt `discard_row`) — drop the whole row;
  - **reject loudly** (dlt `freeze`, guardrails `exception`, pandera eager raise);
  - **ask again** (guardrails `reask`) — send it back to the producer/model;
  - **pass but record** (guardrails `noop`) — let it through, log the deviation.
  Declare the policy *per field family*, at the boundary. For batches, prefer
  **lazy validation** (pandera): collect *all* failures into a structured table in
  one pass, not fail-fast on the first. This single concept unifies schema
  evolution, LLM-output guarding (brain/09), Unknown≠0 (= discard-value, never
  zero-fill), and reason-coded human routing (brain/10 #10: Review-Required reasons
  are `reask`/`refrain` policies).
- Serialization formats are contracts: additive changes only (new optional fields);
  renames and type changes are breaking and need versioning or expand/contract.
- Timestamps in UTC, ISO-8601 at boundaries, timezone math only at display.
  Money in integer minor units or decimal — never floats. These two rules are cheap
  to follow and catastrophically expensive to retrofit.

## Bi-temporal storage: a measured value has two clocks

A stored measurement carries **when it was true in the world** and, separately, **when we
recorded it**. Collapsing them into one timestamp loses both questions. Supersession then sets an
**end-date** rather than overwriting — so "what is true now" and "what was true then" are
answerable from the same store, and a rule change produces a *countable* stale cohort instead of
a silent one (studies/graphiti.md; Norman BI2, where ten rows written under a superseded rule fed
a score for weeks and were invisible until every row was recomputed).

Corollary: **staleness is a graph property, not a flag.** If you know what a derived value
depends on, you know when it is stale without anyone remembering to mark it (studies/dagster.md).
