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
- Global state (singletons, module-level mutables, thread-locals) couples everything
  it touches and makes tests order-dependent. Thread state explicitly, or scope it
  to a request/job context object.

## Data crossing boundaries

- Validate at the boundary, then trust internally. Parse, don't validate: convert
  raw input into a rich internal type *once*, at the edge, so interior code never
  re-checks (`parse_order(json) -> Order`, not `is_valid(dict)` sprinkled everywhere).
- Serialization formats are contracts: additive changes only (new optional fields);
  renames and type changes are breaking and need versioning or expand/contract.
- Timestamps in UTC, ISO-8601 at boundaries, timezone math only at display.
  Money in integer minor units or decimal — never floats. These two rules are cheap
  to follow and catastrophically expensive to retrofit.
