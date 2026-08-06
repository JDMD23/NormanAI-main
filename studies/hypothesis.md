# Study: hypothesis

- **Repo:** https://github.com/HypothesisWorks/hypothesis
- **Studied:** 2026-08-06 at commit `deb4d49` (v6.165.2)
- **What it is:** The property-based testing library for Python. You describe the
  space of valid inputs ("a list of integers"); Hypothesis generates cases,
  including edge cases you didn't think of, and when a test fails it reports the
  *simplest* failing input. ~436 Python modules, a decade mature, plus a Rust
  component and an unusually good set of engineering-culture guides.
- **Why it was worth studying:** Two payloads — a **profound testing idea** that
  upgrades the brain's whole testing chapter, and the best-articulated
  **maintainer engineering culture** of any repo studied, written down as guides.

## The core idea: choice sequences (Conjecture)

Hypothesis's engine represents any randomized test case as "the sequence of
*choices* made while producing it" — each choice a typed primitive (int, float,
bool, string, bytes) drawn from `ConjectureData`. The insight cascades:

- **One representation, two superpowers.** Because a test case *is* a choice
  sequence, (a) any sequence can be replayed, stored, and mutated, and (b)
  *shrinking* becomes a generic operation: find the **shortlex-minimal** choice
  sequence that still fails (shortest, then smallest left-to-right). The failing
  input a user sees — `[0]`, not `[8, -3, 41, 0, 17]` — is the minimal
  counterexample, which is what makes property-based tests debuggable rather than
  just alarming.
- **Model at the right level.** They moved the representation from raw PRNG bytes
  to the *typed choice sequence* "which shrinks far better because we no longer
  have to reason about the encoding of each value into bytes." Choosing the
  abstraction level at which the hard operation (shrinking) is easy is the whole
  game — the same move as LangGraph adopting BSP so durability falls out
  (studies/langgraph.md): pick the representation that makes your defining
  operation a generic function.

The brain-level lesson: **generate-then-shrink beats example-based testing for
whole categories of code.** Example tests check the cases you imagined; property
tests check a described *space* and hand back the minimal witness of any bug in
it. This is not a niche technique — it's the missing half of brain/03's testing
doctrine.

## The other payload: engineering culture, written down

The `guides/` directory is the most valuable maintainer-culture documentation in
24 studies. Highlights that become brain material:

- **Orthogonality as a hard release rule.** "For all minor or patch releases we
  enforce a hard and fast rule that they contain no more than **one user-visible
  change**." The tell for a too-big change: "if the RELEASE.rst uses the words
  'additionally' or needs bullet points, it is likely too large." One PR, one
  user-visible change, one release note — the cleanest operational definition of
  atomic change control seen anywhere (brain/03 "never mix refactor and behavior
  change," generalized and enforced at the release boundary).

- **Two review questions that subsume a checklist.** "(1) Is this change going to
  make users' lives worse? (2) Is this change going to make the maintainers'
  lives worse?" The entire review handbook hangs off keeping both answers "no,"
  with "neutral is good enough — the author is presumed to have a good reason."
  A review rubric grounded in *who bears the cost*, not in style.

- **API house style with teeth.** "*Absolutely no subclassing as part of the
  public API*." "Complexity should not be pushed onto the user — an easy-to-use
  API is more important than a simple implementation." "When writing extras
  modules, consistency with Hypothesis trumps consistency with the library you're
  integrating with." A written, opinionated API aesthetic that new strategies
  (and third-party extensions, explicitly invited to follow it) must match —
  conceptual integrity as a documented, enforced artifact (brain/01, made
  cultural).

- **Backwards compatibility outranks the style guide.** The style doc says so
  outright: existing APIs that predate the style stay as they are; "backwards
  compatibility is much more important than conformance to the style." Rules that
  name what overrides them (brain/00: a principle without its limits is dogma).

## What else stands out

- **Dogfooding the philosophy internally** — Conjecture's "single source of truth
  for what an example should look like" means every choice sequence is a valid
  test input by construction, so the generator and the shrinker share one model
  (no drift between "what we generate" and "what we shrink").
- **A newcomer-facing internals guide** tied to a specific contribution on-ramp
  (writing shrink passes) — lowering bus-factor deliberately by teaching the
  scariest subsystem, the antidote to brain/08's knowledge-silo anti-pattern.
- **Polyglot where it pays** — a Rust component for the performance-critical core
  alongside the Python API, spending an innovation token exactly where the
  hot path justifies it (brain/07).

## Questionable calls and tradeoffs

- **Conceptual weight.** Property-based testing asks users to think in spaces and
  invariants, not examples — a real learning curve, and tests can be slower and
  occasionally flaky at the seams (a strategy that rarely generates a
  precondition-violating case). The payoff is finding bugs example tests can't;
  the cost is honest.
- **Shrinking is a deep, subtle subsystem** — the guides admit the internals are
  "rudimentary" to document and hard to onboard into; the minimal-counterexample
  magic has real maintenance cost concentrated in few heads (mitigated by the
  outreach program, not eliminated).
- **Nondeterminism managed, not banished** — reproducibility relies on the
  database of failing examples and seeds; a property suite is a different
  operational animal than deterministic unit tests (worth knowing before adopting
  wholesale).

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Property-based testing (describe the input space, generate, shrink to the minimal counterexample) is the missing half of a testing strategy | Conjecture / `@given` | Pure logic, parsers, serializers, data structures, invariants; less so for I/O-heavy glue |
| Pick the representation at which your defining operation is a generic function | typed choice sequence → generic shrinking | Any engine with a hard core operation (shrinking, diffing, replay, undo) |
| Enforce one user-visible change per release; "additionally" in the changelog means it's too big | orthogonality rule | Any versioned library; the sharpest atomic-change definition |
| Ground code review in two questions: does this hurt users? does this hurt maintainers? | review handbook | Any review culture; simpler and better than a style checklist |
| Write the API house style down, opinionated, with what overrides it (backwards compat) | api-style.rst | Any library wanting conceptual integrity across many contributors |
| Deliberately teach the scariest subsystem to newcomers to lower bus factor | internals.rst + shrink-pass outreach | Any project with a knowledge silo |

## Brain updates made

- `brain/03-code-quality.md`: added property-based testing as a first-class part
  of the testing pyramid (describe-the-space + generate + shrink-to-minimal), and
  the "one user-visible change per release" orthogonality rule to the change-
  control guidance.
- `brain/07-decision-frameworks.md`: added the two-question review lens (does it
  make users' / maintainers' lives worse?) as a review-prioritization tool.
