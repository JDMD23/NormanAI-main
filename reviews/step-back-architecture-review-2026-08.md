# Step-back architecture review — the 12-round checkpoint

JD asked the right question: "is this 100% the right move — look at the *whole*
architecture, not the batch in front of you." This is the honest answer, grounded in
a direct read of the `phase-0` branch as it stands after batch 5 session 1 (not the
field reports — the code).

## The one-line verdict

The rounds F–S rulings, including S1–S6, are **tactically correct**. But taking the
altitude JD asked for: the *trajectory* has a problem the batch-by-batch cadence hid.
**We have spent twelve rounds perfecting Source → Evidence (enrichment). The layers
that make Norman a *decision-support product* rather than an *accurate list* — a
validated scoring model, product-level observability, and the Priority layer — have
not advanced, and the scorer went live early without its validation coming with it.**
The product is "ranked trust." We have perfected the *ranked inputs* and never
validated the *trust*.

## What the code actually shows (evidence, not report)

**Built, and genuinely excellent** — `core/` (store, entity+resolve, reconcile,
guard/bulkhead, lanes/outbox+records, observe/tripwires, schedule/cadence, contracts),
`contexts/fit` (formula, scorer, velocity, financial_rows), `contexts/discovery`
(crunchbase_csv), `operator/` (board_schema, projection, changes, data_status,
page_body, notion_api), 9 ADRs, ~209 tests. The enrichment engine and the write/
reconcile substrate are principal-grade.

**Absent — and this is the step-back:**
1. **`contexts/priority` does not exist.** The Priority / second-pass urgency ranking —
   *the product's top layer, the "pursue these five first"* — is unbuilt. Norman today
   produces a scored **list**, not a prioritized **decision**.
2. **`contexts/warm_path` does not exist.** The warm-introduction mapping — a whole
   bounded context, and a core part of the original value ("ranked trust" includes
   *how you get in*) — is unbuilt.
3. **There is no scoring eval harness.** `tests/test_scorer.py` is invariant tests
   (bounds, Unknown≠0, monotonicity, hysteresis, routing) **plus exactly two pinned
   directional anchors** (Artemis > Bold Security; Artemis is a Prospect). That is a
   smoke test, not a validation of ranking *quality*. **The scorer is LIVE ranking 95
   companies on a formula whose output has never been checked against JD's expert
   judgment or any ground truth.** No `evals/` directory exists.
4. **`core/observe` is operational-only, by its own docstring:** correlation IDs,
   check_ledger work-state, L1 tripwires. It watches the **lanes** (did they run, are
   they blocked, are we being challenged). **Nothing watches the *product*** — no
   score-drift monitoring (a Fit moving when its evidence didn't, or vice versa), no
   ranking-stability check, no outcome loop. Evidently's drift-as-eval (brain B5) is in
   the brain, not in the system.
5. **No whole-system architecture/rationale doc.** Knowledge lives in 9 ADRs + a
   growing rulings file + JD's head + the build agent's context (bus factor, brain/08).
6. **No tested backup/restore** of the datastore that is now the source of truth for 95
   companies; **no scheduler** (only `cadence.py`), so unattended remains unbuilt.

## The crux argument (why "on-plan" doesn't excuse it)

The handoff put Priority in Phase 2 and validation/governance in Phase 3 — so
Priority-unbuilt is *technically* on-plan. **But the scorer was pulled forward into
production, and its validation was not.** The moment you promote a model to live and
route 95 real companies through it — companies JD is now acting on — you inherit the
obligation to validate it *then*, not in Phase 3. You cannot take the scorer's benefits
early and leave its trust-check late. That validation debt was incurred at the scorer's
go-live and has compounded for twelve rounds while we polished its *inputs* to the
decimal. **We verified the lens to sub-pixel sharpness and never checked the
prescription.**

Every enrichment ruling (F–S) has made the *inputs* to the scorer more correct — Sales
Nav ruler, cross-checks, zero-state traps, direction classifier. All real. But a
perfectly-measured input to an unvalidated ranking function yields a board that is
**precisely, verifiably, and confidently ranked — with no evidence the ranking is
right.** That is the single largest exposure in the system, and it is invisible from
inside the enrichment work.

## Are S1–S6 the right move?

Tactically yes; as an *emphasis*, no — they continue investing in the layer that is
already the strongest. Keep **S1** (careers lane — cheap, and it crosses careers to the
unattended-safe side of the L2 line) and **S5's** shadow-mode discipline. But the
vendor eval, working views, and any parallelism should **yield priority** to:
- **(A) Validate the scoring model against JD's judgment** — the cheapest, highest-
  value action available, and it may be partly done informally already.
- **(B) Add product observability** — score-drift + ranking-stability, so the board can
  tell you it's *right*, not just that it *ran*.
- **(C) Begin Priority** — the layer that turns the accurate list into a decision.

## Open questions (to resolve before finalizing the recommendation)

**Scoring trust:** Has JD ever confirmed the live ranking matches his gut — top-10 are
who he'd actually chase, nothing in Prospect feels wrong, nothing shelved feels like a
miss? When he overrides a placement, is that disagreement captured as eval signal (his
override *is* ground truth)?
**Observability:** Is there *any* monitoring of score/ranking stability over time? Is an
outcome loop (pursued → converted/died) even on the roadmap?
**Process:** Has a holistic code review or **security review** run since the system
began touching real LinkedIn/Crunchbase credentials and storing company data (one
cleanup pass at round 6, twelve rounds of forward build since)? Is there a current
whole-system doc? Tested backup/restore?

## Provisional recommendation

Do not stop the build — it's good. But **make the next deliberate build "prove the
board is right," not "fill the board faster."** Keep the cheap safe wins (careers lane,
liveness gate); pause the vendor/parallelism/views expansion for one or two rounds and
spend them on scoring validation + product observability, then start Priority. Finalize
once the open questions above are answered.
