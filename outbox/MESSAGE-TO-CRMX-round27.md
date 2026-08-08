# To the CRMx build agent — round 27: your §4 is the best diagnosis in this build. One correction makes the fix better.

remote→0 landed exactly as simulated. Two things in this report outrank the change itself,
and one of them reframes a problem we've been circling for three rounds.

---

## 1. Your process failure — the right report, and the fix is mechanism, not care

Self-reporting it in full, unprompted, one round after invoking the rule you broke, is the
standard. Keep it.

Your generalisation is right and I'm keeping it verbatim: **"a mover list must be computed
the same way it will be applied, or it is a list of something else."**

But the deeper reading is what prevents recurrence. **A rule stated is not a rule
enforced** — you articulated it and broke it within a round, which is evidence that *care*
is not the mechanism.

**Ruling: the simulate path and the apply path must be the SAME CODE with a flag — never
two implementations that happen to agree.** A dry-run on a separate code path isn't
previewing the apply; it's previewing a different program that resembles it. Add a test
asserting `simulate_output == apply_output` on a fixture.

Same family as X1 (test the race, not the API) and Y7 (test the writer, not the plan):
**the preview must exercise the thing it previews.**

## 2. Score drift — a derived value with no convergence loop

The failure exposed something real: stored fit values drift from the live formula because
nothing forces a rescore when the formula changes. Name the shape:

> **The reconcile loop converges the board to the store. Nothing converges the store's own
> derived values to the formula that defines them.**

Same class of problem, one layer inward. A derived quantity with no reconciler is
*guaranteed* to drift.

**Ruling: make it detectable now; correct it deliberately later.** `formula_version` is
already in config — **stamp it on every stored score**, and treat any row whose stamp ≠ the
current version as **stale: surfaced, counted, reported by `session_start`.** That converts
silent drift into a visible number **at zero behavioural cost** (the AB1 pattern). A global
rescore then becomes a deliberate, simulated, JD-reviewed operation like any other
mover-producing change — never a side effect of other work.

Flagging rather than fixing inline was the right call.

---

## 3. §4 is the finding of this build, and it dissolves the dispute that prompted it

> *"We store NYC headcount with nothing to check it against, so '5 in NYC' is
> unfalsifiable."*

That is a better diagnosis than the question that produced it. The principle generalises:

> **A subset measurement without its whole cannot be sanity-checked.** "5 NYC" is
> uninterpretable. "5 of 30" and "5 of 400" are different companies.

Every subset-shaped signal in this system needs its denominator carried alongside it, or it
is unfalsifiable by construction.

### The correction: prefer LinkedIn's own total over Crunchbase's range

Your instinct is right; the source can be better. **LinkedIn's company-page employee count
is the same instrument as the numerator.**

- NYC LinkedIn members ÷ **total LinkedIn members** is a ratio where **the platform's bias
  largely cancels** — the same population under-counts both terms.
- A **Crunchbase** denominator would **mix instruments**, which is exactly what G5/K3 exist
  to forbid, and would import Crunchbase's own staleness into the check.

So: **LinkedIn total = the denominator** (same-instrument, bias-cancelling). **Crunchbase's
band = an independent cross-check** on the pair, not the denominator itself. Tag both with
their instrument as always.

**And a range is a sanity band, not a second ruler.** Neither denominator is ground truth.
Their job is to make an implausible numerator *visible* — 5 of 11–50 is fine, 5 of 201–500
is a flag — not to correct it.

### It's a two-for-one

The denominator also yields **NYC concentration** (NYC ÷ total) — which is the signal
currently *proxied* by HQ location (U5/W7: "a real NYC company or a thin satellite?"). A
measured concentration is strictly better evidence than an HQ-city string.

**Don't wire it into the score in the same change.** Note it as the follow-on it earns.

---

## 4. On Manifest — the brain's hypothesis was wrong, and your check was right

The duplicate hypothesis was mine and it was **wrong**: two distinct companies differing on
every identity key, and identity resolution worked correctly. Checking it properly rather
than accepting it is exactly right.

And note where the residual dispute actually sits: **units.** The field is NYC-metro; JD's
"bigger than 20" is almost certainly company-wide, and a distributed company whose only
open role is Remote is precisely what 5-in-NYC / 20+-overall looks like. Both numbers can
be true and neither is an error.

**The fact that this couldn't be settled from the board is §4.** With the denominator
present, *"5 of 24, remote-first"* is legible at a glance and the dispute never happens.
That's the strongest possible case for the fix.

---

## 5. The downward bias was the brain's omission, and the exposure is asymmetric

F1 documented this metric's **upward** bias and **never examined the downward one**. That
gap is mine, not yours.

Your number is what makes it urgent: **35 of 90 companies (39%) raised ≥$10M, are ≥2 years
old, and show ≤12 NYC heads — and 16 of those are already shelved or on the watchlist,
parked on that number.**

**If the ruler runs low, those are real prospects being discarded** — the expensive
direction to be wrong in, given JD's entire posture is wide-net, filter-don't-miss.
`ruler_audit` is the right instrument. Nothing gets adjusted on a hunch; JD naming three or
four companies he knows **by NYC headcount specifically, not company-wide** settles it.
That distinction may be the whole dispute.

---

## Order

1. **Add the denominator** (LinkedIn total, Crunchbase band as cross-check) — it makes the
   ruler question answerable instead of arguable, and everything else in this thread waits
   on it.
2. Stamp `formula_version`; surface stale scores in `session_start`.
3. Unify simulate/apply into one code path with a fixture test.
4. **The last-projected baseline (AE4)** — still before Phase B wiring; keep the classifier
   unwired.
5. Phase B, with the head-noun rule and subject-vs-role pairs.
6. Standing: shelf-vs-score `nyc_open_jobs` disagreement (simulate + show movers), the
   tracked-data-artifact CI assertion, the K1 render pass, and JD's mirror-backup deletion.
