# Study: agency-agents ("The Agency")

- **Repo:** https://github.com/msitarzewski/agency-agents
- **Studied:** 2026-08-06 at commit `c89557f`
- **What it is:** A community-driven roster of 294 persona-styled agent files
  organized as a company (17 "divisions": engineering, design, healthcare, GIS,
  game-dev…), converted by script into 15+ tool formats, with a native desktop app
  for browsing/installing. Born from a Reddit thread; hundreds of community PRs.
- **Why it was worth studying:** A fifth genre — the *persona roster* — and the
  first community-scale content catalog studied that has actually engineered
  defenses against catalog decay. ECC showed the failure; this shows the fixes.

## Architecture at a glance

```
<division>/*.md        # 294 source agents: YAML frontmatter + persona + process
divisions.json         # catalog registry with CI-enforced consistency (see below)
scripts/convert.sh     # one source → integrations/<tool>/ for 15+ harnesses
integrations/          # committed, generated outputs (clearly labeled as outputs)
scripts/check-agent-originality.sh   # near-duplicate detector (CI-enforced)
scripts/lint-agents.sh # frontmatter + structure validation (CI)
.github/workflows/     # four checks: lint, divisions, tools, runbooks
```

Content model: each agent is a *character with a process* — identity/personality,
core mission, "Critical Rules," workflows, deliverables with code, success metrics.

## What this codebase does exceptionally well

1. **The originality gate is the best community-catalog defense I've seen.**
   `check-agent-originality.sh` exists because of a precisely-observed failure mode:
   find-replace "re-skins" of existing agents (swap a country or platform name) are
   "mergeable and well-formed — but they bloat the library with duplicates," and
   slip past human review. The detector compares every candidate against the whole
   roster using **entity-neutralized 8-word shingle overlap** — so a swapped proper
   noun can't hide the copy — and the script header documents its **calibration**:
   worst same-pair similarity in the existing library ~1.5%, median 0%, so the 20%
   warn / 40% fail thresholds carry a wide, *measured* safety margin. CI runs it on
   changed files; contributors run it locally. This is a semantic quality gate,
   mechanized (brain/09's enforcement hierarchy, applied to *content* contributions).

2. **Checked duplication where derivation is impractical.** `divisions.json`'s
   `_note` openly admits the division list exists in four places (the JSON, two bash
   arrays, CI path filters) — and instead of pretending otherwise, CI
   (`check-divisions.sh`) **fails the build when any copy disagrees**, including
   against the directories on disk. It even documents which directories are *not*
   divisions and why. This is the second-best answer to hidden coupling (brain/01)
   when a single source of truth can't feed every consumer: duplicate, but make
   drift impossible to merge. Directly the fix for ECC's three-conflicting-counts
   problem.

3. **Clean generation pipeline with an honest boundary.** One canonical markdown
   format; `convert.sh` writes tool-specific formats into `integrations/` ("this
   script never touches user config dirs — see install.sh for that"); install is a
   separate, interactive, auto-detecting step. Committed generated outputs are
   clearly labeled as outputs. Compare superpowers (per-harness adapter dirs
   maintained by hand) and ECC (sync scripts): source→generate→install as three
   explicit stages is the most disciplined multi-harness distribution of the five
   repos studied.

4. **The contribution bar asks for engineering, not vibes.** The PR checklist
   requires: real-scenario testing, concrete code/template examples, success
   metrics, step-by-step workflow, and an originality check — for what is
   essentially a prompt-content repo. And the content holds up better than the
   persona wrapper suggests: the Backend Architect agent says monolith-first with
   documented paths to scale, timeout budgets and idempotency on every external
   call, bulkheads and DLQs — technically sound, current judgment (it agrees with
   brain/02 point for point).

## Questionable calls and tradeoffs

- **The persona layer is unproven overhead.** "🧠 Your Identity & Memory — you
  remember successful architecture patterns…" — every agent spends tokens on
  identity theater (emoji, vibe lines, personality traits) whose behavioral value
  nobody has measured. Experience-priming may aid role adherence; nothing here
  tests it (no evals anywhere — tier-3 prose per brain/09). The durable engineering
  is in the *catalog machinery*, not the character sheets.
- **Unbounded domain breadth, softly gated.** Aging-Parent-Care-Companion, Economy
  Designer, GaussDB Expert… the ECC breadth question returns. The originality and
  lint gates resist *decay*, but nothing bounds *scope* — the bet is that the app's
  browse/install-per-agent model makes breadth free at use-time (you install only
  what you pick), which mostly holds and is a real difference from ECC's
  bulk-install model.
- **No routing layer in-session.** 294 agents, discovery by browsing the app or
  README ("activate Frontend Developer mode") — no ask-matt-style router mapping
  flows; agents don't compose or reference each other. It's a cast, not a system:
  each agent is a monolith (76–600 lines) rather than compositions over primitives
  (the mattpocock lesson unapplied).
- **An 81KB README** as the primary human catalog — the app exists partly because
  the README stopped scaling.

## Where this sits among the five

The genre axis now has: behavioral patch (karpathy) / composable toolkit (Pocock) /
methodology (superpowers) / platform (ECC) / **content catalog at community scale
(this)**. Its unique contribution is governance: it takes ECC's failure mode
(community-fed catalog decay) and answers it with mechanized gates — originality
detection, checked duplication, format lint — rather than either superpowers'
closed door or ECC's open floodgate.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Community content catalogs need *semantic* duplication gates, not just format lint — re-skins are well-formed | check-agent-originality.sh rationale | Any shared prompt/skill/agent library accepting PRs |
| Calibrate quality thresholds against the existing corpus and document the calibration in the tool | "worst pair ~1.5%, median 0%" header | Any lint/threshold you invent; uncalibrated thresholds are folklore |
| When one source of truth can't feed every consumer, duplicate *and* CI-check agreement — drift that can't merge is drift that doesn't happen | divisions.json `_note` + check-divisions.sh | Fallback for brain/01 hidden coupling; derivation still preferred |
| Multi-target distribution = three explicit stages: canonical source → generated outputs (committed, labeled) → separate installer | convert.sh / integrations/ / install.sh | Any artifact shipped to N harness formats |
| Per-item install beats bulk install for broad catalogs — breadth is only free if users take one item at a time | app model vs ECC bulk install | Catalog UX; changes what scope discipline you need |
| Persona framing is decoration until measured; put the engineering in the process sections and the gates | persona layer vs catalog machinery | Writing agent definitions anywhere |

## Brain updates made

- `brain/09-agentic-engineering.md`: extended the catalog section with the
  community-governance toolkit — semantic originality gates with corpus-calibrated
  thresholds, and CI-checked duplication as the fallback when single-source
  derivation is impractical.
- No other brain changes — the persona-genre observations and distribution
  pipeline are recorded here as evidence for existing principles (brain/01 hidden
  coupling, brain/09 enforcement hierarchy and catalog curation).
