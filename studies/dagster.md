# Study: Dagster — the software-defined asset model

- **Repo:** https://github.com/dagster-io/dagster
- **Studied:** 2026-08-10
- **What it is:** an orchestrator built on *assets* — you declare the data that should exist and
  its dependencies, rather than the tasks that should run.
- **Why it was worth studying:** BL1, the largest defect of the week:
  `growth ← funding_velocity ← funding_rounds ← nothing writes it`. A scoring component consumed
  a value nothing produced, and **no representation of the system made that visible.**

## Architecture at a glance

The inversion is the entire idea:

```
  TASK-centric   :  run step A, then B, then C.        Dependencies are ORDERING.
  ASSET-centric  :  these things should exist:
                      country_populations
                      continent_change_model
                      continent_stats ← (the two above)
                                                        Dependencies are LINEAGE.
```

Dependencies are declared **by function signature** — `continent_stats(country_populations,
continent_change_model)` — so the graph is derived from the code rather than maintained beside
it. From the repo: *"declare — as Python functions — the data assets that you want to build"*,
with *"integrated lineage and observability"*.

## What this codebase does exceptionally well

**1. The dependency graph cannot drift from the code**, because it *is* the code's signatures.
A task DAG is a second artifact that has to be kept in agreement; an asset graph is derived.

**2. It answers "what produces this?" — the question Norman could not answer.** In a task system,
`funding_velocity` is a column somebody may or may not write. In an asset system it is a node,
and **a node with no producer is visible on the graph.**

**3. Staleness is a first-class property, not a job.** Because the system knows what an asset
depends on, it knows when an upstream changed and the downstream did not. **That is BI2 —
"the code obeyed the ruling and the data never did" — expressed as a graph property.**

**4. It scales down conceptually even where the tool does not.** The asset model is useful on a
whiteboard for eight derived values. The orchestration platform around it is not.

## Questionable calls and tradeoffs

- **Heavy for small systems.** A daemon, a database, a UI, and a deployment story to schedule
  what Norman needs one cron for. `brain/00`: *complexity must be paid for by real, present
  needs.* Norman's present need is one scheduled lane.
- **Assets assume materialisation.** The model fits things that are computed and stored. It fits
  poorly where the "asset" is an external side effect — a Notion page write, a browser session.
  Norman's projection layer would sit awkwardly in it.
- **The asset abstraction has a learning cost** that pays back over dozens of interdependent
  datasets and not over eight.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| **Model the things PRODUCED and their dependencies, not the steps run.** "What produces this?" then has an answer | software-defined assets | Any system with derived values; the payoff scales with interdependence |
| **A node with no producer is a visible defect.** In a task system it is invisible until something reads a null | asset graph | Directly: `funding_velocity` consumed and never produced (BL1) |
| **Derive the dependency graph from the code, don't maintain it beside the code** | dependencies from function signatures | Anywhere a diagram and an implementation can disagree — which is everywhere |
| **Staleness is a graph property**: upstream changed, downstream did not | freshness/staleness tracking | BI2's stale-rule cohort is exactly this |
| Steal the model without the platform when the graph has ~10 nodes | Dagster's own weight | The whole tool is the wrong size for a single-operator system |

## Brain updates made

- `brain/02-architecture.md`: **model the assets, not the tasks.** For any system computing
  derived values, write the asset graph — what exists, what it depends on — *before* the
  execution order. **A node with no producer is a defect that a task-shaped view cannot show**,
  and Norman shipped one for four days (BL1).
- `brain/04-data-and-state.md`: **staleness is a graph property, not a flag.** If you know what a
  value depends on, you know when it is stale without anyone remembering to mark it.
