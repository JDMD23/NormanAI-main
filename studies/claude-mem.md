# Study: claude-mem

- **Repo:** https://github.com/thedotmack/claude-mem
- **Studied:** 2026-08-06 at commit `f85bb28` (v13.13.1)
- **What it is:** Persistent memory for Claude Code: lifecycle hooks capture tool
  usage, an LLM compresses observations into semantic summaries at write time,
  storage is SQLite + Chroma (hybrid keyword/semantic), retrieval is a session-start
  context injection plus MCP search tools. Grown across 13 major versions into a
  small distributed system: worker daemon with web UI, process supervisor, sync
  hub, Docker e2e, 239 test files.
- **Why it was worth studying:** The second memory architecture in the collection
  (after ECC's instinct system) — and the other *half* of the problem. Together
  they complete the picture of agent memory.

## Architecture at a glance

```
5 lifecycle hooks (SessionStart/UserPromptSubmit/PostToolUse/Stop/SessionEnd)
        │ capture
        ▼
worker service (Bun daemon, HTTP API + web viewer)
        │ compress (Claude Agent SDK summarizes observations at write time)
        ▼
SQLite (sessions, observations, summaries) + Chroma (vectors)
        │ retrieve
        ▼
SessionStart context injection  +  MCP tools: search / timeline / get_observations
```

Supporting cast: `src/supervisor/` (health checker, process registry, graceful
shutdown, env sanitizer), `src/storage/{sqlite,postgres}`, multi-IDE adapters
(Cursor, OpenCode, Antigravity, Codex), `plans/` of dated design docs, and
`ragtime/` — a corpus-investigation batch tool that repurposes the memory system
for entity/timeline extraction over email archives.

## The two big findings

### 1. Episodic vs procedural memory — the collection now has both

ECC's instinct system (studies/ecc.md) is **procedural** memory: learned
behaviors, confidence-scored, project-scoped. claude-mem is **episodic** memory:
what happened, compressed and timestamped, searchable by content and time. They
answer different questions — "how do I usually do X here?" vs "what did we do
about X in March?" — and a complete agent memory needs both. Design corollaries
recorded in the brain: episodic memory wants *write-time compression* (raw
transcripts are unaffordable to store-and-rescan; summarize as you capture) and
*time as a first-class axis* (the `timeline` tool exists because "what was
happening around this?" is a primary retrieval mode for episodes, meaningless
for instincts).

### 2. The 3-layer retrieval workflow: filter on an index, fetch only survivors

The MCP surface enforces progressive disclosure over *results*:
1. `search` → compact index entries with IDs (~50–100 tokens/result)
2. `timeline` → chronological neighborhood of interesting hits
3. `get_observations` → full detail (~500–1,000 tokens/result), batched,
   **only for IDs that survived filtering** — ~10x token savings claimed.

This is the anthropic-skills loading model applied to retrieval: never pull full
records into context before filtering on a cheap index. It generalizes to any
agent-facing search tool (memory, docs, tickets, logs) and is now in the brain.

## What else it does well

- **Operational engineering unusual for a "plugin."** Process supervision with
  health checks and graceful shutdown, atomic worker restart plans ("worker
  restart single source of truth"), env sanitization, versioned cleanup
  migrations (`CleanupV12_4_3.ts`), 239 test files including platform-specific
  regression tests (Windows transcript watching, provider error classification).
  The failure modes of a daemon-based capture pipeline are engineered for, not
  wished away.
- **`plans/` as dated design docs** — the plan-first discipline dogfooded:
  `2026-06-10-worker-restart-single-source-of-truth.md`,
  `2026-07-17-phase5-two-lane-sync.md`. Decisions have artifacts; the repo's
  evolution is legible.
- **Storage pragmatism**: boring SQLite as source of truth, Chroma as a derived
  semantic index, postgres as scale-out option — the brain/04 shape (one boring
  store, derived indices recomputable from source).
- **Auto-generated changelog** ("no need to edit the changelog ever") — one less
  hand-maintained fact to drift.

## Questionable calls and tradeoffs

- **Heavy operational surface for the value delivered.** Bun + uv + Python +
  Chroma + a resident worker daemon + optional postgres, to remember sessions.
  Hybrid semantic search over one user's own history is plausibly over-built
  where BM25-over-SQLite (the ui-ux-pro-max lesson: boring retrieval, zero deps)
  would cover most queries — the classic brain/06 over-built pattern, though the
  239 tests and supervisor show the cost is at least being paid competently.
- **Version scars in the codebase.** A class named `CleanupV12_4_3` and
  version-specific migration logic baked into services betray 13 majors of
  in-place evolution; honest, but accumulating (brain/07 debt-by-interest-rate
  says schedule the consolidation).
- **Marketing-to-substance ratio in the README** — 33 translated READMEs, star
  charts, badges before the architecture; the actual design (which is good) is
  two clicks away. A familiar genre cost.
- **The recurring gap, again:** no evals measuring whether injected memory
  actually improves session outcomes — the one measurement that would justify
  the infrastructure. (Ten of eleven repos now share this gap; superpowers is
  still alone.)

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Agent memory splits: episodic (what happened, time-indexed) vs procedural (learned behavior, confidence-scored) — design them separately, need both | vs ECC's instincts | Any agent memory system |
| Compress at write time: summarize observations as captured; raw transcripts are for recovery, not retrieval | Agent SDK compression step | High-volume capture pipelines |
| Retrieval tools should force index-then-fetch: compact IDs first, full records only for filtered survivors (~10x savings) | search/timeline/get_observations | Any agent-facing search over large records |
| Time is a first-class retrieval axis for episodic data ("what was happening around this?") | timeline tool | Memory, logs, incident tooling |
| A capture daemon is a distributed system: supervise it (health, graceful shutdown, atomic restart) or it will silently stop remembering | src/supervisor | Any hook-fed background service |
| Keep dated design docs in-repo; auto-generate the changelog | plans/, changelog rule | Everywhere; cheap legibility |

## Brain updates made

- `brain/09-agentic-engineering.md`: extended the agent-memory section with the
  episodic/procedural split, write-time compression, time as a retrieval axis,
  and the index-then-fetch retrieval rule.
