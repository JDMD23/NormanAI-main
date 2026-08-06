# 10 — Workflow and decision-support systems

The discipline of systems that ingest signal, resolve it into *trusted facts*,
and route entities through a **lifecycle of states** that drive human or
automated action. The archetype is a prospecting CRM (Source → Evidence → Fit
Score → Status → Priority), but the patterns generalize to any pipeline that
turns evidence into ranked decisions: fraud triage, content moderation, lead
scoring, alerting, underwriting, clinical routing. This is the "workflow
designer" body of knowledge — distinct from general engineering (00–08) and from
agentic engineering (09), and it is where these systems are actually won or lost.

Founding evidence: the Norman CRM operating spec. Each pattern below is stated
generally; the failure modes are the ones that recur across this class of system.

## 1. The lifecycle is a state machine — make it explicit and total

Every entity is in exactly one state; every transition has an owner, a trigger,
and a reason. Enumerate the states, the legal transitions between them, and the
terminal/protected set — on paper, before code. The states that aren't
enumerated are where the bugs live (an entity that's "sort of qualified but
also under review"). A status field that is stringly-typed and set from twelve
places is the god-object anti-pattern (brain/08) wearing a business costume.
Model it once, enforce transitions in one place, and every illegal state becomes
a category of bug that can't occur (brain/01 make-illegal-states-unrepresentable).

## 2. Separate the continuous signal from the discrete state — and add hysteresis

A *score* is continuous; a *status* is discrete. Mapping one to the other with a
bare threshold makes the state **flap** whenever the signal wanders near the
line — a score oscillating 59↔60 thrashes the entity between shelves, spams the
"what changed" view, and destroys operator trust. The fix is control-systems
thinking: **asymmetric enter/exit thresholds** (enter Prospect at 60, but don't
*demote* until below a lower floor, e.g. 57) or debouncing (require N consecutive
readings, or a minimum dwell time, before a transition). Any system that buckets
a continuous signal into discrete routing needs this and most omit it. State the
floors explicitly and treat them as tunable policy, not magic numbers.

## 3. Write-authority is conditional, not global

"One writer per value" (brain/04) generalizes here: **ownership can depend on the
entity's state.** The machine owns Status while the entity is in machine-routed
states; the human owns it in relationship states (Engaged, Top Pursuit, Client);
a *protected* set is refresh-the-evidence-but-never-route. Model authority as
`(field × state) → owner` and enforce it structurally. The safety rule that makes
this trustworthy: **the system refuses a write it doesn't own rather than guessing**
(the "safety system refuses uncertain writes" principle). Machines quietly
overwriting human relationship decisions is the single most trust-destroying
failure this class of system has — design it out, don't police it.

## 4. Facts are claims, not values

Every piece of evidence carries **source, freshness (`checked_at`), and
confidence** — it is a *claim*, not a bare value. Two rules follow:
- **Unknown ≠ 0.** Missing evidence must be representable as missing and must
  degrade the decision gracefully — renormalize over known components, cap the
  score (a "data-blind cap"), or defer — never silently count as zero. A zero
  masquerading as "we checked and it's nothing" is a lie the model tells itself.
- **Decisions cite their evidence.** The output records *why* (the strongest
  reasons) and *what's missing*, so a human can audit the routing and an LLM
  second pass can't fabricate (brain/09 grounding; graphify provenance labels).
Stale evidence is its own state: a fact checked six months ago is not a current
fact, and freshness should influence both routing and re-check cadence.

## 5. Gate expensive or irreversible stages on explicit preconditions

Scoring, writing, escalating — each runs only when its preconditions are met and
provably so: required inputs resolved, none still open, an explicit "needs
recompute" flag set, and capacity/safety checks passed. A stage that *can* run on
incomplete input eventually will, and will emit a confident wrong answer that
looks identical to a right one. Make the precondition a gate in code, not a
convention in a runbook.

## 6. Idempotent ingestion keyed on identity

Re-arrival of a known entity updates its work queue and **preserves original
provenance** — never duplicates, never rewrites its origin. This requires
**identity resolution before the first write** (name/domain/handle → one
canonical entity); it is the gate the whole system's correctness hangs on,
because every downstream fact attaches to whatever entity you resolved to. Get it
wrong and you corrupt two records at once. (This is why probabilistic entity
resolution is a load-bearing subsystem, not a utility — treat it as such.)

## 7. Operational outcomes are a separate vocabulary from entity state

A source-check result (Success / Partial / Blocked / Manual) is *operational
metadata about the machine's work* — it is **not** the entity's business status.
Keep the two vocabularies rigorously separate: business states drive operator
attention; operational outcomes drive the machine's retry/queue logic and live in
an audit surface. Collapsing them buries the operator under machine bookkeeping
("why is this company's status 'Blocked'?") and is a top cause of these systems
feeling incomprehensible.

## 8. All-or-nothing lanes

A transient failure **consumes no budget, writes no partial evidence, and stays
queued.** Half-written evidence is worse than none because it reads as fact. Each
enrichment lane is a small transaction: either it produces verified evidence and
commits, or it fails cleanly and leaves the entity exactly as it was, retryable.
(brain/04 transactions delimit invariants; brain/02 idempotent retries with
backoff.)

## 9. Tiered cadence — attention is a budget

Monitoring frequency follows the entity's tier: hot entities (Prospects, Top
Pursuits) get checked often; cold ones (Watchlist) rarely. Attention — browser
sessions, API credits, LLM calls, operator glances — is finite and metered, so
spend it where the expected value is. A flat "re-check everything nightly" policy
either burns the budget on the cold tail or starves the hot head. Make cadence a
function of tier and freshness.

