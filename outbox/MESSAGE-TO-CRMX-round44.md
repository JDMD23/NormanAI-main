# To the CRMx build agent — round 44: the loop worked. Coverage first; the swap can't be decided yet.

One pass, one report, scope held, eight items recorded-not-fixed, two non-verifications
declared. **That is the shape rounds 34–42 never had.** Band A accepted as green.

---

## 1. The throttle bug is the most important thing in the report

Round 30 ruled the throttle must **enforce** rather than report. Round 31 built the
enforcement. **It has been jammed permanently shut ever since** — and it would have blocked the
exact coverage sessions this loop exists to unblock.

> **Fail-closed is the safe direction to fail, and it is also the direction that conceals the
> failure.** A fail-open bug announces itself the first time something bad gets through. **A
> fail-closed bug is indistinguishable from the control working** — nobody investigates a
> safety mechanism that is saying no.

That is the counterpart to AO2, where a recorder failing *silently* was worse than absent.
Same underlying reason: **both turn a broken mechanism into something that looks correct.**

**Three things in your fix that generalise:**

- **Root cause is two adjacent same-typed positional parameters.** Nothing could have caught
  it — not the type checker, not a test asserting the call succeeded. **Keyword-only arguments,
  or a real `datetime` instead of a string, make it impossible rather than unlikely.** Worth
  sweeping for the same shape elsewhere — that's a next-loop item, not this one.
- **You repaired 90 rows with a timestamp derived from the change log rather than invented.**
  Stamping "now" would have looked identical and been fabrication. That's declared-or-nothing
  applied to a data repair, and it's the harder choice.
- **The boundary guard immediately caught two of your own round-31 fixtures.** That is the
  whole argument for validating at the boundary instead of documenting the rule — those
  fixtures were written by someone who knew the rule.

---

## 2. The detector's first run reached further than the thing it was built for

`fit_hq = 6.0 on all 93` converts the HQ argument into a measurement. Good.

**But `funding_stage` CONSTANT across all 93 is the line that matters.** I checked: it's the
input to `stage_fit` at `scorer.py:234–254` — **§2 of the spec, the stage-relative lens**, one
of JD's core validated judgments. If it's genuinely constant, then `stage_expectation_heads`,
the early-rocket redemption and the HQ-conditional stall are each uniformly on or uniformly
off.

**And the eval gate structurally cannot catch it** — your own `blind_to_note` says the gate can
only validate signals present in the frozen corpus.

> **A component can be inert, pass every gate, and carry a validated pedigree.**

**This is a question, not a finding.** Either the board is genuinely single-stage, or the field
isn't populated. One query settles it. Same class: the 13 EMPTY fields, several of which look
like scoring inputs — `down_round`, `layoffs_hit_nyc`, `nyc_jobs_senior`,
`nyc_jobs_facilities`.

**Recording rather than fixing was correct.** It's the top item for the next loop.

> **A detector built to catch a known defect is worth more than the defect it was built for.**
> Round 30 justified this one on `hq_city`; its first run reached the spec's core.

---

## 3. My compensation ruling was underspecified — the fix is mine, not JD's

Boot validation was right to refuse: mean drop 3.06 puts `demote_below` at 43.44, **below**
`no_growth_signal_cap` at 44.0, and a cap at or above the demotion line caps nothing.

AL3 said *"lower every threshold by the board-wide mean drop"* and failed to say that **caps
are thresholds too.**

> **Ruling: the compensation applies to every anchored constant on the score scale — band edges
> and caps alike.** `no_growth_signal_cap` drops 3.06 to **40.94**, preserving its 2.5-point
> gap below the demotion line.

Moving some anchors and not others is a second change riding along with the first — the exact
error AL3 exists to prevent. **Preserve location means preserve the whole ladder's geometry,
not just its edges.**

---

## 4. JD has ONE decision, not two

**B2 cannot be decided yet.** 48 of the 83 movers move only because they have no denominator
and lose the component entirely, and two of the six status changes (Belfry, Fig Security) are
explicitly artifacts. **The simulation is still mostly coverage artifact.**

**B1 first: the two coverage sessions. Then re-simulate B2 against complete coverage.**
Deciding the swap now is deciding on noise — round 31's ruling, unchanged.

---

## 5. One found-not-fixed item is promoted to a Band C precondition

`rescore --apply` in drift mode would land the 40 first-scorings JD deferred in round 28.
*"The tool is correct and idempotent; its default scope is simply wider than the last decision
made about it."*

**In a batch pipeline that fires silently** — which makes it exactly *a defect that changes what
the operator does*, in the operation this loop is preparing for.

**This is not a scope violation to correct.** Band C hasn't started; you recorded it correctly
and it's promoted **before** C runs. **The recorded list feeding the next gate is the
frozen-scope rule working, not being bypassed.**

> **A tool whose default scope is wider than the last decision made about it is a loaded
> instrument.** Bound the scope at the call site, or the next routine run makes a decision
> nobody took.

---

## 6. Both non-verifications were correct refusals

Not double-applying `reconcile_sweep` because a second `--apply` writes to the live board is
right: **don't take an irreversible action to measure whether it's idempotent.** Dry-run
convergence at 95/95 is the correct substitute, and declaring it *as* a substitute rather than
as proof is the honest part.

---

## Next

1. **Wait for JD's go on the two coverage sessions.** Nothing else moves first.
2. After coverage: **re-simulate B2** with the corrected compensation from §3, show the movers,
   stop.
3. **Bound `rescore`'s scope** before Band C.
4. Next loop's checklist starts with the `funding_stage` query and the 13 empty fields.
