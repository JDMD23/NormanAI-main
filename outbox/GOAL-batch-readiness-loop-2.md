# GOAL: make the system READY for a mixed batch — loop 2, frozen exit criteria

**To the CRMx build agent.** JD's decision: **no batch yet.** He wants the system able to receive
a batch and execute *elite research and scoring* before one arrives.

**This supersedes `PROMPT-next-batch.md`.** Same loop discipline as last time — it terminated at
pass 1 and that format holds.

---

## THE GOAL

> **A mixed-stage batch can arrive and be researched and scored without a human catching
> anything wrong.**

The first batch was all Series A and every company's careers URL was pasted by hand. **Neither
of those conditions holds for a real batch**, and the system has never been asked to work
without them.

---

## THE CHECKLIST IS FROZEN. You may not edit it.

Ordered by BF3: **the list opens with the measured operator bottleneck**, not with the tractable
item.

### Band A — the bottleneck. 142 manual pastes per 200 companies is the entire cost of a batch.

**A1 · The K1 render pass.** On the standing list since round 4, never built. It unblocks two
things at once: the **31 boards that cannot be read** and the boards that **cannot be found**.

**A2 · Careers-URL discovery, measured — not promised.**
Baseline: **2 of 12** found by conventional paths. Run discovery with the render pass over the
same 12, then a fresh 12. **Report the fraction found. Do not commit to a target.**
Every URL found carries how it was found; every failure records *why*, not just that it failed.

### Band B — scoring readiness. Cheap, no external calls, and it is the "elite scoring" half.

**B1 · Exercise the stage-relative lens. It has NEVER run against varying input.**
All 133 companies are Series A, so `stage_expectation_heads`, the early-rocket redemption and
the HQ-conditional stall have never been exercised.
**Put synthetic Seed / A / B / C / D rows through the scorer and report what each does at each
stage.** No batch required. This is the highest-probability failure in any real batch and it is
testable today.

**B2 · Trace every scoring input to whether it is read, constant, or empty.**
The detector found 6 constants and 13 empty fields. **Now answer the question it raised: which
of them does the scorer actually READ?** `down_round`, `layoffs_hit_nyc`, `nyc_jobs_senior`,
`nyc_jobs_facilities` look like inputs. **A scoring input that is always empty is an inert
component, and we would not know.** Report the table: field · read by scorer? · distinct values
across the board.

**B3 · The reachability check.** For every public function in `src/`, is there a caller outside
its own test file? **Three built-but-unwired mechanisms have been found by hand** — the throttle
Budget, `workplace_contact`, `read_headcount`. All three had green tests. **We do not know what
else is dead.** Mechanical, and it is the generalised form of a grep that has caught two live
defects.

### Band C — human-gated. Halt and surface; do not proceed through these.

**C1 · Sales Nav coverage**, 52 companies, JD's go per session, calibration first. Unchanged
from the staged plan.
**C2 · The `hq_source` swap** — simulate after C1 with the round-44 compensation (every anchored
constant moves, **caps included**), show JD the movers, **stop**.

---

## THE LOOP

```
budget: 3 passes. Not 4.
each pass: run all of Band A and B → fix only what failed → re-run ALL of A and B
all green → surface Band C, stop
after pass 3 with anything red → escalate the specific criterion. No fourth pass.
```

**Frozen scope: a defect found that is not on this checklist goes to `found-not-fixed.md`.
Recorded, not fixed.** Two exceptions only — data loss, or risk to JD's LinkedIn account.

**One report at the end. Not one per finding.**

---

## EXPLICITLY OUT OF SCOPE

- Scheduling the careers lane *(real, valuable, next loop — the render pass changes what should
  be scheduled)*
- Floor storage — no field can hold a bound *(latent; needs a company large enough to abbreviate)*
- The three Notion views · `last_touched_on` writes
- Any new scoring signal, weight or component
- **Ingesting any CSV.** This loop does not touch new companies.

---

## THE HONEST CEILING — say this in the final report

**B1 makes the stage lens FUNCTIONAL. It cannot make it VALIDATED.**

JD's eval corpus is entirely Series A, so his labelling exercised the components his corpus
could vary — **the stage lens was frozen beside them without ever being tested.** Synthetic rows
prove the code does something sensible; **they cannot prove it does what JD would judge.**

**Closing that gap needs an hour of his time, not more engineering: he labels a handful of
non-Series-A companies.** Put that in the report as the one thing engineering cannot supply.

---

## SUCCESS

A batch can arrive and the only human cost is **JD's attention on Sales Nav sessions** — not 142
pastes, and not his judgment being needed to catch a scoring component that was never tested.
