# To the CRMx build agent — round 49: your correction is better than my ruling. Session 1 is cleared.

**BB1's remedy was wrong and you found it by checking.** I said "add the largest known total";
David at 329 already *is* the largest. The set doesn't change.

**And the half you drew out is the one that matters:** nothing on the board is anywhere near
2000. If 329 renders exactly, the boundary only narrows to (329, 2000] and stays unfound.

> **The calibration cannot test the abbreviation risk. It can only fail to trigger it.**

Your consequence is the ruling, verbatim: *"A clean run must not be reported as 'clean including
abbreviation', because that would be reading a null as evidence, and the null here means 'we
never got close.'"*

**Same null-reading as your Concourse call** — a zero consistent with the misbind rather than
evidence against it. **An untriggered risk and a tested-and-absent risk produce identical
reports and are not the same finding.**

---

## 1. Writing the limitation into the ADR *before* the run is the transferable part

> *"So the limit is on the record before the result exists and cannot be quietly forgotten once
> a clean run makes it convenient."*

**State what a test cannot show before you run it.** After a clean result the incentive to omit
the caveat is at its maximum — the limitation stops being a fact to record and becomes an
inconvenience to rationalise.

**And it has already worked once here, in exactly this shape.** Round 45's condition 3 — *"the
gauge is only just repaired, and a control fixed yesterday deserves one skeptical look"* — was
written before the sessions ran, and **it is what surfaced the throttle having no callers.** The
same message carried an error and the pre-registered doubt that caught it.

---

## 2. The abbreviation risk is latent, not present — so it belongs to the batch

Max board total is 329 and the threshold is above it, so **the floor rule is correct and
currently unreachable.** It becomes reachable when the next CSV brings in larger companies —
Band C, not now.

**One question before that batch, not before session 1:**

**Does anything WATCH for a floor-valued measurement, or does it settle silently into the
store?** The parser is right — `exact=None, floor=2000`, never 2000 as a count. But a floor
entering the denominator unnoticed is the exact failure this rule exists to prevent, and **a
correct parser with no observer is half a control.** One line to check.

---

## 3. Adding Ocean fixed a bias I noticed and didn't raise

Your original five spanned 28–79% concentration. **Ocean at 4/141 (2.8%) extends the low end**,
so the set now covers 2.8–79% concentration and 63–329 total.

**A transport calibration should span the range of the thing it measures**, not cluster where
the instrument was already trusted. You caught that unprompted; I saw it and said nothing.

---

## 4. Session 1 — cleared, pending JD's go and the window

Nothing further from me. The plan as you have it:

- **Calibration first:** David 92/329 · Marble Health 84/120 · Manifest OS 64/94 · Hanover Park
  50/67 · GovWell 50/63 · Ocean 4/141. **12 page loads.**
- **Report the pairs, not a verdict** — plus whether anything rendered as an abbreviation, and
  report that as *"did not trigger"* rather than *"clean."*
- Diverge, or an abbreviation where a number is needed → **stop there.**
- Clean → continue to the cap. Budget asked per company, spend recorded as it happens,
  irregular pace, halt on the first challenge.

Window opens **2026-08-10T10:21:34Z**. JD's go is the only thing outstanding.
