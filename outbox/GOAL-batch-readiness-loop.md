# GOAL: batch readiness — a bounded loop with frozen exit criteria

**To the CRMx build agent. This is an execution spec, not a review round.** It replaces the
round-by-round exchange until it terminates.

---

## THE GOAL, in one testable sentence

> **Norman ingests the next CSV batch and produces a correct ranked chase list, with no defect
> that a human has to catch.**

Not "no bugs." **No defect that changes what JD does.** That is the bar, and it is reachable.

---

## WHY A LOOP, AND WHY THIS SHAPE

Rounds 34–42 ran find → fix → verify → find, eight times. Every defect was real. **But a loop
whose exit condition is "no more defects found" cannot terminate**, because the search always
succeeds eventually. What ended each round was attention, not completion.

`brain/09` (autoresearch): **freeze the judge** — the evaluation lives outside the agent's
editable surface, or the loop eventually optimises the metric instead of the target.
`brain/09` again: **normalize by budget, not configuration** — a fixed budget supplies the kill
criterion. `brain/00`: **complexity is the enemy, and it is incremental.**

So: the checklist below **is the judge, and you may not edit it.** If a criterion is wrong,
say so and halt — do not rewrite it and continue.

---

## DONE — the frozen exit checklist

Every item is an **observable with a number**, not a description. The loop ends when Band A is
green and Band B is surfaced. Nothing else counts as done, and nothing else counts as
required.

### Band A — autonomous. You complete and verify these alone.

**A1 · The `people` dedup can run against the state it diagnosed.**
The migration contains the repair, not just the constraint. Report:
```sql
SELECT COUNT(*) FROM people;                                        -- expect ≈170
SELECT COUNT(*) FROM (SELECT company_id, COALESCE(linkedin_url, full_name)
                      FROM people GROUP BY 1,2 HAVING COUNT(*)>1);  -- expect 0
```
**Test: seed the DUPLICATE state → migrate → apply twice.** A test that applies twice against a
clean store does not exercise this bug; the first apply was the failing case, not the second.

**A2 · Every lane is idempotent, proven by running it twice.**
`careers_lane`, `contacts_lane`, `rescore`, `reconcile_sweep`, `chase`. Second run writes
**zero** rows. One test each, and report the five numbers.

This is the general form of A1. `brain/10 #6` — *idempotent ingestion keyed on identity* — and
the duplication happened because `person_id` was generated per call. **Check every lane has a
key, not just the one that broke.**

**A3 · The non-discriminating-field detector exists and has been run.**
Flags any field holding the same value across the whole board. Ruled in round 30, parked, and
since demonstrated twice (`hq_city`, `last_touched_on`).
**Build it, run it, report what it finds. Do not fix what it finds** — that is a finding for
the next loop, not work for this one.

**A4 · The coverage ledger is an exact number.**
Companies scored without a denominator, counted per status. No estimate. This number gates
Band B and the batch order.

### Band B — human gates. Halt and surface. Do NOT proceed through these.

`brain/09`: **hard human gates at irreversible or direction-setting points.**

**B1 · Sales Nav coverage sessions.** Throttle-gated, attended, JD's go per session. Surface
A4's number and the sessions required at ~2 views/company against the 80/day cap.

**B2 · The `hq_source` swap.** Currently `hq_city`, correctly held inert. When A4 reaches zero:
**simulate with the round-31 compensation — lower every threshold by the board-wide mean drop,
preserving location and passing only dispersion — then show JD the movers and STOP.** Do not
apply. This moves companies in both directions and it is his call.

### Band C — the batch. Only after A is green and B is answered.

**C1 · Dry-run the whole pipeline on the new CSV and report the diff before anything writes.**
Every tool already defaults to dry-run; use it. The diff is the artifact JD approves.

---

## THE LOOP

```
budget: 3 passes. Not 4.

each pass:
  1. run every Band A check
  2. fix only what a Band A check failed
  3. re-run every Band A check  (not just the one you touched)
  4. all green?  → surface Band B, stop
     not green?  → next pass

after pass 3 with anything red:
  STOP and escalate with the specific criterion and why it resisted.
  Do not attempt a fourth pass.
```

**Step 3 is not optional.** Re-run *all* of Band A after every fix, because the round-42
finding was a fix that broke its own precondition — the constraint was right and could not be
reached from the state it was written for.

---

## THE FROZEN-SCOPE RULE — this is the part that makes it terminate

> **A defect you find during this loop that is NOT on the Band A checklist gets RECORDED, not
> FIXED.**

Write it to `docs/found-not-fixed.md` with what you saw and what it would take. It becomes the
input to the next loop's checklist. **The scope is fixed at the loop's start and cannot grow
inside it.**

This is the rule that was missing. `brain/00`: *complexity is the enemy, and it is
incremental* — and so is scope. Every round of 34–42 was individually justified and the
sequence had no end.

**Two exceptions, and only two:** something that **loses data**, or something that **puts JD's
LinkedIn account at risk**. Those you fix immediately and report. Everything else is recorded.

---

## THE REPORTING RULE

**One report, at the end of the loop. Not one per finding.**

It states, in this order:
1. Band A: five idempotence numbers, two `people` counts, the detector's output, the coverage
   count.
2. Band B: what is waiting on JD, phrased as a decision he can make in one pass — **a concrete
   instance beside every rate.** ("32% came in on a bare token" was a threshold argument;
   "HEAD WAITER is the best contact at David" was a decision.)
3. `found-not-fixed.md`: what you saw and left alone.
4. What you could not verify, and why.

**A report describes what happened; the repo has to describe what would happen again** — your
own rule, and it applies to this report too.

---

## WHAT IS EXPLICITLY OUT OF SCOPE — do not build these

Frozen so the loop cannot expand into them:

- The three Notion views *(spec'd; JD builds them in the UI, the API cannot)*
- `last_touched_on` writes *(needs JD's workflow, not code)*
- Scheduling the careers lane *(real and valuable — next loop, not this one)*
- Any new scoring signal, weight, or component
- Any refactor not required by a Band A criterion
- Anything discovered in a capture, report, or dataset that JD did not ask for

That last one is round 38's rule: **an insight found while researching a request is not part of
the request.** Record it and move on.

---

## SUCCESS

The loop has succeeded when JD can run the next batch and the only thing standing between the
CSV and a chase list is **his attention on two Sales Nav sessions.**

Not "a perfect system." **A system whose remaining imperfections cannot change what he does
next.**
