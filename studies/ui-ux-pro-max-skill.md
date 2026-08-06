# Study: ui-ux-pro-max-skill

- **Repo:** https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **Studied:** 2026-08-06 at commit `abb7f2f`
- **What it is:** A UI/UX "design intelligence" skill: 14 curated CSV databases
  (84 styles, 192 palettes, 74 font pairings, 98 UX guidelines, motion presets,
  chart guidance, 22 stack-specific guides) fronted by a zero-dependency BM25
  search engine and a design-system generator, distributed to 20 agent platforms
  via template configs plus an npm CLI.
- **Why it was worth studying:** A genre none of the previous eight repos covered:
  the **queryable-knowledge skill** — what to do when the domain knowledge is far
  bigger than any context budget.

## Architecture at a glance

```
src/ui-ux-pro-max/            # single source of truth
  data/*.csv                  # the actual product: curated design knowledge
  scripts/core.py             # BM25 + regex hybrid search, stdlib only (464 lines)
  scripts/design_system.py    # reasoning engine over the data (1,479 lines)
  scripts/validate_data.py    # data lint
  scripts/tests/              # tests for search + design-system mode
  templates/platforms/*.json  # 20 platform configs → generated install targets
.claude/skills/ui-ux-pro-max/ # hand-authored SKILL.md + CI-enforced data/script mirror
cli/                          # npm installer; sync-assets.mjs maintains mirrors
```

## The headline: knowledge as a queryable database, not prose

This takes the anthropic-skills progressive-disclosure model to its logical end.
Tier 3 there was "scripts execute without loading"; here the scripts' *purpose* is
retrieval: the agent runs `search.py "<query>" --domain style` and gets the 3 most
relevant rows — never the 84-style corpus. It is RAG-in-a-skill with deliberately
boring machinery: BM25 + regex over CSV, stdlib only, no embeddings, no network,
runs anywhere Python runs. The context ledger: metadata tier ~100 words; SKILL.md
tier is a **priority-ordered triage index** (10 rule categories, accessibility
first/CRITICAL → charts last/LOW, each with must-haves and anti-patterns inline);
everything else arrives 3 ranked rows at a time.

The division of labor lands exactly on the brain/09 rule — prose for judgment
(the workflow and priority table), references for rare depth (full rule text),
scripts for the deterministic part — with the addition that here *retrieval
itself* is the deterministic part.

## What else this repo does exceptionally well

1. **The data is treated as the product.** CSVs have real schemas (a style row
   carries light/dark suitability, performance and accessibility grades, framework
   compatibility, implementation checklist, design-token variables); a
   `validate_data.py` lints them; the search engine and design-system generator
   have tests. Content repos studied earlier (agency-agents, ECC) lint *format*;
   this one also validates *data shape*.

2. **Sync rules with an ADR-grade reason attached.** No symlinks anywhere,
   because "git-on-Windows checks them out as plain text files pointing at a
   path, which silently breaks the skill" — the **third independent sighting** of
   symlinks failing in distribution (Codex install cache in Pocock's ADR-0002,
   Windows checkout here). Mirrors are real committed files kept in sync by a
   script and **enforced by a CI workflow** — the checked-duplication pattern
   (agency-agents) with the reason documented where the rule lives.

3. **Environment detection with the failure mode named.** Stack routing reads
   `package.json` / `pubspec.yaml` / `*.xcodeproj` / `composer.json`; if nothing
   is detectable, *ask* — "**Never assume a stack** — a hardcoded default silently
   misroutes every recommendation." Detect, then ask, never guess: the correct
   default for any environment-dependent agent routing.

4. **Taste parameterized as bounded dials.** `--variance`, `--motion`,
   `--density`, each 1–10 with documented semantics (variance biases style
   selection minimal→bold; density flips spacing tokens spacious→dashboard).
   Subjective aesthetics exposed as small named knobs — the same API move as
   LangGraph's `Durability` enum, applied to design taste. Unset dials change
   nothing (good default hygiene).

5. **Robustness details that betray real-world testing.** Full-path invocation
   ("do not assume a working directory"), `python` → `python3` → `py -3`
   fallbacks, Windows notes, priority rules for what to check first when time is
   short. This skill has clearly met many hostile environments.

## Questionable calls and tradeoffs

- **The recurring gap: no outcome evals.** Search machinery is tested; whether
  agents produce *better UIs* with this skill is unmeasured (tier-3 by the
  brain/09 hierarchy, like every non-superpowers repo studied). With 84 styles ×
  192 palettes of listicle-shaped data, curation quality is the product's ceiling
  and it's unverified.
- **Marketing numbers in load-bearing places.** Badge counts ("161 reasoning
  rules", "84 UI styles") and the same figures inside the SKILL.md description —
  hand-maintained counts adjacent to generated data, the ECC drift trap unless
  `validate_data.py` checks them (unclear). Low stakes, familiar smell.
- **BM25 keyword matching has synonym blindness** ("calming" won't match a query
  for "muted pastel wellness" unless keywords were curated in). The zero-dependency
  constraint makes this a reasonable trade — but it shifts the burden onto keyword
  columns, which become another curated surface to maintain.
- **`design_system.py` at 1,479 lines** is drifting toward the mega-module smell
  (brain/03); the reasoning engine would split naturally along its domains.
- **The version-bump commit at HEAD** (`fix: bump skill.json version`) beside a
  `.releaserc.json` suggests the release pipeline still needs manual shepherding —
  minor, common, worth automating away.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| When curated knowledge exceeds the context budget, ship it as structured data + a boring local search tool; the in-context tier becomes a priority-ordered triage index | data/ + core.py + SKILL.md table | Any large-corpus skill (design systems, API catalogs, compliance rules); below ~a few hundred rows, references suffice |
| Zero-dependency retrieval (BM25/regex, stdlib) beats infrastructure-heavy RAG for distributable skills | core.py | Portability > recall for installed tooling; accept synonym blindness, curate keywords |
| Validate the data, not just the format — schemas, lint script, tests over the corpus | validate_data.py, tests/ | Any skill/catalog where data is the product |
| Environment-dependent routing: detect from artifacts, ask when unknown, never default silently | stack detection rule | Agent tools that branch on project type/stack |
| Expose subjective quality dimensions as bounded named dials with documented semantics and no-op defaults | --variance/--motion/--density | Parameterizing taste in any generator |
| Symlinks do not survive distribution (3rd sighting: Codex cache, Windows checkout) — use CI-checked mirrors | Sync Rules in CLAUDE.md | Any multi-target repo layout |

## Brain updates made

- `brain/09-agentic-engineering.md`: extended the knowledge-delta section with the
  queryable-knowledge pattern (structured data + boring local search when the
  corpus exceeds context; triage index in the loaded tier) and the
  detect-then-ask rule for environment-dependent routing.
