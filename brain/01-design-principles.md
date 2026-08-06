# 01 — Design principles: modules, coupling, and abstraction

## Deep modules

The best modules have **simple interfaces hiding substantial functionality**.
Interface cost is paid by every caller forever; implementation cost is paid once.
A module with a 3-method interface doing real work (e.g., a Unix file descriptor,
a good ORM session, `requests.get`) is deep. A module whose interface is as complex
as its implementation ("shallow") adds indirection without hiding anything — it makes
the system *worse* than inlining the code.

Practical tests:
- Can a caller use this without reading its implementation? If not, the abstraction leaks.
- Does the interface expose the *what* while hiding the *how*? Config knobs that mirror
  internal structure are the how leaking out.
- **Failure mode:** depth-worship producing god-modules. A module should be deep, but
  it must still have *one* responsibility. Deep ≠ broad.

## Information hiding (Parnas, still undefeated)

Decompose systems around **what is likely to change**, not around the steps of the
processing flow. Each module should encapsulate one design decision — a data format,
an algorithm choice, a third-party dependency — so that when the decision changes,
exactly one module changes. Flowchart-based decomposition (step1/, step2/, step3/)
guarantees every requirement change cuts across every module.

## Coupling and cohesion — the actual fundamentals

All design advice reduces to: **minimize coupling between modules, maximize cohesion
within them.** Ranked from acceptable to toxic, the coupling kinds:

1. Data coupling (pass values) — fine.
2. Interface coupling (depend on a small contract) — fine, this is the goal.
3. Control coupling (flags that tell a callee *how* to behave) — smell; split the function.
4. Temporal coupling (must call A before B, nothing enforces it) — bug factory; make
   illegal states unrepresentable (constructor does A, or B takes A's result as input).
5. Shared mutable state — the most expensive coupling there is; isolate it ruthlessly.
6. Hidden coupling (two modules must agree but nothing connects them — duplicated
   constants, parallel switch statements, matching string keys) — the worst, because
   the compiler can't see it and neither can the reader.

## DRY, correctly scoped

Duplicate *knowledge* is the problem — two places encoding the same business rule.
Duplicate *text* is often fine. Two similar-looking functions serving different
masters (different reasons to change) should stay separate; merging them couples
their futures. **Rule of thumb: tolerate duplication until the third occurrence,
then abstract — and abstract over the knowledge, not the syntax.** The wrong
abstraction is far more expensive than duplication, because it attracts parameters
and conditionals that entangle every caller.

## Composition over inheritance — with teeth

Implementation inheritance couples the child to the parent's *implementation* across
the weakest interface in programming (protected state + override points). Prefer:
interfaces/protocols for polymorphism, composition for reuse, and functions for logic.
Inheritance is acceptable for genuine is-a with a stable, designed-for-extension base
(frameworks do this well); it is wrong as a code-sharing device.

## Errors: define them out of existence, then handle the rest at the edge

- First choice: design APIs so error cases can't occur (deleting a missing file is a
  no-op; slicing out of range clamps; idempotent operations retry safely).
- Second choice: handle errors where there's enough context to *do something* —
  usually far up the stack, at a request/job boundary. Mid-level code that catches,
  logs, and re-throws (or worse, swallows) adds noise and hides failures.
- Exceptions/Result types are for *expected* failure paths; crashes are for bugs.
  Blurring the two (catching everything, defensive `except: pass`) turns bugs into
  silent corruption. **Crash early, crash loudly, log the context.**

## Make illegal states unrepresentable

Enforce invariants with the type system / data model, not with comments and runtime
checks scattered everywhere: non-nullable fields, enums instead of stringly-typed
state, constructors that can't produce invalid objects, database constraints for
business invariants. Every invariant enforced structurally is a category of bug
that no longer needs testing, reviewing, or debugging.

## General-purpose leaning, specialized implementation

When designing an interface, ask "what is the simplest interface covering all my
*current* needs?" — the answer is usually slightly more general and much simpler than
the special-case version (one `insert(text)` beats `insertNewline()` + `insertTab()` +
`insertChar()`). But do not *implement* generality nobody asked for; speculative
flexibility (plugin systems, config-driven everything, premature interfaces with one
implementation) is complexity paid now for value that usually never arrives (YAGNI).