## 10. Human-in-the-loop is designed, bounded, and reason-coded

Enumerate the *exact* decisions a human owns, and give each a **fixed set of
reason codes** — not free text. "Review Required" is not a mood; it is one of
{thin-data, crypto-hold, invalid-input, identity-conflict, conflicting-evidence},
and each code implies a specific next action. Bounded, coded human input is a
designed feature: it makes the queue triageable, the automation resumable (fix
*this* input → reopen *that* check → recompute), and the system's uncertainty
legible. Open-ended "someone should look at this" is a leak that fills with
sludge. Pair every human decision with the deterministic machine action it
unblocks (brain/09 autonomy calibration; the reason code is the interface between
the two).

## 11. Score change and state change are different truths — surface both

The operator must simultaneously see the continuous truth ("Fit moved 96→82,
review cleared, evidence reduced it") and the discrete truth ("still Prospect").
Show only the state and they distrust it when the number moves; show only the
number and they can't act. The operator card is the join of both, plus *why* and
*what's next* — the presentation layer's whole job is making the state machine's
current cell and the evidence behind it legible at a glance.

## Failure-mode catalog for this class

- **Flapping routing** — continuous→discrete with no hysteresis (see 2).
- **Machine clobbers human decisions** — no conditional authority (see 3).
- **Silent zeros** — missing evidence counted as 0, not Unknown (see 4).
- **Confident wrong answers** — stages run on incomplete input (see 5).
- **Duplicate/forked entities** — write-before-identity-resolution (see 6).
- **Operator drowning** — machine outcomes leaked into business states (see 7).
- **Phantom facts** — partial evidence committed on transient failure (see 8).
- **Attention bankruptcy** — flat cadence instead of tiered (see 9).
- **HITL sludge** — unbounded, un-coded human queues (see 10).
- **Distrusted board** — state shown without the evidence that produced it (see 11).

## Meta-principle

The spine (Source → Evidence → Score → Status → Priority) is what everyone
builds. The trustworthiness — hysteresis, conditional authority, evidence-as-
claims, refuse-uncertain-writes, all-or-nothing lanes, coded HITL — is what makes
the output something a human will *act on without re-checking*. That is the entire
product of a decision-support system; a ranking nobody trusts is worse than no
ranking, because someone acted on it. Build the substrate, not just the spine.
