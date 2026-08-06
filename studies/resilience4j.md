# Study: resilience4j

- **Repo:** https://github.com/resilience4j/resilience4j @ `2f3d998` (2026-07-08)
- **What it is:** The canonical, lightweight **fault-tolerance library** (Java) —
  a composable set of resilience patterns you wrap around any call. The reference
  taxonomy for "make calls to a flaky dependency survivable."
- **Why studied:** Norman's W3 gap — retry exists, but no circuit-breaking or
  bulkheading around Notion / Grok / browser sources. Maps to `core/lanes/` (per
  external dependency) and `core/schedule/`.

## The pattern taxonomy (the module list *is* the lesson)

Each is a composable decorator around a call; the value is knowing the *whole set*
and that they compose:

- **CircuitBreaker** — track the failure rate of a dependency; when it exceeds a
  threshold, **open** the circuit and fail fast (stop hammering a dead service);
  after a wait, go **half-open** and probe; **close** on success. States:
  closed → open → half-open. *This is Norman's W3 gap directly.*
- **Bulkhead** — cap concurrent calls to one dependency so a slow/dead source
  can't consume all resources and sink the whole session (isolation between lanes).
- **RateLimiter** — cap call rate (token bucket) — respect Notion's ~3 req/s, Grok
  quotas, and a humane scraping pace as a *declared limit*, not ad-hoc sleeps.
- **Retry** — bounded retries with backoff (Norman has this; resilience4j is the
  reference for composing it *under* a circuit breaker so retries don't fight it).
- **TimeLimiter** — a hard deadline per call (every external call gets a budget —
  brain/02 "timeouts on every network call").
- **Fallback** — a declared alternative when all else fails (return last-known
  value, or `Unknown`, never a fabricated one).
- **Hedge** — issue a duplicate request after a delay and take the first to
  answer, to cut tail latency (advanced; rarely needed here).
- **Cache** — memoize successful results (Norman's read-through cache, orca).

## The composition insight
These stack in a defined order: `Retry(CircuitBreaker(RateLimiter(TimeLimiter(call))))`
— rate-limit and time-box the call, break the circuit on sustained failure, retry
within the breaker's budget, fall back if exhausted. Every Norman external
dependency should be wrapped in this stack, declared per-dependency (Notion, Grok,
each browser source get their own breaker + limiter + bulkhead), so one dead
source fails fast and in isolation instead of burning the 15-minute session window.

## Lessons for Norman
- **Add circuit-breaking + bulkheading around every external dependency** (W3): a
  prolonged Notion/Grok outage trips the breaker and the session sheds that lane
  fast, instead of every lane retry-starving the window.
- **Rate limits become declared policy, not scattered `sleep`s** — Notion's limit,
  Grok's quota, and the human-pace scraping cadence are RateLimiter configs.
- **Every external call gets a TimeLimiter** — a hung browser page can't hang the
  session.
- **Fallback returns `Unknown`/last-known, never a fabricated value** — resilience
  composes with the trust boundary (brain/04 Unknown≠0).
- **Python implementations:** `pybreaker` (circuit breaker), `tenacity` (retry),
  `aiolimiter`/`limits` (rate limiting) — resilience4j is the *design reference*;
  these are the parts.

## Transferable lessons
| Lesson | Norman application |
|---|---|
| Circuit breaker (closed→open→half-open) fails fast on a dead dependency | Wrap Notion/Grok/each source; W3 fix |
| Bulkhead isolates concurrency per dependency so one dead source can't sink the session | Per-lane concurrency caps |
| RateLimiter makes quotas/pace declared policy, not ad-hoc sleeps | Notion 3 req/s, Grok quota, human scraping cadence |
| TimeLimiter on every external call | No hung page hangs the session (brain/02) |
| Fallback returns Unknown/last-known, never fabricated | Composes with the trust boundary |
| The patterns compose in a defined order | The standard resilience stack around each dependency |

## Brain updates
- `brain/02`: the **resilience pattern stack** (circuit breaker + bulkhead +
  rate limiter + time limiter + retry + fallback, composed) added to the
  cross-cutting failure-design section — completing "timeouts on every call" with
  the full failure-isolation taxonomy.
