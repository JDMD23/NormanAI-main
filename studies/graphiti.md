# Study: Graphiti (Zep)

- **Repo:** https://github.com/getzep/graphiti
- **Studied:** 2026-08-10
- **What it is:** a temporally-aware knowledge graph engine for agent memory, where every fact
  carries a validity window and contradictions invalidate rather than overwrite.
- **Why it was worth studying:** Norman hit BI2 — *"a ruling was made, the code obeyed it, and the
  data never did."* Ten rows written under a superseded rule kept feeding the score for weeks.
  Graphiti is that problem solved structurally.

## Architecture at a glance

Four concepts, and the separation between the first two is the whole design:

- **Episodes** — the raw ingested stream. Ground truth, append-only, never edited.
- **Entities** (nodes) — *evolving summaries* of people, products, policies, concepts. Derived
  from episodes, not authored.
- **Facts** (edges) — triplets `Entity → Relationship → Entity`, each with a **temporal validity
  window**.
- **Custom types** — developer-defined ontology via Pydantic models.

Retrieval is hybrid: semantic embeddings **+** keyword BM25 **+** graph traversal.

## What this codebase does exceptionally well

**1. Bi-temporal modelling — two clocks, not one.** A fact carries *when it was true in the
world* and, separately, *when we learned it*. Those are different questions and most systems
collapse them into one timestamp and then cannot answer either properly.

**2. Contradiction invalidates, it does not delete.** In their words: *"old facts are invalidated
— not deleted."* The graph can answer **"what's true now"** and **"what was true at any point in
time"** from the same store.

**3. Episodes are separated from entities, and the direction is one-way.** Raw arrivals are
immutable; the entity summary is derived and rederivable. This is the functional-core /
imperative-shell split (`brain/02`) applied to *memory* rather than to computation.

**4. Incremental, not batch.** They draw the contrast with GraphRAG explicitly: *"static document
summarization, batch-oriented"* versus *"continuous, incremental updates"* without recomputing
the graph. Supersession is cheap because it's an edge write, not a rebuild.

**5. Provenance is not optional.** Every derived fact traces to the source episode. A summary you
cannot trace is a summary you cannot audit.

## Questionable calls and tradeoffs

- **A graph database is heavy** for small corpora, and the LLM-driven entity extraction costs
  tokens per episode. For a few hundred entities the machinery outweighs the benefit — which is
  precisely Norman's situation, and the reason to steal the *model* and not the *engine*.
- **Automatic invalidation is an inference.** Deciding that fact B contradicts fact A is a
  judgment, and getting it wrong silently rewrites history. They accept this because the
  alternative — a human adjudicating every contradiction — does not scale. **Norman's population
  is small enough that it should not accept it.**

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| **Model two clocks: when a fact was true, and when you learned it.** Collapsing them loses both questions | bi-temporal validity + ingestion provenance | Any store of measured values; the cost is one extra column and it is always worth it |
| **Supersession is data, not bookkeeping.** A superseded fact gets an end-date, not a deletion | `valid_to` / `invalid_at` | Ruling logs, config history, scoring rules — anywhere a rule changed and old rows exist |
| **Separate the immutable arrival stream from the derived summary, one-way** | episodes → entities | Any enrichment pipeline; makes the summary rederivable and the history auditable |
| **"What was true then" must be answerable from the same store as "what is true now"** | temporal query | Audit, replay, and any system whose past decisions get questioned |
| Automatic contradiction resolution is an inference and should be a human gate below a certain scale | LLM-driven invalidation | Small, high-stakes corpora should adjudicate; large ones cannot |

## Brain updates made

- `brain/04-data-and-state.md`: **bi-temporal storage** — a measured value carries both the
  interval it was true and the moment it was recorded; supersession sets an end-date rather than
  overwriting.
- `brain/10-workflow-and-decision-systems.md`: extends #4 (*facts are claims, not values*) with
  **a claim has an interval** — the missing dimension. A claim without an end-date cannot be
  superseded, only overwritten, and overwriting is what made BI2 invisible.
