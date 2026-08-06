# Study: gstack

- **Repo:** https://github.com/garrytan/gstack
- **Studied:** 2026-08-06 at commit `a325940`
- **What it is:** Garry Tan's "open source software factory": 23 role-based
  workflow skills (CEO/eng/design plan reviews, code review, QA, security audit,
  ship/deploy) + 8 power tools, built around a persistent-browser daemon, a
  companion memory system (gbrain), model-specific overlays, team distribution
  with auto-update, and 287 test files. 1,177 files; a 912KB CHANGELOG testifying
  to daily production use.
- **Why it was worth studying:** The most engineering-dense agent-tooling repo of
  the ten — several genuinely novel mechanisms — plus an explicit philosophical
  challenge to this brain's economics ("Boil the Ocean") that deserves honest
  engagement rather than dismissal.

## Architecture at a glance

```
<skill-name>/SKILL.md      # 30+ top-level skill dirs; frontmatter is a real schema
browse/                    # the hard part: persistent Chromium daemon + CLI
  (compiled Bun binary ⇄ localhost HTTP ⇄ CDP; state file; 30min idle timeout)
model-overlays/            # per-model behavior patches: claude.md, gpt.md, gemini.md…
test/                      # 287 test files incl. Windows paths, security pins
ETHOS.md                   # philosophy, injected into every workflow skill preamble
ARCHITECTURE.md            # 32KB of *why*, with failure history per decision
setup / bin/               # install, team mode, hourly throttled auto-update
```

## Novel mechanisms (four firsts across ten studies)

