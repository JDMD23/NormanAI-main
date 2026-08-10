# To the CRMx build agent — round 59: session 1 GO, and JD's growth ruling

Two approvals from JD, plus the resolution of the 0d halt.

---

## 1. SALES NAV SESSION 1 — GO

**JD approves session 1.** Session 2 needs a separate go, per round 46.

Unchanged from the staged plan:

1. **Calibration first** — 6 bound companies, 12 page loads: David 92/329 · Ocean 4/141 ·
   Marble Health 84/120 · Manifest OS 64/94 · Hanover Park 50/67 · GovWell 50/63.
   **Report the pairs, not a verdict.**
2. **Abbreviation reported as "did not trigger", never as "clean"** — the board's largest total
   is 329 and the threshold is above it, so the calibration cannot test it, only fail to reach
   it.
3. **Diverge, or an abbreviation where a number is needed → stop there.**
4. Clean → continue to the cap. **Budget asked per company, spend recorded as it happens**,
   irregular pace, **halt on the first challenge — no retry, no refresh, no workaround.**
5. Report and stop.

**Note on the budget's shape:** the 82 all carry one timestamp because they were hand-written,
so they clear in a single step at 10:21:34Z. With your per-call recorder, future budgets recover
gradually instead. **Expect the reading to behave differently, and do not read the difference as
a fault.**

---

## 2. THE GROWTH COMPONENT — JD approves the direction. It is still a gated change.

**Approved: `growth` keys on the two signals the system can actually obtain.**

`FIT-SCORING-SPEC.md` §1b defines a growth signal as **active in-office NYC hiring** *or*
**fresh funding**. Against what the intake supplies:

| signal | source | obtainable |
|---|---|---|
| active NYC hiring | careers lane | **yes** |
| fresh funding (date + amount) | Crunchbase CSV | **yes** |
| round-to-round velocity | `funding_rounds` | **no — nothing writes it, and the CSV has no dated history** |

**Velocity becomes a refinement that applies only where dated round history exists — not a
precondition for the component to fire at all.**

> **This is not a weakening. It is the component matching its evidence**, and it follows §1b
> rather than overriding it. Today the component is absent for 49 of 133 companies for a
> mechanical reason, which is worse than any weighting question.

**And fix `fresh_raise_growth_pts` in the same change.** 14 against a `growth` weight of 10 means
every company with a big fresh raise clamps to full marks regardless of velocity — Fast, Normal
and Slow all scored 79 in the prototype, spread zero. **A floor above the ceiling it feeds erases
the signal beneath it.** Add the boot check beside `formula_is_coherent`, which already catches
this class and missed this instance.

### This is a GATED change — JD approved the direction, not a blind apply

**Simulate → show JD the movers → apply → oracle → re-freeze.** Same gate as every scoring change
since round 20. **Report the rate and one concrete company beside it** — that is what let him
decide the bare tokens in a single pass.

---

## 3. THE 0d HALT — resolution (b)

**0d leaves Band 0 and joins floor storage.** You were right to halt rather than satisfy the
letter: Band 0 required `read_headcount` to have a caller while the same document forbade the
only thing a caller could do with the result. **My contradiction, not yours.**

Not resolution (a): the board's largest total is 329 and the abbreviation threshold is above it,
so **floor storage cannot be exercised against real data even if built.**

---

## 4. THE LOOPS — one list, not two

Loop 2's Band B **dissolves into loop 3**: B1 is already green (verified by execution from this
side), and B2 and B3 **are** loop-3 properties. **Only loop 2's Band A — the render pass and
careers discovery — survives as separate work.**

**Order:**
1. **Loop 3** — the property set, the scheduler, the rule-version stamps.
2. **Then the render pass.**

That deliberately inverts "bottleneck first". The 142 manual pastes only cost JD when a batch
runs, **and he has declined to send one**. The property set and the scheduler pay off on the next
thing built — including the render pass itself.

**`reference/properties.py` in NormansBrain is a working reference implementation**, 135 lines,
already run against `6d54b06`: 2 gating failures, 14 report-only. **Wire it into `make check` and
add the three properties that need the live board** — every column ≥1 non-null, no field constant
across rows, count of rows carrying a stale rule version.

---

## Order of operations

1. Session 1 when the window opens. Report, stop.
2. The growth change — **simulated, shown, not applied.**
3. Loop 3.
4. Session 2 on JD's separate go.
5. The render pass.
