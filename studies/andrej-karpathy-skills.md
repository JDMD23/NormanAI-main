# Study: andrej-karpathy-skills

- **Repo:** https://github.com/multica-ai/andrej-karpathy-skills
- **Studied:** 2026-08-06 at commit `2c60614`
- **What it is:** A single CLAUDE.md (~90 lines, mirrored as a Claude skill and a
  Cursor rule) distilling Andrej Karpathy's public observations of LLM coding
  failure modes into four behavioral principles. Nine files total.
- **Why it was worth studying:** The minimal end of the agent-config spectrum after
  superpowers (methodology) and ECC (platform) — and a test of whether tiny,
  content-only repos can still teach the brain something. This one does.

## Architecture at a glance

There is none to speak of — the same four principles in three formats (CLAUDE.md,
`skills/karpathy-guidelines/SKILL.md`, `.cursor/rules/*.mdc`) plus README/examples.
The design is the *content*: four principles, each derived from a named failure mode
in Karpathy's post:

| Principle | Failure mode it targets |
|---|---|
| Think Before Coding | Silent wrong assumptions; unmanaged confusion; no pushback |
| Simplicity First | Overcomplication; bloated abstractions; 1000 lines where 100 do |
| Surgical Changes | Orthogonal edits; touching code/comments outside the task |
| Goal-Driven Execution | No verifiable success criteria; can't loop independently |

## What this repo does exceptionally well

1. **"Surgical Changes" is the best statement of agent diff-discipline I've seen.**
   "Touch only what you must. Clean up only your own mess." — remove the orphans
   *your* change created; don't delete pre-existing dead code, mention it; match
   existing style even when you'd do it differently; and the test: **every changed
   line should trace directly to the user's request.** This names a real gap in the
   brain: brain/03's boy-scout rule is correct for human owners but wrong as an
   agent default, because unrequested "improvements" inflate the diff a human must
   review and erode trust in the whole change.

2. **Goal transformation: imperative → verifiable.** "Add validation" → "write tests
   for invalid inputs, then make them pass"; "fix the bug" → "write a test that
   reproduces it, then make it pass." One rewrite rule that compresses TDD and
   verification into task *phrasing* — and the stated payoff is exactly right:
   "strong success criteria let you loop independently; weak criteria require
   constant clarification." Autonomy is downstream of verifiability.

3. **It states its own tradeoff and its own success metric.** Up front: "These
   guidelines bias toward caution over speed. For trivial tasks, use judgment."
   At the end: "working if: fewer unnecessary changes in diffs, fewer rewrites due
   to overcomplication, clarifying questions before implementation rather than
   after mistakes." Guidance that declares its cost and its observable test is
   following brain/00's own rule ("a principle without its limits is dogma") —
   rare in this genre.

4. **Value density.** ~90 lines loaded into context, no infrastructure, no
   dependencies, nothing speculative — the repo practices its own Simplicity First.
   Highest value-per-token of the three repos studied so far.

## Questionable calls and tradeoffs

- **Untested prose — tier 3 of the enforcement hierarchy.** By the standards of
  brain/09 (built from superpowers/ECC): no baseline runs, no evals, no
  rationalization defenses, no enforcement. The success criteria are stated but
  never measured. Ironically, "push back when warranted" and "stop when confused"
  are precisely the judgment-shaped rules that superpowers' testing showed fold
  under pressure without hardening. The content is good; nothing proves it works.
- **The same knowledge in three hand-synced files.** CLAUDE.md, SKILL.md, and the
  Cursor rule duplicate the full text — ECC's drift trap at miniature scale, and
  drift is already visible: the README's install commands still point at
  `forrestchang/...` while the repo lives at `multica-ai/...` (fork lineage leaking).
- **Mild description leak.** The skill description enumerates the principles
  ("avoid overcomplication, make surgical changes, surface assumptions...") —
  borderline against the superpowers rule that descriptions state only *when* to
  use. Principle names are safer than workflow steps, but the risk (agents acting
  on the summary, skipping the body) is the same in kind.

## The three-repo spectrum

| | karpathy-skills | superpowers | ECC |
|---|---|---|---|
| Form | Single-file patch | Curated methodology | Platform + runtime |
| Mechanism | Plain prose | Eval-tested prose | Deterministic hooks |
| Cost to adopt | ~90 lines of context | Plugin + workflow buy-in | Full install, learning curve |
| Verifiability | None | Behavioral evals | CI + enforcement |

Read as a maturity ladder: start here (patch the worst failure modes for free),
graduate to eval-tested workflows when the prose has to hold under pressure,
add deterministic enforcement when a rule is worth mechanizing. Each step buys
reliability with infrastructure.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Agent default is surgical: every changed line traces to the request; clean up only your own orphans | Surgical Changes section | Agent edits & code review of agent diffs; humans who own the code may boy-scout (brain/03) |
| Transform imperative tasks into verifiable goals before starting — autonomy is downstream of verifiability | Goal transformation table | Task briefs, plan steps, delegation prompts |
| Guidance should declare its own tradeoff and its observable success criteria | Header + "working if" footer | Any behavioral doc, including this brain |
| A well-chosen 90 lines beats an unfocused 9,000 — but unverified prose is a hypothesis, not a control | Whole repo vs. its lack of evals | Calibrates investment: patch → eval → enforce |

## Brain updates made

- `brain/09-agentic-engineering.md`: added **"Diff discipline: agents are guests in
  the codebase"** (surgical-changes rule, its tension with the boy-scout rule, and
  the ownership-based resolution) and the imperative→verifiable goal transformation
  under autonomy calibration.
- `brain/03-code-quality.md`: one-line caveat added to the refactoring section —
  the boy-scout rule presumes ownership and review trust; agents and drive-by
  contributors should default to surgical changes (cross-ref brain/09).
