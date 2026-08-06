# Study: kubernetes-sigs/controller-runtime

- **Repo:** https://github.com/kubernetes-sigs/controller-runtime @ `820ed1a` (2026-08-05)
- **What it is:** The Go library behind Kubernetes controllers/operators — the
  framework for the **reconcile loop**: keep the world matching a declared desired
  state. The canonical implementation of the most important pattern in
  keep-two-things-in-sync systems.
- **Why studied:** Norman's W4 gap — no reconciliation loop, which bites the moment
  a real datastore becomes truth and Notion becomes a projection. Maps to a new
  `core/reconcile/`.

## The pattern

A `Reconciler` has one method: `Reconcile(ctx, request) → (Result, error)`. It
**compares the desired state (the spec) against the actual observed state, and
takes whatever action converges them** — create, update, delete. Three properties
make it powerful, and all three are what Norman needs:

1. **Idempotent and state-based, not delta-based.** Reconcile doesn't process "an
   event"; it reads current desired + current actual and drives toward
   convergence. Called once or a hundred times, it lands in the same place. You
   never write "on update, do X" — you write "make actual match desired," and it's
   correct from *any* starting state.
2. **Level-triggered, not edge-triggered.** Events *trigger* a reconcile, but the
   controller also **requeues periodically** (`Result{RequeueAfter: d}`), so a
   *missed* event (a dropped webhook, a crash, a write that failed silently)
   self-heals on the next sweep. The library's own docs say it plainly: to wait
   for an external thing, return a poll interval — don't depend on the event
   arriving. This is the antidote to the entire class of "the projection silently
   drifted from truth."
3. **The result carries when to look again** — `RequeueAfter` is per-object tiered
   cadence (a hot object reconciles sooner), the same idea as Norman's brain/10 #9.

## Lessons for Norman
- **The SoR↔Notion sync is a reconciler.** Datastore = desired state; Notion =
  actual. A reconciler reads both, patches Notion toward the datastore, and
  requeues — so if a write failed, a property drifted, or a manual Notion edit
  happened, the next sweep heals it. This *dissolves* the two-stores-diverge risk
  (W4) instead of hoping every write succeeds.
- **Model business convergence the same way.** "A Prospect must be in the SN list,"
  "a scored company must have a current card" — these are reconcile invariants:
  state the desired condition, let a loop converge it, don't script every
  transition. This composes with the state machine (brain/10 #1): the state
  machine decides *what* the state should be; the reconciler makes the world *match*.
- **Level-triggered is the unattended-reliability principle.** A scheduled system
  that only reacts to events accumulates silent drift; one that periodically
  re-converges from observed state is self-healing. Every Norman lane should be
  re-runnable to convergence, not a one-shot event handler.

## Transferable lessons
| Lesson | Norman application |
|---|---|
| Reconcile = compare desired vs observed, act to converge; idempotent, state-based | `core/reconcile/`: keep Notion projection synced to the datastore SoR |
| Level-triggered (periodic re-converge) heals missed events — don't rely on events alone | Self-healing drift; the answer to W4 and silent projection lies |
| Requeue-after = per-object tiered cadence | Hot entities reconcile sooner (brain/10 #9) |
| Desired-state invariants replace scripted transitions | "Prospect ⇒ in SN list", "scored ⇒ has card" as reconcile invariants |

## Brain updates
- `brain/02`: new **"Keep projections in sync with a reconcile loop"** subsection —
  level-triggered convergence (desired vs observed, requeue-to-heal) as the pattern
  for any system with a source of truth and a derived copy.
