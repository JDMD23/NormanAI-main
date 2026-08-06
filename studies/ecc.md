# Study: ECC (Everything Claude Code)

- **Repo:** https://github.com/affaan-m/ECC
- **Studied:** 2026-08-06 at commit `623f2c0`
- **What it is:** A single-maintainer "agent harness operating system": 281 skills,
  67 agents, 94 command shims, ~50 enforcement/observation hooks, a continuous-learning
  system, security scanning (AgentShield), and adapters for ~12 agent harnesses —
  MIT core plus a commercial GitHub App (ECC Pro).
- **Why it was worth studying:** The natural counterpart to superpowers
  (`studies/superpowers.md`): toolbox-platform vs curated methodology. Together they
  bracket the design space for agent-workflow systems.

## Architecture at a glance

```
skills/ (281)  agents/ (67)  commands/ (94, legacy shims)  rules/ (opt-in packs)
hooks/hooks.json          # ~21 hook registrations: enforcement + observation
scripts/ (234 files)      # the real runtime: dispatchers, doctor/repair, sync,
                          #   memory, orchestration, dashboards, release tooling
skills/continuous-learning-v2/   # instinct system: observe → score → evolve
src/llm/                  # a separate Python LLM-provider abstraction (scope creep)
ecc2/                     # "ECC 2.0" platform, in-tree, alpha
.claude/ .codex/ .cursor/ .gemini/ .zed/ ...   # per-harness adapters
tests/ (217 files)        # real infra tests: manifests, hooks, adapters, providers
```

Two products share one repo: a **content catalog** (skills/agents/rules — prose) and a
**runtime** (hooks + scripts — code). The runtime is the more interesting artifact.

## What this codebase does exceptionally well

