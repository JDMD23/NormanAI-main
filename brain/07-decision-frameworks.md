# 07 — Decision frameworks: how to choose

Principles tell you what good looks like; frameworks tell you what to do when goods
conflict. These are the reusable decision procedures.

## The universal tradeoff procedure

For any significant decision:
1. **Name the forces.** What actually varies here — load? team size? change frequency?
   correctness stakes? Most bad decisions optimize for a force that isn't present
   ("web scale" for 100 users) or ignore one that is (compliance, on-call reality).
2. **Sketch two+ genuinely different options** (see 00 — design it twice). Include
   "do nothing / do the boring thing" as a real option, not a strawman.
3. **Compare against the forces, not against vibes.** A table of options × forces,
   three lines each, is usually enough.
4. **Classify reversibility.** Reversible → decide fast, try it, keep the exit.
   Irreversible (data model, public API, vendor lock) → slow down, prototype, decide
   with evidence.
5. **Write it down** — an ADR (architecture decision record): context, options,
   choice, consequences. Ten minutes of writing saves the next person a week of
   archaeology and prevents relitigating. A repo with zero ADRs and non-obvious
   architecture is a repo where knowledge lives in one person's head.
   The trigger gate (all three required, else skip): the decision is **hard to
   reverse**, would be **surprising without context**, and was a **real trade-off**
   among genuine alternatives. The best ADRs also record *tested* rejected
   alternatives with their observed failure, and the invariants the decision creates.

## Build vs buy vs adopt

- **Core vs context** (the only question that matters): does this capability
  differentiate the product? Core → own it. Context (auth, payments, email, search,
  monitoring) → buy/adopt the boring standard and move on.
- Adopting a dependency = marrying its maintenance, security surface, upgrade
  treadmill, and project health. Check: maintenance activity, issue responsiveness,
  your ability to read its source, exit cost. A 200-line utility you understand
  beats a 50k-line framework you use 2% of.
- The trap in both directions: NIH (rebuilding Postgres features in app code) and
  dependency-maximalism (leftpad syndrome; a dependency for every function). The
  test is total cost of ownership over 3 years, not initial effort.

## When to refactor vs rewrite vs leave alone

- **Leave alone:** ugly but stable, rarely-touched, well-isolated code. Ugliness
  only costs when read or changed. Don't polish corners nobody visits.
- **Refactor (default):** code that's touched often and hurts every time. Do it
  incrementally, preparatory-style (see 03), behind tests, never as a feature freeze.
- **Rewrite (rare, dangerous):** justified only when the *foundation* is wrong —
  wrong runtime, wrong data model, unsalvageable coupling — AND the system's behavior
  is well-understood (tests or unambiguous spec). Big-bang rewrites fail at
  spectacular rates because the old system encodes years of invisible requirements.
  If rewriting: strangler-fig — new system takes traffic slice by slice, old one
  keeps running, at no point is there a cliff-edge cutover. For a *library* with a
  regretted API, the production-proven form is rename-and-freeze: the old surface
  gets an explicit legacy name, stays installable with no new features, and lives
  beside the (much smaller) replacement while the ecosystem migrates — LangChain
  v1 shrank its flagship ~12x this way (see studies/langchain.md).

## Technical debt, honestly

Debt is a *deliberate* shortcut with known interest — logged, visible, scheduled.
Most "tech debt" is actually just cruft (unintentional bad code) or drift (the world
changed). Triage by interest rate, not by ugliness:
- High interest (slows every feature, causes incidents, blocks upgrades) → schedule
  now, alongside features, as first-class work.
- Low interest (ugly, isolated, stable) → log and ignore, guilt-free.
A standing ~10–20% capacity for debt/upgrades beats episodic "quality sprints,"
which arrive only after velocity has already collapsed.

## Optimization discipline

1. Don't, yet. 2. Measure — profile with real workloads; the bottleneck is never
where intuition says. 3. Fix the algorithm/query/N+1 before micro-optimizing.
4. Keep the fast path boring: most performance wins in typical systems are removing
accidental waste (chatty queries, missing indexes, serialization in loops,
sync-waiting on parallelizable I/O) — not clever code. Set a budget (p99 target)
so "fast enough" is defined and optimization has a stopping point.

When speed genuinely requires multiple implementations (SIMD tiers, native
extension + pure fallback, GPU/CPU), keep them behind one identical interface and
(a) **detect capability at runtime, dispatch best-first with graceful
fall-through** — try the fast path, silently degrade on failure, never *require*
the optimal artifact; (b) **give an env-var/config escape hatch to pin the tier**
for testing and reproduction; (c) treat the **fast path and its fallback as owing
each other identical results** — a fallback that returns different answers is a
correctness bug, not a slower path, so run one conformance suite against both.
(Reference: RapidFuzz — studies/rapidfuzz.md.)

## Reviewing changes: the two-cost question

A whole code-review rubric collapses into two questions (Hypothesis's review
handbook): **does this change make users' lives worse? does it make the
maintainers' lives worse?** Review is the collaborative work of getting both
answers to "no"; *neutral is good enough* — the author is presumed to have a good
reason, so a change need not make things better, only not-worse on both axes.
This grounds review in who bears the cost rather than in style checklists (style
is settled by tools — brain/03), and it correctly separates the two constituencies
a change can hurt. Pair it with orthogonality (one user-visible change per
release, brain/03) and most review process falls out.

## Choosing technologies

Innovation tokens: a team can afford *one or two* exciting choices; everything else
should be boring, proven, operable tech the team already knows (Postgres, the
mainstream framework, the standard queue). Novelty costs on-call knowledge, hiring,
ecosystem maturity, and Stack-Overflow-density. Spend the tokens where they
differentiate the product — never on plumbing.
