# 03 — Code quality: the craft layer

## Naming is design

If a thing is hard to name, its boundaries are wrong — naming difficulty is a design
smell, not a vocabulary problem. Standards:
- Names say *what*, at the abstraction level of the caller (`retryBudgetExhausted`,
  not `checkFlag2`). Precision over brevity, brevity over ceremony.
- One name per concept, one concept per name — a codebase where `fetch`, `get`,
  `load`, and `retrieve` all mean the same thing (or worse, subtly different things)
  taxes every reader.
- Booleans read as assertions (`isExpired`, `hasAccess`); functions with side effects
  read as verbs; pure functions can read as nouns of their result.

## Comments explain what code cannot

Code shows *what* and *how*; comments exist for everything else: **why** (rationale,
rejected alternatives, links to the incident that motivated the weird branch),
**invariants and units** ("holds the lock", "milliseconds", "sorted, deduped"),
and **interface contracts** (what a caller must know without reading the body).
A comment restating the line below it is noise; a missing "why" on surprising code
is a landmine. If a function needs a paragraph explaining *how* it works internally,
refactor instead of documenting the confusion.

## Functions and shape

- A function does one thing at one abstraction level; mixing levels (business rule +
  byte fiddling in one body) is the main readability killer.
- Early returns / guard clauses over nested conditionals. Nesting depth is a direct
  measure of cognitive load.
- Parameter count > 3 usually means a missing type. Boolean parameters at call sites
  (`render(true, false)`) are unreadable — use enums or split the function.
- Length matters less than *coherence*: a 60-line function telling one linear story
  beats five 12-line fragments the reader must reassemble. Extract when there's a
  nameable, reusable concept — not to hit a line count.

## Tests: the pyramid is about feedback speed

- **Unit tests** on the functional core: fast, no I/O, test behavior through the
  public interface. These are the bulk.
- **Integration tests** on the seams that unit tests can't reach honestly: real DB
  queries, real serialization, real framework wiring. A few dozen, not thousands.
- **End-to-end**: a handful of smoke paths. E2E-heavy suites are slow, flaky, and
  pinpoint nothing — inverted pyramids are a top-3 cause of slow teams.
- **Property-based testing** is the missing half of example-based tests, not a
  niche: describe the *space* of valid inputs, let the tool generate cases
  (including edge cases you didn't imagine), and — the part that makes it
  debuggable — have it **shrink any failure to the minimal counterexample**
  (`[0]`, not `[8,-3,41,0,17]`). Highest value on pure logic, parsers,
  serializers, encoders/decoders, and anything with a round-trip or an invariant
  (`decode(encode(x)) == x`, `sorted` is idempotent). Weaker for I/O-heavy glue.
  (Evidence: studies/hypothesis.md.)

Quality bar for individual tests:
- Test *behavior*, not implementation. A refactor that preserves behavior should not
  break tests; if it does, the tests are coupled to internals and are now anti-refactor
  armor rather than a safety net. Mock at architectural boundaries (network, clock,
  filesystem), not at every internal class.
- Each test: one scenario, named as a statement of behavior
  (`expired_token_is_rejected`), arrange–act–assert visible at a glance.
- The failure message alone should tell you what broke.
- Flaky tests are P1 bugs: they train the team to ignore red, which destroys the
  entire value of the suite. Quarantine or fix same-day.
- Coverage is a *floor-finder*, not a target. 100% coverage of assertion-free tests
  is worthless; chasing the number produces exactly that.
- Scoring/ranking/matching systems get an **eval harness**, not just unit tests
  (JustHireMe is the reference: studies/justhireme.md): labeled cases run through
  the *real* engine; `invariant` cases encode product guarantees that fail CI on
  their own; expectations are **directional and fear-driven** — a `min` bound
  where the feared regression is a drop, a `max` (+ capped assertion) where it's
  creep — calibrated with a few points of headroom so benign tuning passes and
  real regressions trip. Non-deterministic criteria self-disable in CI so the
  number is stable. Precondition for all of it: a deterministic scoring core —
  judgment in a rubric is measurable; judgment in a prompt is an opinion.

## Refactoring is a continuous activity, not a project

The sustainable mode is the boy-scout rule plus **preparatory refactoring**: when a
change is hard, first refactor so the change becomes easy, then make the easy change —
as two separate commits. (The boy-scout rule presumes ownership and review trust:
AI agents and drive-by contributors should instead default to surgical, request-scoped
changes — see brain/09, "Diff discipline.") "Big refactor projects" that freeze features are usually a
symptom that continuous refactoring was skipped for years; they fail more often than
they succeed. Never mix refactoring and behavior change in one commit: it makes both
unreviewable. The strongest operational form of this (Hypothesis's release rule):
**one user-visible change per minor/patch release** — if the changelog entry needs
"additionally" or bullet points to be clear, the change is too big and should be
split. Atomic changes are atomically reviewable, revertable, and bisectable.

## Style is settled by tools, not people

Formatting, import order, and lint rules are decided once, enforced by formatter +
linter in CI, and never discussed in review again. Human review time is too expensive
to spend on anything a machine can check. Review attention goes to: correctness,
design, naming, tests, and "will I understand this in a year."
