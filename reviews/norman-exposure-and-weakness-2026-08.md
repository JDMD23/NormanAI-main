# Norman — fresh exposure & weakness map (post-33-study brain)

A second, deeper pass over crm-core with the now-complete brain (00–10 + 33
studies). Focus: exposures and weaknesses **not named in earlier reviews**, each
grounded in code, with *why* it matters and which (new) popular repo would close
it. Framing up front: **the brain is now build-ready.** These are sharpeners for
specific components, not gates — and I lead with what's genuinely strong so the
rebuild doesn't churn it.

## Confirmed strengths — do not touch these
- **Tests are behavior-based, not mock-theater.** 37/82 files use mocks but only
  ~4 mock-interaction assertions — they mock I/O boundaries (Notion, Chrome) and
  assert on values (brain/03, done right). Keep this discipline; add property
  tests and the eval harness *on top*.
- **The causal outbox** (intent → verified readback → receipt) and **verified
  writes** (write-then-read-back-confirm) are genuinely excellent. Promote, don't
  replace.
- **Notion retry/backoff exists** — retryable codes {429,500,502,503,504},
  `Retry-After` honored. The base is there; the gap is circuit-breaking (below).

## New weaknesses & exposures (ranked, with why)

### W1. Config is validated syntactically, never semantically — HIGH, cheap fix
CI runs `json.loads` on every config (parses) but nothing validates the *shape*:
that Fit weights form a valid rubric (components present, weights sane), that a
mode's thresholds are coherent. A valid-JSON-but-wrong-shape config ships and
**silently misscores the entire board** — the worst failure for a system whose
product is a ranking. **Why it matters:** the config *is* the scoring logic
(brain/10 #5 gate expensive stages on preconditions; a bad formula is worse than
a crash because it looks like it worked). **Fix:** schema-validate every config at
boot with jsonschema/pandera (both now studied) — fail fast, don't limp. Days.

