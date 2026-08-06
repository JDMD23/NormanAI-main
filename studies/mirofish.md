# Study: MiroFish

- **Repo:** https://github.com/666ghj/MiroFish
- **Studied:** 2026-08-06 at commit `b5b53ac`
- **What it is:** A "swarm intelligence prediction engine" (Shanda-backed): feed it
  seed material (news, reports, a novel's first 80 chapters), it builds a knowledge
  graph, generates persona agents, runs a social simulation of them on synthetic
  platforms, then a ReportAgent interrogates the simulated world to produce a
  prediction report. Flask backend + React frontend, built on camel-ai's OASIS
  simulation framework and Zep Cloud graph memory. 128 files.
- **Why it was worth studying:** A genre none of the fifteen prior studies touched
  — **prediction via agent-society simulation** — and a clean specimen of
  composition-first engineering with tests aimed exactly at the seams.

## Architecture at a glance

```
seed docs → ontology_generator → graph_builder (Zep GraphRAG)
         → oasis_profile_generator (personas) → simulation_config_generator
         → simulation_runner (OASIS, separate process, dual-platform)
         → zep_graph_memory_updater (temporal memory during sim)
         → report_agent (toolset over the post-simulation world)
Flask backend ⇄ simulation process via file-based IPC (commands/ and responses/
dirs, polled; command types: interview, batch_interview, close_env)
```

## What this codebase does well

1. **Innovation tokens spent correctly.** The hard problems — agent society
   simulation (OASIS/camel-ai, pinned versions) and temporal graph memory (Zep
   Cloud) — are bought, not built. The repo's own code is the differentiating
   glue: ontology extraction from seed documents, persona generation, phase
   orchestration, and the ReportAgent. Brain/07's core-vs-context discipline,
   practiced by a research-adjacent team that could easily have NIH'd a
   simulator.

2. **Tests aimed at the seams, not the coverage number.** Nearly all 18 backend
   test files target the external-dependency boundary: `test_zep_cloud_contracts`
   (contract tests pinning a SaaS vendor's behavior), retry/paging/lifecycle,
   LLM JSON-response robustness, tool-result sanitization, prepare-failure paths.
   When your system is mostly composition, the risk lives at the joints — and
   that's exactly where their tests are.

3. **Phase barriers over eventual consistency, tested.** Zep's graph writes are
   async; the pipeline's next phase reads what the previous phase wrote. So there
   are explicit barriers (`test_zep_simulation_barrier`, `test_zep_report_barrier`)
   ensuring memory writes settle before dependent reads — the
   eventually-consistent seam made explicit and regression-tested rather than
   discovered in production as flaky reports.

4. **Transparent, boring IPC.** Backend and simulation communicate via files:
   commands written to a directory, the sim polls and writes responses, statuses
   are an enum (pending/processing/completed/failed). Crude — polling latency, no
   backpressure — but inspectable (every command is an artifact on disk),
   language-agnostic, and crash-legible. For a two-process system at this scale,
   the right amount of infrastructure (brain/00 scope honesty).

5. **Honest cost disclosure in the quickstart.** "High consumption, try
   simulations with fewer than 40 rounds first" — plus a free-tier note for the
   memory vendor. Products that burn tokens by the thousands rarely say so in
   the install section.

6. **The interview mechanism.** `interview`/`batch_interview` IPC commands let
   you chat with any agent inside the finished simulation — the simulated world
   remains a queryable artifact after the run, not a discarded intermediate
   (same instinct as Understand-Anything's viewer: the output is a place, not
   a printout).

## The core critique: simulation is not prediction until calibrated

The product claim is *prediction* ("rehearse the future… win decisions"), and
the evidence offered is demo anecdotes (a public-opinion case study, a
novel-ending deduction). There is no calibration, no backtesting against
resolved events, no held-out evaluation — nothing distinguishing "the swarm
converged on X" from "the base model's priors say X, with extra steps." Known
failure modes of LLM agent societies (homogenization, sycophantic convergence,
persona collapse over long horizons) go unmeasured. This is the ecosystem's
eval gap at its most acute, because here measurement isn't hygiene — it's the
entire epistemic warrant for the product. The graphify standard (same-harness
baselines, blind judging, costs, losses admitted) applied to resolved
real-world outcomes is what "predicting anything" would need. Until then, the
honest framing is the one their micro-level pitch already uses: a *hypothesis
generator and creative sandbox*, not a forecaster.

## Other tradeoffs

- **Mega-services**: `report_agent.py` (2.6k lines) and `simulation_runner.py`
  (2k) concentrate the orchestration in two files (brain/03 coherence strain).
- **Vendor coupling with data egress**: Zep Cloud is a hard dependency — seed
  material and simulation memory leave the machine; the thick `zep_tools`
  wrapper (1.7k lines) is the right brain/05 move and would ease a future
  self-hosted swap, but the coupling is real.
- **Bilingual codebase** (Chinese docstrings/comments, English identifiers) —
  coherent internally, a contribution-filter externally; the docs handle it
  with full parallel READMEs.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| When you depend on a SaaS, pin your assumptions with contract tests — the inverse of shipping a conformance kit | test_zep_cloud_contracts | Any external API your pipeline trusts; catches vendor drift as a red test, not a prod incident |
| Async-write/dependent-read seams get explicit, tested barriers | zep barriers | Eventually-consistent stores between pipeline phases |
| In composition-heavy systems, test density belongs at the joints | the whole test dir | Complements brain/03; coverage% is meaningless here |
| Keep simulation worlds queryable after the run (interviews, report tools) | IPC interview commands | Simulation/analysis tooling; the artifact is a place |
| A simulation's output is a hypothesis, not a forecast, until calibrated against resolved outcomes | the missing evals | Any generative "prediction" product |

## Brain updates made

- `brain/05-apis-and-boundaries.md`: one addition — when *you* consume a
  third-party service, pin your assumptions with contract tests (the consumer-side
  inverse of shipping a conformance kit), so vendor drift fails your CI instead
  of your production pipeline.
