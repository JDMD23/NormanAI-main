# GOAL: readiness for a mixed batch — loop 2, grounded in the studies

**To the CRMx build agent.** JD's call: **no batch yet.** The system must be able to receive one
and do elite research and scoring first. **This supersedes `PROMPT-next-batch.md` and the
earlier loop-2 draft.**

Same loop discipline as loop 1 — it terminated at pass 1 and that format holds. **The checklist
is frozen and you may not edit it.**

Every design choice below cites the repo study it comes from. Those studies are in NormansBrain
under `studies/`; **read the two named in Band A before building it.**

---

## BAND 0 — four confirmed bugs, found by running a reachability check over `src/`

I ran the check rather than asking you to. **200 public functions; 30 with no reference in
`src/` outside their own definition.** About half are pydantic validators the framework
dispatches by decorator — not dead. **These four are real:**

**0a · `velocity.py` is disconnected at BOTH ends. This is the significant one.**
```
scorer.py:206        reads company.funding_velocity        ← a scoring input, consumed
velocity.py          360 lines, imported NOWHERE in src/   ← nothing computes it
set_funding_velocity store writer, called NOWHERE in src/  ← nothing writes it
```
**A scoring input that is consumed and never produced.** 19 test references keep it green.
**Observable: how many of the 133 companies have a non-null `funding_velocity`?** If the answer
is "most", something outside the repo populated it and that path needs finding. If "few", the
growth component has been running on a mostly-absent input.

**0b · `changes_tags`** (`operator/changes.py`) — never called. This feeds the board's **Changes**
column, which the "Changed Recently" view filters on.

**0c · `status_owner`** (`entity/company.py`) — never called. Field ownership is the machine-vs-human
distinction reconcile arbitrates with.

**0d · `read_headcount` / `is_measurement`** — already known. No caller, and no field that can
hold a floor.

**Fix these first. They are Band 0 because a readiness loop that leaves a scoring input
unproduced is not measuring readiness.**

---

## BAND A — the operator bottleneck: 142 manual pastes per 200 companies

Opens the list per BF3: **the checklist begins with the measured bottleneck**, not the tractable
item. The scoring work in Band B is cheaper and has cleaner tests, and it is deliberately second.

**A1 · The K1 render pass, built as a CAPABILITY LADDER — not a browser-first fetcher.**

> **`studies/scrapling.md`:** *"Ship capability ladders with visible price tags; never default to
> the expensive tier"* (Fetcher → Dynamic → Stealthy).
> **`studies/orca.md`:** *"Run a fixed, cheap, deterministic baseline unconditionally and
> completely. Treat further tool use as a budgeted, justified exception."*

So: **static HTTP on every company, unconditionally. Browser render only on the static path's
failure, with a call budget.** Not "render everything slowly."

> **`studies/scrapling.md`:** *"Trigger official skills on the failure of the platform's native
> tool — the fallback slot is the highest-value trigger."*

The render pass is a **fallback**, not a default. It already has a home: the 31 boards recorded
as unreadable are its first input, and they are the test set you already have.

**A2 · Careers-URL discovery — measured, not promised.**
Baseline **2 of 12** by conventional paths. Run the ladder over those same 12, then a fresh 12.
**Report the fraction found. Do not commit to a target.**

> **`studies/scrapling.md`:** *"References into volatile external structure are derived data:
> store a fingerprint at bind time, re-derive by similarity on failure."*

**Every URL found records HOW it was found; every failure records WHY, not just that it failed.**
That "why" is the input to the next attempt, and without it the second run repeats the first.

> **`studies/ats-scrapers.md`:** *"The legitimacy of the data source is the ceiling on everything
> built above it."*

**Careers pages are public. LinkedIn is not.** The render pass applies to the first and **never**
to the second — the UI-only, JD-supervised, halt-on-challenge rules for Sales Nav are untouched
by anything in this band.

---

## BAND B — scoring readiness. No external calls.

**B1 · Exercise the stage-relative lens. It has NEVER run against varying input.**
All 133 companies are Series A, so `stage_expectation_heads`, the early-rocket redemption and the
HQ-conditional stall have never been exercised. **Put synthetic Seed / A / B / C / D rows through
the scorer and report what each does at each stage.** No batch required, and it is the
highest-probability failure in any real batch.

**B2 · Trace every scoring input: is it READ, is it CONSTANT, is it EMPTY?**

> **`studies/pandera.md` / `studies/evidently.md`:** validation as **pass/fail gates on the data**,
> not as documentation — and drift detection as a first-class test rather than a report nobody
> reads.

The detector found 6 constants and 13 empty fields. **Now answer the question it raised.**
`down_round`, `layoffs_hit_nyc`, `nyc_jobs_senior`, `nyc_jobs_facilities` look like inputs.
**A scoring input that is always empty is an inert component and nothing would tell us.**
Report the table: **field · read by scorer? · distinct values across the board.**

**B3 · Land the reachability check as a permanent gate.**
Band 0 was me running it once. **Make it part of `make check`**, with the pydantic-validator
false positives excluded by rule rather than by hand.

> **`brain/09`:** *enforce mechanically; persuade only where judgment lives.* Four
> built-but-unwired mechanisms have now been found by hand. A fifth will not announce itself.

---

## BAND C — human-gated. Halt and surface.

**C1 · Sales Nav coverage**, 52 companies, calibration first, **JD's go per session**, unchanged.
**C2 · The `hq_source` swap** — simulate after C1 with the round-44 compensation (every anchored
constant moves, **caps included**), show JD the movers, **stop**.

---

## THE LOOP

```
budget: 3 passes. Not 4.
each pass: run all of Band 0, A, B → fix only what failed → re-run ALL of them
all green → surface Band C, stop
after pass 3 with anything red → escalate the criterion. No fourth pass.
```

**Frozen scope: anything found that is not on this checklist goes to `found-not-fixed.md`.
Recorded, not fixed.** Two exceptions — data loss, or risk to JD's LinkedIn account.

**One report at the end. Not one per finding.**

---

## OUT OF SCOPE

Scheduling the careers lane *(next loop — the render pass changes what should be scheduled)* ·
floor storage · the three Notion views · `last_touched_on` · any new scoring signal or weight ·
**ingesting any CSV. This loop touches no new companies.**

---

## THE HONEST CEILING — put this in the final report

**B1 makes the stage lens functional. It cannot make it validated.**

JD's eval corpus is entirely Series A, so his labelling exercised only the components his corpus
could vary — **the stage lens was frozen beside them without ever being tested.** Synthetic rows
prove the code does something sensible; they cannot prove it does what JD would judge.

**Closing that costs an hour of his time, not more engineering: he labels a handful of
non-Series-A companies.** Name it as the one gap engineering cannot supply.

---

## SUCCESS

A batch arrives and the only human cost is **JD's attention on Sales Nav sessions** — not 142
pastes, and not his judgment needed to catch a scoring component nobody ever tested.
