# Study: JustHireMe

- **Repo:** https://github.com/vasu-devs/JustHireMe
- **Studied:** 2026-08-06 at commit `5e41b25`
- **What it is:** A local-first desktop job-intelligence workbench (solo
  maintainer, AGPL + commercial dual license): Tauri 2 shell + React front end,
  Python 3.13 FastAPI sidecar, scraper adapters for job sources, a deterministic
  ranking engine with GraphRAG evidence, local CRM, and document generation.
  All data local: SQLite + Kuzu graph + LanceDB vectors + ONNX embeddings.
- **Why it was worth studying:** The first ordinary *end-user product* in the
  collection — and it turns out to contain the best evaluation harness of all
  seventeen repos, plus a causal lesson about *why* it could have one.

## Architecture at a glance

```
Tauri shell (port + API token bridge)
  → FastAPI sidecar: discovery/sources (adapter per job source, base.py port)
                     → lead quality gate → SQLite CRM
                     ranking/ (criteria/ plug-ins → scoring_engine → optional LLM)
                     generation/ (documents, outreach) → local PDFs
  → local data: SQLite + Kuzu (profile graph) + LanceDB (vectors) + ONNX embeddings
llm/providers: keyless (Ollama, Claude Code CLI, Codex CLI) + 15 keyed providers
First-run runtime pack: heavy deps (Playwright, vectors, ONNX model) downloaded
once, content-versioned, verified, cached — installer ~100MB instead of ~700MB
```

## The headline: an eval harness that shames the ecosystem

`backend/evals/` makes ranking quality "a **measured, regression-guarded number**
instead of an opinion" — their words, and they earn them:

- **Labeled cases through the real engine.** `(profile, job) → expected band`
  JSONL cases scored by the production `score_job_lead`, across *six domains*
  (tech, healthcare, trades, business, cross-field mismatches, seniority
  mismatches) — deliberately testing beyond the maintainer's own field.
- **Two CI gates:** invariants must hold, aggregate accuracy ≥ floor.
  `invariant: true` marks **product guarantees** whose single failure fails CI
  outright ("in-field non-tech never floored; cross-field mismatches stay
  capped") — the difference between a metric and a promise, encoded.
- **Directional, fear-driven expectations.** For in-field cases you fear the
  score *dropping* → set `min` with generous `max`; for mismatch cases you fear
  *creep* → set `max` + `capped: true`. Plus calibration guidance: read the
  current number, then set bounds "with a few points of headroom so benign
  tuning doesn't trip it but a real regression does." Asymmetric regression
  bounds — more sophisticated than most ML teams' practice, documented in a
  README.
- **Deterministic in CI.** The semantic criterion *self-disables* when the
  vector store is absent, so scores are stable — reproducibility designed in,
  not hoped for.
- The stated motivation nails the epistemics: "Before this harness there was no
  way to tell an improvement from a lucky change."

**The causal lesson** — why this repo has evals when fifteen others don't: the
scoring core is a **deterministic weighted rubric with hard caps**, with LLM
evaluation as an optional layer on top. You can only regression-test what is
deterministic. Putting the judgment in a rubric instead of a prompt is what
*makes quality measurable* — the brain/09 enforcement hierarchy (mechanize the
mechanical) doesn't just improve reliability; it is the precondition for having
a number to guard.

## What else it does well

- **Keyless-first LLM access, including agent CLIs as providers.** Ollama,
  *Claude Code CLI, and Codex CLI* serve as zero-configuration LLM backends —
  reusing the agent runtime the user already has as the app's inference
  provider. Zero-key onboarding for an AI app is rare; this is the cleverest
  route to it I've seen. Embeddings likewise degrade: local ONNX model → hashing
  fallback — a capability ladder, never a hard wall.
- **Ports and adapters, plainly.** `discovery/sources/` is an adapter per job
  source over `base.py`; `ranking/criteria/` is a typed `Criterion` Protocol
  with frozen specs and pluggable criteria (evidence, learning-curve,
  logistics…). Brain/01 shapes, unceremonious and correct.
- **Distribution engineering for heavy local-first apps.** The first-run
  runtime pack (content-versioned, verified, cached; app updates reuse it)
  solves the 700MB-installer problem honestly, and releases are CI-built from
  `v*` tags for three OSes.
- **The tombstone skill.** `skills/justhireme/SKILL.md` is a *deprecated
  placeholder that actively disclaims itself*: "The previous contents were
  stale, request-specific notes and should not constrain future agents…
  inspect the current codebase instead." Stale agent guidance is worse than
  none — misleading with authority — and rather than deleting (dangling refs)
  or leaving rot, they shipped an explicit do-not-use marker. Small, new
  pattern; the first repo of seventeen to handle guidance *decay* head-on.
- **116 backend test files** beside the evals — seams, routers, generation,
  ranking — a serious floor for a solo product.

## Questionable calls and tradeoffs

- **Scraping legal surface.** Adapters target job boards, HN, Reddit, X…
  ToS/robots posture isn't visible at the survey level; for an AGPL product with
  commercial licensing this is the risk the roadmap should name (open question,
  not accusation).
- **Marketing weight in the repo**: star-history at the top of the README,
  badge walls, `Posts/`, `Designs/`, and a `website/` inside the product repo —
  the solo-maintainer gravity (ECC pattern) at small scale.
- **Dual license + CLA** is coherent for sustainability but adds contributor
  friction the CONTRIBUTING docs must keep earning.
- Kuzu + LanceDB + SQLite is three embedded stores for one desktop app —
  justified by graph-proof + semantic-search features, but the brain/04
  question ("one boring store until measured need") deserves its ADR.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Deterministic rubric cores make quality measurable; LLM layers stay optional — mechanization is the *precondition* for regression-guarded numbers | scoring_engine + evals | Any scoring/matching/routing system tempted to "just ask the LLM" |
| Eval cases carry directional, fear-driven bounds with headroom; invariant cases encode product guarantees that fail CI alone | evals README | Heuristic/ML systems generally; the calibration prose is worth copying verbatim |
| Make CI evals deterministic by having non-deterministic criteria self-disable | semantic self-disable | Hybrid deterministic/ML pipelines |
| Agent CLIs the user already runs are legitimate zero-key LLM providers | llm/providers | Local-first AI apps |
| Ship heavy runtimes as a content-versioned first-run pack, not installer payload | runtime pack | Desktop AI apps with model/browser deps |
| Tombstone stale agent guidance explicitly — deprecated docs that disclaim themselves beat deletion and beat rot | the disabled skill | Any aging skill/CLAUDE.md content |

## Brain updates made

- `brain/03-code-quality.md`: added the scoring-system eval pattern to the
  testing section — labeled cases through the real engine, invariant gates,
  directional bounds with headroom, deterministic-in-CI — with the causal note
  that deterministic cores are what make quality measurable.
- `brain/09-agentic-engineering.md`: one line on guidance decay — tombstone
  stale skills/docs with an explicit self-disclaimer rather than deleting or
  letting them mislead.
