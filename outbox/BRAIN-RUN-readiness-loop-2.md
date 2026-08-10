# The brain ran loop 2 — Band 0 and Band B1, executed not described

Run against `origin/main` at `ab1f00d`. **Everything below was executed. No claim here rests on
reading the code.** Band A (the render pass) is not runnable from here — no board data, no
domains — so it is untouched and yours.

**Compare your pass-1 results against these.**

---

## BAND B1 — THE STAGE LENS WORKS. The predicted failure is not one.

This was called the highest-probability failure in any real batch. **It isn't.** All three
branches fire and discriminate correctly.

**Test 1 — hold heads CONSTANT at 18, vary only the stage.** Only the lens should move.

```
pre-seed    64
seed        64
series-a    59
series-b    55
late        54
```

Correct: 18 people is far above a pre-seed expectation (4) and far below a late one (90).
**10 points of discrimination on stage alone.** The pre-seed/seed tie is the ratio cap at 2.0
saturating (18/4 and 18/8 both exceed 2.0) — **the cap working, not a bug.**

**Test 2 — heads AT each stage's own expectation (4 / 8 / 18 / 45 / 90).**

```
pre-seed    45
seed        50
series-a    59
series-b    66
late        71
```

A 26-point spread for companies all equally "on track for their stage" — **and that is JD's
ruling, not a defect.** §1a: *"Size leads; growth amplifies"*, from him ranking the 40-NYC
Series B above the 15-NYC Series A above the 6-NYC seed.

**Early rocket (W3) — fires, and every gate discriminates:**
```
qualifies (seed, 12mo, $6M, 5 jobs/10 heads)   54
too old (20mo)                                 50
underfunded ($2M)                              50
not hiring hard (1 job)                        39
```

**HQ-conditional stall — fires, and every gate discriminates:**
```
qualifies (series-b, 8 heads, 0 jobs, NYC HQ)  19
too many jobs (5)                              45
too many heads (30)                            44
early stage (seed)                             30
```

**B1 is green. Spend pass 1 elsewhere.**

---

## THE FINDING NEITHER BAND PREDICTED — and it is the answer to "is the system ready for a batch"

**No. Here is why.**

**The `growth` component depends on `funding_velocity`, and no code path in this repo has ever
produced that field — in any commit.**

Executed:
```
velocity None, no funding date          growth MISSING
velocity None, round 60d ago            growth MISSING     ← recency alone is not enough
velocity None, round 400d ago           growth MISSING
velocity None, BIG raise 60d ago        growth PRESENT     ← only a fresh_raise rescues it
velocity 'Fast'                         growth PRESENT
```

And traced across the full history:
```
compute_velocity      called only by velocity.py and its own tests — in EVERY commit
set_funding_velocity  called NOWHERE, not even in tests
crunchbase_csv.py     does not produce velocity
tools/*               only label_prep, and it READS
```

**Yet the frozen eval corpus has `funding_velocity` on all 32 evidence records** — 19 Fast,
11 Normal, 2 Slow, with `velocity_basis` of `measured` / `founded_anchor` / `collapsed_rounds`,
which is exactly `velocity.py`'s vocabulary.

**So the board's velocity values were written by hand, by a path that is not in the repo** — the
same pattern as the 82 hand-written throttle events and the 85 hand-pasted careers URLs. **Third
instance.**

### Why this is the batch-readiness blocker

1. Companies arriving from a CSV get `funding_velocity = None`.
2. For them, `growth` is **MISSING** unless they happen to have a big fresh raise.
3. Missing → **excluded and renormalized** (correctly, per Unknown ≠ 0).
4. **So new companies are scored by a different formula than the existing 133** — silently, with
   the growth weight redistributed across their other components.

> **A batch would not be scored wrongly. It would be scored by a DIFFERENT FORMULA than the
> board it joins — and the board's ranking is the product.**

### And the eval cannot catch it

The frozen corpus has velocity on **every** record. So the oracle validates the *with-velocity*
path and **never exercises the without-velocity path that every new company will take.** The
gate's own `blind_to_note` already says it can only validate signals present in its frozen
evidence — **this is that limitation with a live consequence.**

### The observables, before anything else in pass 1

```sql
SELECT COUNT(*) FROM companies WHERE funding_velocity IS NOT NULL;   -- of 133
SELECT velocity_basis, COUNT(*) FROM companies GROUP BY 1;
```
**And: how many currently carry `growth` in their missing list?**

### The fix is not "wire up velocity" — decide first

`compute_velocity` needs dated rounds. **How many of the 133 have enough funding-round history
for it to return anything?** If the answer is "few", wiring it produces `None` anyway and the
real question is whether `growth` should key on something a CSV actually supplies.

**Do not wire it before answering that.** Wiring a computation whose inputs are absent is how
`read_headcount` got built.

---

## BAND 0 — confirmed, with one correction to my own report

`velocity` is **not** a regression. I checked the full history: `compute_velocity` has had no
caller outside its own module and tests **in any commit**. It was never wired, and the corpus
values came from outside the repo.

The other three stand: `changes_tags`, `status_owner`, `read_headcount`.

**And one methodological note for B3:** of 30 unreferenced public functions, roughly half are
pydantic validators the framework dispatches by decorator. **"No textual reference" is not "never
invoked" for framework-dispatched code** — the inverse of the export-is-not-a-call-site error,
and just as easy to make. The permanent check must exclude them by rule.

---

## WHAT I DID NOT RUN

- **Band A** — no board data or domains here. Entirely yours.
- **B2's second half** — "distinct values across the board" needs the DB. I answered only "is it
  read by the scorer."
- **Anything against the live database.** Every number above is from synthetic input against the
  committed scorer.