1. **Declarative context assembly.** Skill frontmatter carries a `gbrain` block of
   *context queries* — filesystem globs and memory-list filters with sort/limit
   and a `render_as` heading — so `/plan-ceo-review` declares "pull the last 5
   CEO plans for this repo, the last 3 design docs, recent review activity" and
   the runtime assembles that context before the skill runs. Context construction
   (brain/09's "construct, don't inherit") expressed as versioned, reviewable
   *data* instead of imperative prose. This is the pattern the other nine repos
   didn't have.

2. **Model overlays with inheritance.** Per-model behavioral patch files —
   Claude gets todo-discipline nudges, Gemini gets conciseness constraints,
   GPT-5.4 gets `{{INHERIT:gpt}}` plus an anti-verbosity protocol. The insight:
   harness-portable skills still need *model-specific* quirk correction, and it
   belongs in composable overlay files, not forked skill bodies. Nobody else
   studied separates the two concerns.

3. **Least-privilege tool allowlists per skill.** `allowed-tools:` in frontmatter
   scopes each skill to what it needs (a plan review gets Read/Grep/WebSearch,
   not Edit). The security principle brain/06 applies to services, applied to
   skills — only repo of the ten that does it.

4. **Fleet distribution with silent auto-update.** Team mode: no vendored files,
   session-start update check throttled to once/hour, network-failure-safe,
   `required` vs `optional` enforcement per repo. Skills managed like a deployed
   artifact, not a copied file — beyond every marketplace model studied.

## What else it does exceptionally well

- **The browser daemon is real systems engineering, documented as decisions.**
  ARCHITECTURE.md justifies the daemon model with numbers (cold start 3-5s/call
  vs ~100-200ms warm; login/cookie state survives), atomic state-file writes
  (tmp+rename, 0600), health-check liveness *chosen over PID checks with the
  Windows failure explained*, random-port selection *with the failure history of
  the old port-scan approach*, and version auto-restart that "prevents the stale
  binary class of bugs entirely." Even the security section narrates its own past
  vulnerability (the `/health` token leak that forced the dual-listener design).
  This is ADR-quality writing at document scale — decisions with reasons,
  alternatives, and scars.
- **Role reviews as orthogonal lenses in a pipeline.** CEO review (rethink the
  product), eng review (lock architecture), design review (catch AI slop), CSO
  (OWASP + STRIDE), QA (real browser) — agency-agents' persona idea, but
  *process-integrated*: the roles are stages with distinct rubrics, not a
  browsable cast. Perspective-diverse review as workflow structure.
- **Tooling is tested like a product.** 287 test files, including Windows path
  handling and dependency security pins; generated skill docs from a template
  (`AUTO-GENERATED — do not edit`) with a regeneration command — the
  checked-generation pattern done right.
- **Boring-tech justifications with limits stated.** The "Why Bun" section gives
  three concrete reasons (compiled single binary for `~/.claude/skills/`
  installs, native SQLite for cookie decryption without gyp, native TS) and then
  *deflates its own choice*: "Bun's startup speed is nice but not the reason."

## The philosophical challenge: "Boil the Ocean"

ETHOS.md argues the brain's economics are stale: "'Don't boil the ocean' was
right when engineering time was the bottleneck. That era is over." Always prefer
the complete implementation (all edge cases, full error paths, tests now — "the
cheapest lake"); compression ratios run 3x (research) to 100x (boilerplate).

The honest resolution — adopted into the brain — is to split the cost term:

- **Write-cost collapsed.** Decisions that hinged on *effort to produce* — skipping
  tests, deferring error paths, shipping the 90% version of the task at hand —
  should flip toward completeness. gstack is right, and "that would take too
  long" is increasingly a stale reflex when the delta is minutes.
- **Carry-cost did not collapse.** Every line still must be read, reviewed,
  operated, secured, and evolved — by humans and by future agents with finite
  context. Speculative abstractions, extra dependencies, and unrequested features
  cost what they always cost. YAGNI survives; it was never really about typing
  effort.

So: **completeness of the task at hand — yes, boil it. Expansion of scope or
abstraction — the old rules stand.** The ethos itself half-concedes this
("genuinely unrelated work… flag as separate scope"); its table conspicuously
shows architecture/design compressing least (5x) — judgment remains the
bottleneck, which is the brain's founding premise.

## Questionable calls and tradeoffs

- **The productivity marketing is load-bearing.** The README leads with 810×
  claims; to its credit there's a methodology doc with a reproduction script
  (measurement discipline most such claims lack), but "logical LOC" as the
  numerator still measures output, not outcomes — brain/06 would ask for DORA-
  shaped evidence instead. The claims sell the repo; the engineering carries it.
- **Monolithic flat layout at the root** — 40+ top-level skill directories beside
  core docs; discoverable via CLAUDE.md but the repo root is a wall. Bucket
  lifecycle (Pocock) would help.
- **59KB CLAUDE.md / 64KB BROWSER.md / 144KB TODOS.md** — the always-loaded tier
  is enormous by anthropic-skills' economics (<500 lines ideal); mitigated partly
  by preamble tiers, but this is a context-budget bet the spec authors would
  question.
- **No behavioral evals** (the recurring gap) — 287 tests cover the *tooling*;
  the skills' effect on output quality is attested by one very public power
  user's shipping record, which is evidence of a kind, but not transferable
  verification.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Declare context assembly as data: queries (glob/filter/sort/limit) in skill frontmatter, assembled at invocation | gbrain context_queries | Any skill system with persistent artifacts; needs a runtime that honors it |
| Separate model-specific quirk correction into overlay files with inheritance; keep skill bodies model-neutral | model-overlays/ | Multi-model harnesses; prevents forked skill bodies |
| Scope each skill to a tool allowlist (least privilege) | allowed-tools frontmatter | Any skill/agent definition format that supports it |
| Distribute team tooling as a managed artifact: silent throttled auto-update, required/optional enforcement | setup --team | Team-shared agent config; beats vendored copies and manual upgrades |
| Long-lived daemon + thin CLI for stateful expensive resources (browser); atomic state file, health-check liveness, version auto-restart | browse/ architecture | Browsers, emulators, DB sandboxes for agents; overkill for stateless tools |
| Write architecture docs as decisions-with-scars: numbers, rejected alternatives, and the failure that forced each design | ARCHITECTURE.md | Everywhere; this is the ADR discipline at document scale |
| Split AI-era economics: write-cost collapsed (be complete on the task), carry-cost didn't (YAGNI stands on scope) | ETHOS.md vs brain/00 | The build-vs-skip judgment everywhere |

## Brain updates made

- `brain/09-agentic-engineering.md`: added **"The economics update: write-cost
  collapsed, carry-cost didn't"**; added declarative context assembly, model
  overlays, and per-skill tool allowlists to the skill-composition section.
