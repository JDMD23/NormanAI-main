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

## Cross-cutting failure design

The architecture-level questions that separate toy systems from production systems:
- What happens when each dependency is down or slow? (Timeouts on *every* network
  call, budgeted; retries only on idempotent operations, with backoff and jitter;
  circuit breaking where fan-out amplifies failure.)
- What is the blast radius of a bad deploy? (Small, rolled-back automatically.)
- Can every operation be traced end-to-end? (Correlation IDs from edge to store.)
- What is idempotent and what is not — and is that written down at the boundary?
