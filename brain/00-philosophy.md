# 00 — Philosophy: what elite engineering actually is

Everything else in this brain derives from a small number of load-bearing beliefs.

## Complexity is the enemy, and it is incremental

Systems don't die from one bad decision. They die from hundreds of small ones — each
"just one special case," "just one more parameter," "just one dependency." Complexity
compounds silently until change becomes dangerous and slow. The elite engineer's core
skill is not writing clever code; it is **noticing and refusing incremental complexity**
that isn't paid for by a real requirement.

Two forms of complexity (Ousterhout's framing, validated everywhere):
- **Change amplification** — a simple change requires edits in many places.
- **Cognitive load** — a reader must hold too much in their head to work safely.
Every design decision should be evaluated against both.

## Working code is not the goal — evolvable code is

Almost all software cost is downstream of the first version: reading, modifying,
debugging, operating. Optimizing for "it works now" over "it can change later" is
borrowing at a terrible interest rate. Corollary: **the reader outranks the writer.**
Code is read tens of times more than it's written; when writing convenience conflicts
with reading clarity, clarity wins.

## Simple is not easy

"Easy" is near at hand — the familiar library, the copy-paste, the quick hack.
"Simple" is unentangled — one concern per construct, one reason to change per module.
Easy choices often create complected systems (state braided with logic, config braided
with code). Choosing simple over easy is frequently more work *today* and vastly less
work *forever after*. (Hickey's distinction; it holds up.)

## Design it twice

The first design that comes to mind is rarely the best, because it's the most *available*
one, not the most *fitting* one. For any non-trivial decision, sketch at least two
genuinely different approaches and compare them against the actual forces (change
patterns, failure modes, team, timeline). Even ten minutes of this routinely saves weeks.

## Judgment beats rules

Every principle in this brain has a domain of validity. DRY taken too far creates
coupling between things that merely *look* similar. Abstraction taken too far creates
indirection nobody can follow. Testing taken too far ossifies implementation details.
The mark of a senior engineer is not knowing the rules — it's knowing **when each rule
stops applying**. Every doc here states failure modes for its own advice; if a principle
is presented without its limits, distrust it.

## Scope honesty

Most systems are not FAANG-scale and never will be. Elite engineering is matching the
solution to the *actual* problem: a monolith with clean internal boundaries beats
microservices for almost every team under ~50 engineers; SQLite or Postgres beats a
distributed database for almost every dataset under a terabyte; a cron job beats a
queue for almost every workload under thousands of events per minute. Choosing the
boring, smaller thing is usually the sophisticated move, not the naive one.

## Feedback loops are the real product

The speed at which a team can go from idea → running code → observed result governs
everything else. Slow tests, slow CI, slow deploys, and slow local setup are not
inconveniences — they are compounding taxes on every future decision. When reviewing
a project, the health of its feedback loops is diagnostic priority #1.