1. **Deterministic enforcement instead of persuasion.** Where superpowers uses
   absolutist prose to hold discipline, ECC pushes rules into hooks that fire 100% of
   the time: `config-protection` *blocks* edits to linter/formatter configs ("steers
   agent to fix code instead of weakening configs"), `block-no-verify` stops
   `git commit --no-verify`, pre-bash dispatchers gate dangerous commands. Their own
   stated reason is the sharpest line in the repo: **"Skills are probabilistic — they
   fire ~50-80% of the time based on Claude's judgment. Hooks fire 100% of the time,
   deterministically."** Anything mechanically checkable gets a hook; prose is reserved
   for judgment.

2. **The instinct system (continuous-learning-v2) is a real learning architecture.**
   Hooks capture every tool call to an observations log; a cheap background model
   (Haiku) mines it for patterns (user corrections, error resolutions, repeated
   workflows); output is atomic "instincts" — one trigger, one action — each carrying
   a **confidence score (0.3–0.9)** that rises with repeated observation and falls on
   user correction. v2.1 adds **project scoping** to stop cross-project contamination
   (React habits stay in the React repo), with **promotion to global** only on
   evidence: same instinct in 2+ projects at ≥0.8 confidence. Evidence-weighted,
   scoped, decaying memory — this is the most thoughtful design for "agent that
   learns your preferences" I've seen in the wild.

3. **Operational product maturity.** `doctor`, `repair`, `list-installed`,
   `uninstall`, timestamped backups before sync, explicit "pick one install path,
   don't stack them" guidance, a troubleshooting doc, and an honest per-harness
   support matrix ("see support status before assuming feature parity"). 217 test
   files cover plugin manifests, hook behavior, and adapter compliance in CI. This is
   config-distribution treated as a real software product, with the failure modes
   (double-install, wiped setups, drifted caches) engineered for rather than wished away.

4. **Security is a first-class subsystem.** AgentShield scans prompts/hooks/MCP
   configs/permissions; CLAUDE.md opens with a prompt-injection defense baseline;
   gitleaks config, a security guide, and a supply-chain warning ("official sources
   only") acknowledging that agent-config repos are now a malware vector. Threat
   modeling for a category most competitors treat as inert markdown.

5. **Visible migration management.** 94 commands are explicitly parked in
   `legacy-command-shims/` while the project moves to a skills-first surface —
   labeled debt with a direction, not silent accretion (brain/07's expand/contract
   done in public).

## Questionable calls and tradeoffs

- **Unbounded catalog, no quality floor.** 281 skills spanning
  `carrier-relationship-management`, `cisco-ios-patterns`,
  `blender-motion-state-inspection`; SKILL.md lengths run 34–948 lines with wildly
  varying depth; thin entries are project-specific docs, not general skills — exactly
  what superpowers' contribution policy refuses ("domain-specific skills belong in
  their own plugin"). Breadth *is* the product's pitch, but nothing structural stops
  catalog decay, and with agents choosing among 281 descriptions, every low-quality
  entry taxes selection for all the others.
- **Documentation drift proves the coupling rule.** Three files state three different
  catalogs: README (67/281/94), SOUL.md (30/135/60), WORKING-CONTEXT.md (47/79/181).
  Counts hardcoded in prose are duplicated knowledge with no enforcement (brain/01,
  hidden coupling) — at this scale the drift is guaranteed, and a generated catalog
  (a `catalog.js` exists!) should be the only source of truth.
- **`hooks.json` embeds the same minified ~1KB root-resolver blob 21 times.** Likely
  forced by the plugin format (each hook entry must be self-contained before any
  script can resolve paths), but 21 hand-synced copies of nontrivial logic in JSON
  strings is a bug factory unless the file is generated — and nothing in-tree labels
  it as generated output.
- **Scope sprawl.** One repo contains the plugin, a Python LLM-provider layer
  (`src/llm` with five providers), a 41KB dashboard script at root, an in-tree alpha
  platform (`ecc2/`), a REPL, Discord tooling, and release-video automation. Classic
  single-maintainer gravity: everything lands where the maintainer lives. The cost is
  a 3,390-file repo where the load-bearing 10% is hard to find — the permanent
  prototype and god-module patterns (brain/08) at repo scale.
- **Three identifiers** (`affaan-m/ECC`, `ecc@ecc`, `ecc-universal`) with a
  documented explanation — a reasonable constraint-driven choice, but the docs spend
  real estate apologizing for it, which is the tell that the naming costs users.

## The pairing: ECC vs superpowers

The two repos are a controlled experiment in brain/01's deep-vs-shallow modules:

| | superpowers | ECC |
|---|---|---|
| Thesis | Curated methodology | Comprehensive platform |
| Skills | 14, eval-gated, domain skills refused | 281, breadth-first, everything accepted |
| Discipline | Persuasion (eval-tuned absolutist prose) | Determinism (hooks that block) |
| Quality gate | Behavioral evals per change | Infra tests; content mostly ungated |
| Conceptual integrity | One voice, one workflow | Many voices, many surfaces |

Neither is simply right: superpowers trusts the model where ECC trusts the harness;
superpowers stays coherent by refusing scope that ECC monetizes. The durable synthesis:
**enforce mechanically what can be enforced (ECC), eval-test the prose that remains
(superpowers), and curate the catalog like an API surface (superpowers) — while
engineering the distribution/ops layer like a product (ECC).**

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Prose instructions are probabilistic (~50-80% compliance); hooks are deterministic — mechanize every mechanically-checkable rule | hooks.json enforcement suite + their own v1→v2 rationale | Any agent workflow; prose remains for judgment calls |
| Block the shortcut, don't just forbid it — make violations impossible, and point the agent at the right fix | config-protection, block-no-verify | Same idea as DB constraints (brain/04): structural > exhortation |
| Learned preferences need: atomic units, confidence scores that decay/respond to correction, project scoping, and evidence thresholds for generalizing | instinct system v2.1 | Any "agent memory" design; global-by-default memory contaminates |
| A skill/prompt catalog is an API surface: unbounded, uncurated growth degrades selection for every entry | 281 skills, 34–948 line variance | Applies to any team's shared skill/prompt library |
| Facts stated in more than one doc will drift; generate catalogs and counts from source | README/SOUL/WORKING-CONTEXT triple mismatch | Universal; brain/01 hidden coupling, empirically confirmed |
| Config distribution is a product: doctor/repair/backup/uninstall and anti-double-install guards are the difference between a repo and a tool | scripts/, install docs | Anything users install into their environment |
| Agent-config repos are an attack surface: scan hooks/MCP/prompts, warn on unofficial mirrors | AgentShield, security guide | Adopting *anyone's* agent config — including repos I study |

## Brain updates made

- `brain/09-agentic-engineering.md`: added two sections — **"Enforce mechanically,
  persuade only where judgment lives"** (the determinism hierarchy: hook > eval-tested
  prose > plain prose) and **"Agent memory that learns"** (atomic, confidence-scored,
  project-scoped, evidence-promoted); extended the interface section with the
  catalog-curation lesson.
- `brain/08-antipatterns.md`: no edit — ECC's drift and sprawl are strong *evidence*
  for existing entries (#2, #9, hidden coupling), now citable via this study.
