# Study: taste-skill

- **Repo:** https://github.com/Leonxlnx/taste-skill
- **Studied:** 2026-08-06 at commit `e988add`
- **What it is:** "Anti-slop" frontend skills: a 1,206-line flagship design skill
  plus style variants (minimalist/brutalist/soft), image-generation skills for
  reference boards, an image-to-code skill, and a `research/` directory
  investigating LLM output failures. 58 files, sponsor-funded, Agent Skills
  compatible.
- **Why it was worth studying:** The direct counterpart to ui-ux-pro-max — same
  domain, opposite bet (dense judgment prose vs. curated data + search) — and
  the source of two authoring patterns none of the previous thirteen had.

## Architecture at a glance

```
skills/taste-skill/        the flagship: brief inference → dials → system map → rules
skills/{minimalist,brutalist,soft}-skill/   style presets as separate small skills
skills/imagegen-frontend-{web,mobile}/      reference-board generation (design-first pipeline)
skills/image-to-code-skill/                 frames → implementation
skills/taste-skill-v1/     previous version, retained
research/laziness/         root causes / remediation / findings on incomplete LLM output
```

## The two new patterns

### 1. Anti-default discipline: name the model's priors to escape them

The skill maintains an explicit list of what the model *will produce by default*
and forbids it: "AI-purple gradients, centered hero over dark mesh, three equal
feature cards, generic glassmorphism, infinite-loop micro-animations,
Inter + slate-900. These are the LLM defaults. Reach past them deliberately."

This is a third species of knowledge-delta (brain/09 had two): footguns document
where the model's *beliefs* diverge from reality; rationalization tables document
its *behavior* under pressure; this documents its **output priors** — the mode
the model collapses to when unconstrained. Slop is mode collapse, and escaping a
default requires *naming* it. The pattern generalizes far beyond design: default
test shapes, default API scaffolds, default README prose all have the same
signature.

### 2. Declared interpretation before action: the one-line "Design Read"

Step zero is inference, not generation: read the brief's signals (page kind,
vibe words, references, audience, "quiet constraints" — accessibility/regulated
contexts that *override* aesthetics), then **state a one-line interpretation
before any code**: "Reading this as: B2B SaaS landing for technical buyers, with
a Linear-style minimalist language, leaning toward Tailwind + Geist + restrained
motion." If genuinely ambiguous, ask **exactly one** clarifying question — never
a question dump; if confidently inferable, declare and proceed.

This is the lightweight sibling of frontier interrogation (brain/09, Pocock):
grilling suits multi-session design work; a declared read suits single-shot
generation — the user sees the interpretation early enough to redirect at the
cost of one line, and "the audience picks the aesthetic, not your taste" pins
whose preferences govern.

## What else it does well

- **Reach for the official system; don't invent CSS.** A brief→package mapping
  (Fluent, Material 3, Carbon, Polaris, GOV.UK Frontend, USWDS, shadcn,
  Bootstrap: "boring, fast, works") with the rule "do not invent CSS for things
  that have an official package; do not pretend an aesthetic trend is an
  official system." Brain/07's buy-over-build and boring-tech encoded for
  design — including the compliance cases where the official system is
  "legally / regulatorily expected."
- **Dial inference, not dial interrogation.** The same three dials as
  ui-ux-pro-max (variance/motion/density, 1–10 — convergent evolution in this
  niche), but *inferred* from brief signals via mapping tables with per-use-case
  presets, overridable conversationally. Plus a small gem of naming discipline:
  "never invent aliases like `LAYOUT_VARIANCE` or `ANIM_LEVEL`" — pinning
  internal variable names so the model can't drift terminology mid-generation
  (brain/03's one-name-per-concept, applied to the model's own working memory).
- **Contextual rules, declared as such.** "Every rule below is contextual. None
  of it fires automatically. First read the brief, then pull only what fits" —
  an honest register between superpowers' Iron Laws and mere suggestions,
  correct for taste (where hard rules would *be* the slop).
- **A research directory as evidence trail.** `research/laziness/` documents
  root causes, remediation techniques, and experiment data for incomplete LLM
  output — the study-then-write discipline (our own studies/ pattern) applied
  by a skill author to the failure mode their skills target.
- **Version retention** (`taste-skill-v1` kept alongside) and style presets as
  separate small skills rather than flags on the big one.

## Questionable calls and tradeoffs

- **A 1,206-line always-loaded body.** The flagship blows past the <500-line
  guidance (anthropic-skills) with no reference split and no retrieval layer —
  the exact problem ui-ux-pro-max's triage-index + search solved in the same
  domain. The two repos are complementary halves: judgment prose (here) over
  queryable data (there) would beat either alone.
- **Sponsor real estate above the fold** — the README leads with sponsors before
  the product; commit history includes sponsor-layout work. Sustainable OSS
  funding, but the reader pays first.
- **No outcome evals** (the ecosystem constant) — research/ shows the instinct
  exists; it hasn't been pointed at the skills' own effect.
- **skill.sh** is a bash associative-array lookup that echoes a path — a
  charmingly minimal installer, but it does nothing the directory listing
  doesn't.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Maintain an anti-default list: name the model's collapsed-mode outputs explicitly and forbid them | Anti-Default Discipline section | Any generation domain with recognizable slop (design, tests, docs, READMEs) |
| For single-shot tasks: declare a one-line interpretation before acting; one clarifying question max, only on genuine divergence | the Design Read | Lightweight sibling of frontier interrogation; use grilling for multi-session work |
| Encode buy-over-build as a brief→official-package map, including regulatory cases | Section 2 mapping | Design systems, and by analogy any domain with official SDKs |
| Pin internal variable names to stop mid-generation terminology drift | "never invent aliases" | Long prompts with cross-references |
| Declare rules' firing mode honestly: contextual vs automatic | "none of it fires automatically" | The register between Iron Laws and suggestions |

## Brain updates made

- `brain/09-agentic-engineering.md`: added the **output-prior delta** (anti-default
  lists) as the third knowledge-delta species, and the **declared-interpretation**
  pattern beside frontier interrogation in the shared-language section.
