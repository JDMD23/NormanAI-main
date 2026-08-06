# Study: graphify

- **Repo:** https://github.com/Graphify-Labs/graphify
- **Studied:** 2026-08-06 at commit `07b9143` (v0.9.34)
- **What it is:** A YC S26 company's open-source tool that maps a project (code,
  docs, PDFs, media) into a queryable knowledge graph: tree-sitter AST extraction
  for code (deterministic, local, $0 LLM), an LLM semantic pass for prose/media,
  NetworkX graph with community detection, interactive HTML/JSON/Obsidian export,
  an MCP server for querying, distributed as a skill across 15+ harnesses.
- **Why it was worth studying:** Two reasons. A new genre — the *generated project
  map* (curated data was ui-ux-pro-max; this is derived-from-source) — and, at
  last, the second repo of twelve with real measurement: a benchmark suite run
  with a rigor the rest of the ecosystem should copy.

## Architecture at a glance

```
detect() → extract() → build_graph() → cluster() → analyze() → report() → export()
```

Each stage is one function in one module, communicating via plain dicts and
NetworkX graphs — "no shared state, no side effects outside `graphify-out/`" —
with `validate.py` enforcing the extraction schema at the seam between extract
and build. Textbook functional core (brain/02), stated as a design rule in
ARCHITECTURE.md and visible in the module table.

## The two big findings

### 1. Epistemic provenance on derived knowledge

Every edge in the graph carries a confidence label:
- `EXTRACTED` — explicitly stated in source (an import, a direct call)
- `INFERRED` — a reasonable deduction (call-graph second pass, co-occurrence)
- `AMBIGUOUS` — uncertain; **flagged for human review in the report**

Generated knowledge that distinguishes *what was read* from *what was guessed* —
and routes the uncertain remainder to a human — is exactly what brain/04 demands of
derived data (provenance + invalidation story) applied to knowledge graphs, and
what most LLM-extraction pipelines skip. Paired with it: **deterministic-first
extraction economics** — everything an AST can yield is parsed by tree-sitter
(free, local, reproducible); the LLM is reserved for what genuinely needs
semantics (prose, PDFs, images). The brain/09 enforcement hierarchy ("mechanize
the mechanical") applied to knowledge extraction, with the bill to prove it:
"builds its index with zero LLM credits."

### 2. The benchmark standard the ecosystem is missing

BENCHMARKS.md is what ten of the twelve studied repos lack, done properly:
- **Competitors run inside the same harness** (mem0, supermemory, BM25, dense
  RAG as adapters) — same model, same token budgets, same grader.
- **Blind dual-judge validation** — a second independent judge, with agreement
  reported (90.6%, Cohen's kappa 0.81).
- **Cost as a first-class axis** — ingest dollars alongside accuracy ($1.40 vs
  supermemory's $15.67).
- **Losses reported honestly** — supermemory beats them on LOCOMO QA accuracy
  (49.7% vs 45.3%) and the doc says so, arguing cost-effectiveness instead of
  hiding the number.
- Dated, versioned, with the harness itself open.

Caveat: self-run benchmarks on one's own harness still aren't independent
replication — but this is the honest form of the exercise, and it sets the bar.

## What else it does well

- **A documented extension recipe.** "Adding a new language extractor" is five
  steps ending in "add a fixture and tests" — the seam is public, mechanical,
  and test-gated. Contributor-ready in a way none of the content catalogs are.
- **Security as a module with a threat model.** All external input flows through
  `security.py`: URL scheme validation with file:// redirect blocking, fetch
  size/timeout caps, output-path confinement to `graphify-out/`, label
  sanitization (control chars, length, HTML-escape). A tool that ingests
  arbitrary repos and URLs treating itself as an attack surface — matches the
  anthropic-skills symlink lesson, systematized.
- **Query instead of re-read.** The product thesis is brain/09's index-then-fetch
  taken further: build the index once (deterministically), then answer
  path/explain/neighborhood queries from the graph without re-reading files —
  with `benchmark.py` measuring corpus-vs-subgraph token savings per query.
- **Pure unit tests, one file per module, no network, no fs side effects outside
  tmp_path** — stated and structured.

## Questionable calls and tradeoffs

- **The package is going wide fast.** ~50 modules in one flat package:
  per-platform skill files (15 `skill-*.md` variants) live *inside* the Python
  package next to `pg_introspect.py`, `google_workspace.py`, `transcribe.py`,
  `wiki.py`, `prs.py` — ingestion frontiers and distribution artifacts mixed
  with the core pipeline. The clean 7-stage architecture is real, but the
  "map everything" ambition is accreting satellites around it (brain/08 #9
  watch item; the pipeline deserves a `core/` boundary before this doubles).
- **Open-core funnel in the OSS repo** — `always_on/` and the cloud pitch are
  the business (disclosed, fine), but they blur what the standalone tool is vs
  the trial of the product.
- **Graph freshness is the unsolved half.** A generated map is derived data;
  `watch.py` writes change flags, but the README's own pitch ("always-on,
  updating in the background") concedes the OSS tool's graph goes stale between
  runs — the invalidation story lives in the paid product.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Label derived knowledge by provenance: extracted vs inferred vs ambiguous, and route ambiguous to humans | edge confidence labels | Any LLM-extraction pipeline; cheap and epistemically honest |
| Extract deterministically wherever a parser exists; spend LLM only on genuine semantics | tree-sitter for code, $0 build | Knowledge graphs, indexing, migration tooling |
| Benchmark like graphify: competitors in your harness, same budgets, blind dual-judge with kappa, costs published, losses admitted | BENCHMARKS.md | Any "my system is better" claim; the ecosystem default should be this |
| Validate schemas at stage seams in a pure pipeline | validate.py between extract and build | Multi-stage data pipelines (brain/02 functional core) |
| Publish the extension recipe with a test requirement | "Adding a language extractor" | Any pluggable-by-community tool |
| Tools that ingest arbitrary input need a security module with a threat model, not scattered checks | security.py + SECURITY.md | Ingestion tooling of every kind |

## Brain updates made

- `brain/09-agentic-engineering.md`: extended the queryable-knowledge section
  with the generated-map variant — provenance labels (extracted/inferred/
  ambiguous) on derived knowledge, deterministic-first extraction — and added
  the benchmark-fairness standard (same-harness competitors, blind dual-judge
  with agreement stats, cost axis, honest losses) to the evals discussion.
