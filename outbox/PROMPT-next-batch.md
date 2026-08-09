# CRMx — run the next batch

Two phases. Do not start phase 2 until phase 1 reports `without denominator: 0`.

---

## PHASE 1 — finish the current board (52 companies)

Already staged and agreed. Nothing new here.

1. **Calibration first**, 6 bound companies, 12 page loads:
   David 92/329 · Ocean 4/141 · Marble Health 84/120 · Manifest OS 64/94 · Hanover Park 50/67 ·
   GovWell 50/63
   **Report the pairs, not a verdict.** Abbreviation reported as **did not trigger**, never as
   *clean*.
   **Diverge, or an abbreviation where a number is needed → stop.**
2. Clean → continue to the daily cap. Budget asked per company, spend recorded as it happens,
   irregular pace, **halt on the first challenge — no retry.**
3. Report, stop. **JD's go before session 2.**
4. After both: **re-run the coverage ledger. It must read `without denominator: 0`.**

---

## PHASE 2 — the new batch

```bash
uv run python -m norman.tools.session_start    <db>
uv run python -m norman.tools.ingest_csv       <csv> <db> --added-from crunchbase:2026-08
uv run python -m norman.tools.careers_lane     <db> --apply
uv run python -m norman.tools.rescore          <db>            # PREVIEW — see the gate below
uv run python -m norman.tools.reconcile_sweep  <db> --apply
uv run python -m norman.tools.contacts_lane    <db> --print-query
uv run python -m norman.tools.contacts_lane    <db> --apply <response.json>
uv run python -m norman.tools.chase            <db> --limit 20
```

**One hazard, and it is the only thing in this phase that can go wrong quietly.**

`rescore` has **no scope flag** — `--apply` writes every mover it computes, including the 40
first-scorings JD deferred in round 28. **Do not run `rescore --apply` unreviewed.** Run the
preview, show JD the mover list, and apply only after he has seen it. If any of the 40 appear,
say so explicitly.

**The new companies will score on the current formula**, `hq_source = hq_city`, same as the
existing board. That is consistent, not correct — see below.

---

## GATES — three, and each stops the run

| gate | what stops |
|---|---|
| **Calibration diverges** | stop before spending the other 49 |
| **First challenge / captcha** | stop the session, no retry, report |
| **Rescore movers** | JD sees the list before anything is written |

---

## AFTER THE BATCH — one decision waiting for JD

**The `hq_source` swap.** With coverage complete, re-simulate it with the round-44
compensation — **every anchored constant moves by the board-wide mean drop, band edges AND
caps**, so `no_growth_signal_cap` moves with `demote_below` and their gap is preserved.

**Show him the movers and stop.** Do not apply. This time the list is signal, not coverage
artifact, which is why it waited.

---

## NOT IN THIS BATCH

Recorded, deliberate, do not build:

- The reachability check (`no callers` detector)
- The `funding_stage` question and the 13 empty fields
- Floor storage — there is no field that can hold a bound
- The three Notion views — JD builds them in the UI
- `last_touched_on` writes
- Scheduling the careers lane

**These are the next loop.** If you find something new during the batch, **record it in
`found-not-fixed.md` — do not fix it.** Two exceptions only: data loss, or risk to JD's
LinkedIn account.

---

## REPORTING

**One report at the end of each phase. Not one per finding.**

State: what ran, the numbers, what is waiting on JD, what you recorded and left alone, and what
you could not verify.
