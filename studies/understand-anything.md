# Study: Understand-Anything

- **Repo:** https://github.com/Egonex-AI/Understand-Anything
- **Studied:** 2026-08-06 at commit `fe8c5bc`
- **What it is:** A Claude Code plugin that turns a codebase into an interactive
  knowledge graph via a multi-agent pipeline (scanner → file/architecture/domain
  analyzers → assembler → reviewer agents → tour builder), rendered in a React
  Flow dashboard with structural and business-domain views, guided tours, and a
  shareable viewer. TypeScript monorepo, hybrid LLM + tree-sitter (WASM) analysis.
- **Why it was worth studying:** The direct pair to graphify (studies/graphify.md)
  — same problem, opposite architecture (agent-native LLM pipeline vs
  deterministic-first CLI) — and the source of two pipeline-engineering patterns
  new to the collection.

## Architecture at a glance

```
understand-anything-plugin/
  agents/        project-scanner, file-analyzer, architecture-analyzer,
                 domain-analyzer, assemble-reviewer, graph-reviewer, tour-builder…
  skills/        /understand (+ per-language guidance files, + locale files),
                 /understand-dashboard, -chat, -onboard, -explain, -domain…
  packages/core       shared engine: types, schema, persistence, search, tours
  packages/dashboard  React Flow + Zustand dashboard (graph-first, code viewer)
  packages/viewer     npx-servable viewer for committed graphs (share w/o Claude)
```

Agents communicate through `.ua/intermediate/` files on disk — "not returned to
context" — cleaned up after graph assembly.

## The two new patterns

### 1. Reviewer agents mechanize their own checks

`graph-reviewer` is a QA agent whose **first instruction is to write and execute
a deterministic validation script** covering every schema check (16 node types,
ID-prefix conventions, required fields, enum values, tag format), output JSON to
a temp file — with a precise exit-code contract: "exit 0 even if validation finds
issues (the exit code signals the script ran, not that the graph is valid);
exit 1 only if the script itself crashes." Phase 2 is judgment: review the
script's findings and render approve/reject with justification.

This is brain/09's enforcement hierarchy applied *inside a single agent role*:
don't ask an LLM to eyeball 3,000 nodes for schema conformance — have it author
the checker, run it, and spend judgment only on the residue. The pipeline runs
two such reviewers (assemble-reviewer, graph-reviewer): adversarial verification
of LLM-produced artifacts, with the mechanical majority mechanized.

### 2. The filesystem as the pipeline bus

Analyzer agents write intermediate results to `.ua/intermediate/` on disk rather
than returning them into the orchestrator's context, and the intermediates are
deleted after assembly. This is the data-plane completion of two existing brain
principles: construct-don't-inherit (control plane) and the ledger (recovery).
For multi-agent pipelines producing large artifacts, **context carries
coordination; disk carries data** — the orchestrator's window stays small no
matter how big the analysis gets.

## What else it does well

- **Typed graph schema built for LLM producers.** 16 node types with ID-prefix
  conventions (`file:`, `function:`, `domain:`…), complexity enums, tag format
  rules ("lowercase and hyphenated"), summary constraints ("not just the
  filename") — the schema is designed so that machine validation can catch the
  ways LLMs actually cut corners. Schema validation runs again at dashboard load
  with an error banner.
- **A CLAUDE.md written from scars, with receipts.** The agent `model` field is
  *omitted* because Claude Code's `inherit` keyword crashed opencode with
  `ProviderModelNotFoundError` (issue #167 cited) — the portability rule:
  cross-harness frontmatter should omit optional fields rather than use any
  platform's keywords. WASM tree-sitter over native (darwin/arm64 + Node 24
  bindings failure). Browser-safe subpath exports so the dashboard can't pull
  Node modules. Every gotcha has its story attached.
- **First sighting of skill i18n** — `/understand` ships locale files
  (en/ja/ko/ru/zh/zh-TW) and per-language extraction guidance files
  (typescript.md, python.md, ruby.md…) — the model-overlay pattern (gstack)
  applied to human languages and target languages respectively.
- **The shareable-artifact move.** `packages/viewer` serves a committed graph
  via `npx <release-url>` with no Claude Code required — the analysis output is
  a document teammates can open, not a session-locked artifact. (Same instinct
  as graphify's graph.html, taken further.)
- **Performance testing for the UI** — a fake-graph generator
  (default 3,000 nodes) for layout benchmarking, plus large-repo benchmark
  tests with a report schema.

## Questionable calls and tradeoffs

- **No provenance labels.** LLM-written summaries and relationships carry no
  extracted/inferred/ambiguous marking — the graphify lesson this pipeline
  needs most, given *more* of its graph is LLM-authored. The reviewers check
  schema conformance, not epistemic grounding.
- **Cost and reproducibility.** A multi-agent LLM pass over every file is
  expensive and non-deterministic where graphify's AST pass is free and
  reproducible; the hybrid (tree-sitter for structure) mitigates but the
  semantic layer re-rolls each run. The two tools bracket the tradeoff:
  richer semantics per dollar vs. reproducible structure for free.
- **19 test files for a monorepo this size** is thin relative to its own
  ambitions (core engine + dashboard + viewer + hooks + installers), though
  what exists is well-aimed (schema, hooks, install, benchmarks).
- **Two data directories** (`.ua/` vs legacy `.understand-anything/`) with
  resolution rules threaded through "all bundled scripts and core code" —
  migration debt acknowledged and handled, but every consumer pays the branch.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| QA agents should write and run their own deterministic checkers first, then judge the residue — with exit codes meaning "script ran," not "content valid" | graph-reviewer phases | Any LLM review of structured artifacts |
| In agent pipelines: context carries coordination, disk carries data — intermediates to files, cleaned after assembly | .ua/intermediate/ | Multi-agent analysis producing large artifacts |
| Design schemas for LLM producers: ID prefixes, enums, format rules aimed at the corners LLMs cut | 16-type node schema | Any LLM-generated structured output |
| Cross-harness frontmatter: omit optional fields; never rely on one platform's keywords | the `inherit` scar, issue #167 | Multi-harness skills/agents |
| Ship analysis outputs as standalone shareable artifacts (npx viewer over committed JSON) | packages/viewer | Team tooling; the graph is a document, not a session |

## Brain updates made

- `brain/09-agentic-engineering.md`: added reviewer-mechanization (QA agents
  author and run deterministic checkers, judge the residue) to the enforcement
  section, and "context carries coordination, disk carries data" to the
  durable-state section.
