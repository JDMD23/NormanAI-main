<!--
For JD: this is the concrete batch-5 execution plan the build chat runs. It folds in
the round-11 rulings (R1–R9, in NormansBrain reviews/phase1-lane-design-decisions.md).
The one design change from the agent's proposal: batch 5 runs TWO lanes, not three —
it proves the permanent skeleton on the safe axis and defers the two-concurrent-browser
question to batch 6. Attended, JD present, same safety substrate.
-->

# Batch 5 — First Split-Pipeline Batch: Execution Plan

**Goal:** prove the permanent concurrency skeleton (lane interface, guarded writer,
per-company barrier, batch observability, halt semantics) on real data, on the axis
with **zero two-browser risk**, and **measure** whether the split beats
serial-with-interleaving. ~30–35 companies, attended, JD present.

**Governing decision (R1/R9):** batch 5 is **two lanes**, not three. The one genuinely
interim-and-risky part — two concurrent browsers on one Chrome profile — is deferred to
batch 6. Everything else is built to Phase-1 quality because it *is* the Phase-1 lane
skeleton.

---

## Lane assignments

- **Lane 0 — Orchestrator + browser identity (serial spine).** Holds the
  `linkedin:jd-seat` lease for the whole batch. Runs, per company, at human pace under
  the 80-view throttle with halt-on-first-challenge: **Sales Nav headcount → jobs-
  fallback (if needed)**, and **Crunchbase interleaved into the LinkedIn pacing gaps**
  (G7 — one browser, one active service at a time; no second browser identity). Also
  the **sole writer** (see Apply).
- **Lane 1 — Careers (API, concurrent, no identity).** ATS-API-first
  (Ashby/Greenhouse/Lever/Kula posting endpoints — public, no browser, no account).
  Embed-only boards are **flagged for Lane 0's browser**, never opened by this lane.
  Freely parallel; unattended-safe by nature (R6).

Lanes are **pure producers**: they return typed evidence records and **never touch
SQLite or Notion**. Build the lane interface to Phase-1 quality (R9) — it's the
`core/lanes` registry.

## Write discipline (R2 / R8)

- **Single guarded writer = the orchestrator.** It drains a queue of typed evidence
  records and applies each idempotently through the existing write path
  (identity-before-write → verified write → read-back → confirm). Write this apply path
  as an **outbox interface backed by memory now** — so the durable table is a later
  backing-store swap, not a rewrite.
- **Field-level adopt-check immediately before each company's board write (R8):** for
  every field about to be written, if JD authored a newer value, **adopt** human-owned
  fields (never overwrite) and route machine-field edits through the jd-manual dispute
  flow (surface as a delta). Plus the mandatory **session-start sweep** before the batch
  begins.

## Scoring (R3)

- **Write evidence values on arrival** (board fields populate live).
- **Compute score/route/status only at the per-company barrier** = all sources have a
  *terminal* result for that company (terminal includes Unknown / blocked / no-page).
  Per-company, not per-batch — a company scores when *its* slowest source lands.
- **No status is ever written on transient partial evidence.** No flapping.

## Observability (R5)

Before the batch starts, confirm the work-state view shows, live:
- `batch_id` with child per-lane `run_id`s on every ledger/change/observe row.
- **Per-identity risk budget + tripwires, live:** Sales Nav views/80, challenge count,
  soft-block count.
- **One collapsed "batch health" line** — normal = a single green signal; every
  exception raises itself. JD supervises **by exception**.
- **Per-lane liveness** (last-action timestamp) to catch a silently stuck lane.

## Halt rules (R4)

- **LinkedIn challenge #1 → Lane 0 halts immediately**, no retry, surfaces to JD.
- **Lane 1 (careers-API) has no identity → completes its in-flight work** regardless.
- Batch **never ends silently** — it ends with an explicit per-lane terminal report.
- (Batch 6+ only, when a 2nd browser lane exists: a shared-IP challenge makes the other
  browser lane finish-current-and-pause.)

---

## Step-by-step

1. **Pre-flight (JD present).**
   - `make session-start`: run the dry-run reconcile sweep, adopt any JD edits, confirm
     193+ tests green, all configs boot-valid, tripwire counters at zero, the `batch_id`
     health line live.
   - Confirm the `linkedin:jd-seat` lease is held and the bulkhead refuses a second
     holder (the mechanized guard from ADR 0009).
   - Pick the ~30–35 companies; confirm the throttle arithmetic:
     `(companies × Sales-Nav reads) + (no-careers fraction × fallback reads) ≤ 80`.
     If it exceeds 80, split across two attended sessions.
2. **Launch Lane 1 (careers-API) concurrently.** It sweeps ATS APIs, returns typed jobs
   evidence per company, flags embed-only boards for Lane 0.
3. **Run Lane 0 serially** per company at human pace: Sales Nav headcount (zero-state
   read first, O1), jobs-fallback where flagged, Crunchbase interleaved in the gaps.
4. **Apply on the per-company barrier.** As each company reaches terminal on all
   sources: field-level adopt-check → apply evidence → score → route → project →
   verified read-back. Evidence fields may write on arrival; status only at the barrier.
5. **Supervise by exception.** JD watches the collapsed health line; any lane halt,
   tripwire climb, or stuck-lane liveness flag raises itself.
6. **Close-out.** Per-lane terminal report; session-end flush sweep; record the timing
   measurement (below); commit, push, confirm main current.

## The measurement (R7) — this is half the point of batch 5

Record via observe events, and report:
- **Per-company wall-time** (batch 5 is 30–35 vs. batch 4's 20 — normalize per company;
  batch 4 ≈ 2.5h/20 ≈ **7.5 min/company serial-back-to-back baseline**).
- **Idle-gap composition** on Lane 0: how much of the LinkedIn pacing-gap time was
  filled by Crunchbase/careers work vs. idle. **This computes the interleaving
  counterfactual** — what serial-with-interleaving alone would achieve.
- **Attribute the gain:** how much came from the safe careers-API parallelism vs. from
  interleaving. If the safe axis alone clears the bar, batch 6's second browser may be
  unnecessary.

## Go / no-go criteria

- **GO to keep the pipeline** if batch 5 beats the **interleaving counterfactual** (not
  the back-to-back baseline) by **≥ ~25–30% per-company**, with zero challenges and a
  clean per-lane report.
- **REVERT to serial-with-interleaving** as the standing pattern if the margin over
  interleaving is below that — the orchestration complexity isn't paying for itself.
- **HALT / escalate to JD** on any challenge, any tripwire crossing threshold, or any
  write-discipline anomaly (a clobbered edit, a status written on partial evidence).
- **Batch 6 decision (separate):** only if batch 5 proves the skeleton clean AND the
  measurement shows the second browser lane would add real margin beyond the safe axis,
  take on the two-concurrent-browser topology deliberately — separate browser contexts,
  the R4 shared-IP pause rule, and ideally after the F2 dedicated profile exists.

**Nothing runs unattended. The waiver holds only while JD is present and the
account-risk lane is under the collapsed health line (R6).**
