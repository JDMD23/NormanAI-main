# 02 — Architecture: systems, boundaries, and structure

## Architecture = the decisions that are expensive to reverse

Most code can be rewritten in an afternoon; architecture is the set of choices you
*can't* cheaply undo: the data model, the module boundaries, the persistence strategy,
the sync/async split, the deployment topology, the language/runtime. Spend design
effort proportional to reversal cost. Everything easily reversible should be decided
quickly and revisited freely.

## The dependency rule

Dependencies must point from volatile toward stable, from mechanism toward policy:
**business logic at the center, I/O at the edges.** The domain core should not import
the web framework, the ORM entities, or the vendor SDK — those live behind interfaces
the core defines. This is the shared insight of hexagonal / clean / onion architecture;
the layer-naming religion doesn't matter, the direction of the arrows does.

Practical form, even in a small codebase:
- **Functional core, imperative shell.** Pure logic (decisions, transformations,
  validation) in plain functions operating on plain data; side effects (DB, HTTP,
  filesystem, clock, randomness) pushed to a thin outer shell. This single move makes
  testing trivial, reasoning local, and refactors safe — it's the highest-ROI
  architectural pattern that exists for small-to-mid projects.

For a cross-cutting capability that libraries *emit* but the application *owns*
(instrumentation, logging, plugin hooks), the proven structure is a **thin stable
API with working no-op defaults, plus a heavy swappable implementation selected at
the composition root** (OpenTelemetry's api/sdk split — studies/opentelemetry-python.md).
Libraries code against the API only; with no implementation installed the calls
are cheap no-ops, so a library can adopt the capability at *zero cost and zero
config imposed on its users*, and the application picks the real backend (or none)
without the library ever depending on it. This is dependency inversion plus
"return a safe default" (brain/05) fused into a distribution strategy — the only
shape that lets library code carry optional cross-cutting hooks honestly.

**Failure mode:** ceremony worship. Four-layer lasagna with pass-through mappers at
every boundary, interfaces with one implementation, DTO↔entity↔model conversions for
a CRUD app. If a boundary never varies independently, it shouldn't exist as a
boundary. Add layers when a second implementation, a second client, or a real seam
requirement shows up.

## Monolith first — with internal boundaries

Distributed systems trade every hard problem for a harder one: function calls become
network calls (partial failure, latency, retries), transactions become sagas,
debugging becomes archaeology across services. Microservices are a solution to an
*organizational* scaling problem (many teams needing independent deploys), not a
technical virtue. Default: **a modular monolith** — one deployable, strict internal
module boundaries (enforced by imports/packaging, not by convention), one database
with schema-per-module discipline if needed. Extract a service only when a specific
module demonstrably needs independent scaling, independent deploys, or a different
runtime — and extract *that module*, along its existing boundary.

## Data model outlives code

The database schema and the shapes of data crossing boundaries are the most permanent
artifacts in any system — application code churns around them. Consequences:
- Design the data model deliberately; review schema changes with more care than code.
- Normalize until it hurts, denormalize only with a measured reason.
- Never let two components share a database schema as their contract unless they
  deploy together — shared schemas are the tightest coupling in distributed systems.
- Migrations must be forward-only, reversible in effect (expand → migrate → contract),
  and deployable independently of the code that needs them.

## Adopt formal models; inherit their theorems

When the domain has a mature formal model — BSP/Pregel for stepwise parallel
workflows, actors for isolated concurrency, event sourcing for auditable state,
state machines for lifecycle logic — adopting it wholesale buys properties you'd
otherwise engineer feature by feature. LangGraph is the clean demonstration
(studies/langgraph.md): because execution advances in supersteps with writes
invisible until the step boundary, durable checkpointing, safe human-in-the-loop
interruption, replay/forking, and race-free parallelism all *fall out* of the
model rather than being bolted on. Ad-hoc control flow gives each of those
features a hand-built, bug-prone implementation — if it gets them at all. The
price is the model's constraints (BSP's lockstep latency, actors' no-shared-state);
take the deal when the guarantees matter more than the constraints, and design the
unit of atomicity before the features that will need it.

## State is the hard part; minimize what owns it

Every stateful component (DB, cache, queue, in-memory session, singleton) is a source
of failure modes, ordering bugs, and operational burden. Architectural quality is
strongly correlated with **how few places own mutable state and how explicit their
ownership is**. Stateless services in front of one well-managed store beat clever
state distributed across components. Caches are a common self-inflicted wound:
every cache is a second copy of the truth with an invalidation problem — add one only
after measuring, and prefer request-scoped or TTL-only caches over invalidation logic.

## Sync vs async

Synchronous request/response is easier to reason about, debug, and trace — default
to it. Introduce queues/events when you genuinely need: buffering under bursty load,
decoupled availability (producer must succeed while consumer is down), fan-out to
many consumers, or work that outlives the request. Event-driven architecture as a
*default* style produces systems where nobody can answer "what happens when I do X"
without a distributed trace. If you adopt events: events carry facts (what happened),
not commands; consumers must be idempotent; and dead-letter handling is designed on
day one, not after the first silent data loss.

## Keep projections in sync with a reconcile loop

Any system with a **source of truth and a derived copy** (a datastore and a cache,
a DB and a search index, a real store and a Notion projection) needs a
**reconciler**, not just write-through hope (controller-runtime is the canonical
pattern — studies/controller-runtime.md). A reconciler **compares desired state
against observed state and acts to converge them** — idempotent, state-based (not
delta/event-based), correct from *any* starting point. Make it **level-triggered,
not edge-triggered**: events *trigger* a reconcile, but a *periodic re-converge*
(requeue-after) heals the events you missed — a dropped write, a crash, a manual
out-of-band edit. This is the antidote to the entire class of "the copy silently
drifted from the truth": you stop writing "on event X do Y" and start declaring
"make the copy match the source," run on a sweep. Requeue-after doubles as tiered
cadence (hot objects reconcile sooner). Business invariants fit the same mold —
"a Prospect must be in the outreach list" is a reconcile invariant, not a scripted
transition: the state machine decides what the state *should* be, the reconciler
makes the world *match*.

## Durable execution: separate the plan from its side effects

For long-running, multi-step, crash-prone work (a scheduled enrichment session, a
multi-stage pipeline), the durable-execution model (Temporal —
studies/temporal.md) is the functional-core/imperative-shell split enforced by a
runtime: a **workflow** is deterministic orchestration that is *replayed from an
event history* to survive any crash (no clock/random/I/O inside it); an
**activity** is each side effect (API call, fetch, LLM call) — recorded in
history, retried by the runtime under a declared policy, idempotent because
delivery is at-least-once. Two rules transfer even if you never run the engine:
put every side effect behind a recorded, retryable boundary so the *whole run*
resumes from where it died rather than restarting; and let one layer own retries
(declared policy per step, with non-retryable error types) instead of nesting
retry loops. Scope honesty (brain/00): adopt the *model* freely; buy the *server*
only when the operational cost is paid for by real need — a lighter write-ahead
outbox often gives most of the benefit.

## Cross-cutting failure design

The architecture-level questions that separate toy systems from production systems:
- What happens when each dependency is down or slow? Wrap every external
  dependency in the **resilience stack** (resilience4j is the reference taxonomy —
  studies/resilience4j.md), composed in order: **RateLimiter** (respect the
  dependency's quota as declared policy, not ad-hoc sleeps) → **TimeLimiter**
  (a hard deadline on *every* call) → **CircuitBreaker** (closed→open→half-open:
  fail fast when a dependency's failure rate spikes, stop hammering the dead
  service, probe to recover) → **Retry** (bounded, backoff+jitter, idempotent ops
  only, *inside* the breaker's budget) → **Fallback** (return last-known or
  `Unknown` — never a fabricated value). **Bulkhead** each dependency's concurrency
  so one slow/dead source can't consume all resources and sink the whole job.
  Retry handles blips; the circuit breaker handles outages; the bulkhead contains
  the blast radius — you need all three, not just retry.
- What is the blast radius of a bad deploy? (Small, rolled-back automatically.)
- Can every operation be traced end-to-end? (Correlation IDs from edge to store.)
- What is idempotent and what is not — and is that written down at the boundary?

## Model the assets, not the tasks

For any system computing derived values, write the **asset graph** — what should exist and what
it depends on — before the execution order. A task view shows *ordering*; an asset view shows
*lineage*, and only the second makes the fatal case visible: **a node with no producer.** In a
task-shaped system a value that nothing computes is invisible until something reads a null;
on an asset graph it is a gap you can see (studies/dagster.md; Norman BL1, where a scoring
component consumed `funding_velocity` for four days and no code path in any commit produced it).

Derive the graph from the code — dependencies from signatures — so the diagram and the
implementation cannot disagree. Adopt the *model* at ten nodes; adopt the *platform* never,
unless the node count justifies it.