### W2. 173 broad-except/suppress sites + no real-time alerting = silent failures at scale — HIGH
Many are legitimate lane-isolation (a source failing must not kill the run,
brain/10 #8). But **173** is a large surface, and without the observability layer
(evidently/OTel, not yet built) a genuinely-swallowed error is *invisible* — the
exact silent-failure mode that rots a scheduled board (brain/08 #6). **Why:**
lane isolation and silent failure look identical in code; only a log+metric on
each suppression distinguishes them. **Fix:** audit that every broad except emits
a structured log + metric, and build the observability layer so suppressions are
counted, not hidden. (This is why W2 and the observability gap compound.)

### W3. Retry exists, but no circuit-breaking / bulkhead on external deps — MEDIUM-HIGH
Norman retries a flaky Notion/Grok call, but nothing *stops hammering a dead
dependency*. A prolonged Notion outage means every lane burns its 15-minute window
retrying, starving the whole session. **Why:** retry handles blips; circuit
breakers handle outages (fail fast, shed load, recover), and bulkheads stop one
dead source from sinking the session. **Fix:** a circuit-breaker + bulkhead around
each external dependency (Notion, Grok, each browser source). → **new study:
resilience patterns** (below).

### W4. No systematic reconciliation loop — MEDIUM now, HIGH the day SoR moves off Notion
There's ad-hoc divergence detection (`linkedin_aggregate/divergence.py`, preflight
checks, provenance backfill) but no **reconcile loop**: a continuous "desired
state vs observed state → heal the difference." Today Notion *is* the SoR so
there's nothing to reconcile against — which is itself the weakness. The moment
the rebuild makes a real datastore the truth and Notion a projection (recommended
in the architecture), you **need** a reconciler keeping Notion in sync and healing
drift. **Why:** two stores without a reconciler diverge silently; the projection
lies. **Fix:** a level-triggered reconcile loop. → **new study: the Kubernetes
controller reconcile pattern** (below).

### W5. No tested backup/restore of the system of record — MEDIUM
No clear backup/restore of the Notion board. The outbox gives *intent
replayability* (a partial DR story), but "a bad batch write corrupted 200 pages —
restore to yesterday" has no tested path. brain/06: *backups exist only if
restores are tested.* **Why:** the SoR is the whole product; one errant script
can corrupt it, and verified-writes prevent *bad single writes*, not *a bad script
run in bulk*. **Fix:** periodic SoR snapshot + a tested restore; the move to a real
datastore makes this native (point-in-time recovery).

### W6. Single-machine / single-Chrome availability SPOF — MEDIUM (architectural)
Everything runs on JD's machine with a logged-in Chrome. Machine asleep, Chrome
logged out, or laptop closed → the whole automation stops, silently. The browser
daemon (planned) makes it *efficient* but not *available*. **Why:** an unattended
system that only runs when one laptop is awake isn't really unattended. **Fix:**
a hosted runner + a cloud/remote browser (the capability ladder: local Chrome →
remote browser) so the schedule survives the laptop. Weigh against the ToS/session
sensitivity of moving logged-in sessions off JD's machine.

### W7. Orchestration is hand-rolled dispatch, not a data-aware DAG — MEDIUM
`crm_runtime_dispatch` + leases + windows + the signal watcher hand-roll a
scheduler for what is really a dependency DAG (watcher → intake → enrich → score →
second-pass → warm-path). It works, but reimplements retries, backfills,
dependency ordering, and run observability that mature orchestrators provide.
**Why:** hand-rolled orchestration is a maintenance surface and lacks the
lineage/backfill/observability that come free from a real engine. **Fix:** adopt a
durable workflow/asset orchestrator for the schedule. → **new study: Temporal
and/or Dagster** (below).

### W8. No cost/quota governance across browser + Grok + LLM — LOW-MEDIUM
Beyond the 15-min window there's no unified budget across browser sessions, Grok
API, and LLM calls. **Why:** cost is a real constraint at scale and an unbudgeted
agent loop can surprise you. **Fix:** a token-bucket budget per resource per
session (orca's cost-in-tool-descriptions + a shared budget); mostly a brain
pattern already, needs applying.

## Other popular repos worth studying (ranked, each → the gap it closes)

These are **enhancements to specific components**, not prerequisites. The brain is
build-ready without them; each sharpens one weakness above.

| Repo | Closes | Why it's the right reference |
|---|---|---|
| **kubernetes-sigs/controller-runtime** | W4 reconciliation | THE canonical reconcile-loop pattern: desired-vs-observed state, **level-triggered not edge-triggered** (converge from any state, not just react to events). Exactly the model for keeping Notion synced to a real SoR and self-healing drift. Highest new value. |
| **temporalio/temporal** (or sdk-python) | W7 orchestration, W3 durability | Durable execution: the scheduled DAG with built-in retries, timeouts, exactly-once, and resumability — the mature form of the hand-rolled dispatch + parts of the outbox. |
| **dagster-io/dagster** | W7 orchestration + observability | Asset-oriented, **data-aware** orchestration with built-in lineage, backfills, and freshness/drift observability. More data-pipeline-shaped than Temporal; would inform the scheduler *and* `core/observe`. Study one of {Temporal, Dagster} by which model fits — Temporal for durable steps, Dagster for data assets. |
| **resilience4j** (Java, canonical) or **pybreaker**/**tenacity** (Python) | W3 circuit-breaking | The reference implementations of circuit-breaker + bulkhead + timeout + fallback. Small study, directly fills the outage-resilience gap the retry layer leaves. |
| **stripe/stripe-python** + their idempotency design | W5/robust writes | The canonical idempotent-mutation-over-a-flaky-network pattern (idempotency keys). Norman's outbox already does most of this; worth confirming against the gold standard. |

## Honest bottom line
After 33 studies + `brain/00–10`, the brain is **genuinely elite and build-ready**
for Norman. The weaknesses above are real but bounded, and every one maps to a
pattern already in the brain (W1 jsonschema, W2 evidently/OTel, W3 resilience,
W4 reconcile, W5 DR, W6 availability, W7 orchestration). The three studies worth
doing — **controller-runtime, Temporal or Dagster, and a resilience reference** —
are *sharpeners for the scheduler, store-reconciliation, and resilience
components*, not gates. Diminishing returns have set in on general knowledge; the
remaining value is these three narrow, high-leverage domain references and then
**building**.
