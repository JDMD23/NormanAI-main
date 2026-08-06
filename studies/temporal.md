# Study: temporalio/sdk-python (Temporal)

- **Repo:** https://github.com/temporalio/sdk-python @ `d5642db` (2026-08-05)
- **What it is:** The Python SDK for Temporal — "a distributed, scalable, durable,
  highly available orchestration engine." You author **workflows** (durable
  orchestration) and **activities** (side-effecting steps) as `async def`
  functions; Temporal makes them survive worker crashes, restarts, and deploys.
- **Why studied:** Norman's W7 gap — orchestration is hand-rolled dispatch. Temporal
  is the mature durable-execution engine for the scheduled DAG. Maps to
  `core/schedule/` and reinforces `core/outbox/`.

## The model

- **Workflow = durable, deterministic orchestration.** The workflow function is
  **replayed from an event history** after any failure, so it must be
  deterministic (no wall-clock, no random, no direct I/O inside it). Its state
  survives crashes because it's reconstructed from history — durable execution.
- **Activity = the side effect.** Anything non-deterministic or I/O (an API call,
  a browser fetch, an LLM call) is an **activity**: run outside the workflow,
  **recorded in history**, **retried by Temporal** per a `RetryPolicy`
  (initial_interval, backoff_coefficient, maximum_attempts,
  non_retryable_error_types), and **survives worker restarts**. At-least-once, so
  activities must be idempotent.
- **Temporal owns retries** — configure the policy; don't add your own retry loop
  inside (double-retry is an explicit anti-pattern the SDK guards against).
- **Timers, signals, queries, continue-as-new** — durable sleep, external input,
  state inspection, and history-truncation for long-running loops.
- **Credentials live in activities on the worker, never in the workflow/history**
  (from the Gemini integration): a security property — API keys never enter the
  replayable event log.

## Lessons for Norman

- **The functional-core / imperative-shell split, enforced by the runtime.**
  Temporal *forces* the exact discipline brain/02 recommends: deterministic
  orchestration logic (the workflow) is physically separated from side effects
  (activities). Norman's session logic (which lanes, in what order, gated on what)
  is a workflow; every browser fetch / Grok call / Notion write is an activity.
- **Durable execution ≈ the causal outbox, generalized.** Norman's outbox makes
  *writes* exactly-once and recoverable; Temporal makes the *whole session*
  recoverable — if the machine dies mid-session, it resumes from history, not from
  scratch. This is the mature form of "leases + windows + resume_automation," and
  it subsumes W7 and part of the outbox.
- **Retry as declared policy on each step**, with non-retryable error types (a
  `Blocked` outcome is retryable; `Manual`/`invalid input` is non-retryable) —
  Norman's Success/Partial/Blocked/Manual maps cleanly onto retry policies.
- **The honest tradeoff (brain/00 scope honesty):** Temporal is a *server* to
  operate (or Temporal Cloud). For a solo operator it may be more infrastructure
  than warranted — the *patterns* (durable workflow vs recorded activity,
  runtime-owned retries, determinism, resume-from-history) are the takeaway even
  if Norman implements a lighter version on its own outbox. Adopt the model; buy
  the engine only if the operational cost is paid for by real need.

## Transferable lessons
| Lesson | Norman application |
|---|---|
| Workflow (deterministic, durable, replayed) vs Activity (side-effecting, recorded, retried) | Session-plan = workflow; every fetch/LLM/write = activity — functional core enforced |
| Durable execution: resume from event history, not from scratch, after any crash | Sessions survive a laptop dying mid-run (also helps W6) |
| Runtime owns retries via declared policy; no nested retry loops | Success/Partial/Blocked/Manual → retry policy + non_retryable types |
| Credentials live in activities, never in the durable history | Keep Notion/Grok tokens out of any replayable log (brain/06 security) |
| Adopt the model even if you don't buy the engine | Norman's outbox + a workflow-shaped session, weighed against running a server |

## Brain updates
- `brain/02`: durable-execution model (workflow vs activity; resume-from-history;
  runtime-owned retries) added to the formal-models and functional-core guidance —
  and the scope-honesty caveat that the *pattern* transfers even when the *engine*
  is too heavy.
