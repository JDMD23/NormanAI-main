# To the CRMx build agent — round 45: coverage sessions APPROVED. Go.

**JD approves B1: both Sales Navigator coverage sessions.** 52 companies, ~104 views, two
sessions at the 80/day cap.

**Approved for both sessions, not one** — but report between them rather than running them
back to back. His per-session go was there to protect the account; the throttle now enforcing
and the halt-on-challenge rule do that job better than a second approval click.

---

## Running conditions

1. **Halt immediately on the first challenge, captcha, soft block, or "unusual activity"
   notice.** Do not retry, do not refresh, do not work around it. Report and stop. One retry
   into a challenge is worse than an unfinished session.
2. **The throttle enforces per call now.** Let it stop you. If it refuses, that's the answer —
   don't raise the cap to finish a session.
3. **The gauge is only just repaired.** If the reading looks wrong in either direction, stop
   and say so before spending. A control fixed yesterday deserves one skeptical look.
4. **Report between sessions:** companies measured, views spent, anything that looked off.

---

## After coverage completes

**In this order:**

1. **Re-run A4.** The coverage ledger should read `without denominator: 0`. That number gates
   everything below it — if it isn't zero, stop there.

2. **Re-simulate B2 (the `hq_source` swap) against complete coverage**, with the corrected
   compensation from round 44 §3: **every anchored constant on the score scale moves by the
   board-wide mean drop — band edges AND caps.** `no_growth_signal_cap` moves with
   `demote_below`, preserving their gap.

   **Then stop and show JD the movers.** Do not apply. This time the list will be signal rather
   than coverage artifact, which is the whole reason it waited.

   Report it the way you reported the bare tokens: **the rate, and one concrete company beside
   it.** That's what let him decide in a single pass.

3. **Bound `rescore`'s scope before Band C.** In a batch pipeline, drift mode silently lands the
   40 first-scorings he deferred in round 28. Bound it at the call site so a routine run cannot
   make a decision nobody took.

---

## Not now, but first on the next loop's checklist

**The `funding_stage` question.** One query: how many distinct values across the 93? If it is
genuinely one value, the stage-relative lens — §2 of the spec — is not discriminating, and that
is a bigger scoring defect than the HQ component. Same query for the 13 empty fields: which of
them are scoring inputs?

**Do not start it now.** It stays recorded until coverage and B2 are through — the frozen scope
is what made this loop terminate, and it holds in both directions.
