# Answers — both decisions, and four corrections you were right about

**Your report is accepted, and three of its findings are corrections to me, not to the loop.**
You ran Band D's queries instead of describing them, and you found a checklist defect before
writing code. **That is the whole purpose of the first-action requirement.** Keep that posture.

---

## DECISION 1 — E3 gets fixture inputs. Option (i), with a boundary.

You argued (i) and you are right: **an acceptance test that leaves all four Band A columns
blank-correctly validates the half of the pipeline that already worked.**

**But a fixture that enters at the wrong depth proves the fixture, not the pipeline.** The rule:

> **The fixture may replace DISCOVERY. It may never replace COMPUTATION or PROJECTION.**

Discovery is what this loop puts out of scope — *finding* a careers URL, *obtaining* a headcount
reading. Everything downstream of the input arriving must execute for real.

| seed this | at this boundary | so that this runs for real |
|---|---|---|
| a **recorded ATS payload** | the careers-fetch return | classifier · desk-role math · `nyc_jobs_*` · `Desk Jobs` |
| **two headcount readings, two dates** | the same write the measurement lane calls | `NYC Band` · `Intensity` · **and `NYC Δ`** |

**Two readings, not one.** `prev_nyc_employees` is non-null on 4 of 134 rows — which means the
delta path is close to untested on the live board. **A single seeded reading leaves `NYC Δ` blank
and E3 cannot tell blank-correctly from blank-wrongly for it.** That is the exact confusion E3
exists to eliminate.

**Do not** write `nyc_employees` or `Desk Jobs` into a column directly. If the value arrives
downstream of the code that was supposed to produce it, the test is green by construction.

**And do (ii) as well.** The report states, per column, **which inputs were seeded and at which
boundary.** A fixture-fed test that does not say so reads as end-to-end when it is not.

---

## DECISION 2 — Band D gets a third category. Membership is proven per row, not per pattern.

**The category is legitimate.** A company deliberately left unscored by a recorded ruling is not
a company the projection dropped, and D2 should not halt on it.

**But "consistent with round 28" is the reasoning that produced AO1.** You said it yourself: you
did not name-match all 39, and **39 ≠ 40 ≠ 41.** So:

**D1's deliverable is a name-level reconciliation. Every row in exactly one bucket:**

```
deferred by round 28        — cite the ruling, name the row
tombstoned                  — Pro Padel League, and any other
NEITHER                     — ← D2 fires here, and only here
```

**One row in the third bucket is the finding that outranks the loop.** Zero rows in it and Band D
is green, permanently, with the list on the record.

**Separately, name the 39-vs-41.** Two rows appear to have a `notion_page_id` and no `fit_score`
— *projected but unscored*. **A row on JD's board with no score is visible and ranks nowhere.**
Resolve which views it appears in. If the overlap is different from what I've inferred, say so —
I'm reading your counts, not the store.

---

## E1 — you found a checklist defect. It is mine, and it is BI3's second instance.

**You are right that "all green in 3 passes" cannot depend on a decision JD hasn't made.** I
wrote a checklist that required something the same checklist gated on a human. That is exactly
the contradiction you halted on in round 55, in a new place. **Your proposed definition is
adopted verbatim:**

> **E1 is green for pass purposes when the simulation is done and the movers report is
> delivered** — the rate with one concrete company beside it. **Apply · oracle · re-freeze
> execute on JD's go. E3 is re-verified after the apply, not before.**

**Two instances of the same defect from me in ten rounds. The pattern: I write a gate and a
deadline into the same document without checking whether the gate can clear inside it.**

---

## THE REST — accepted, with one correction to my own framing

**Pre-register the yields (3b). Accepted, and my round-61 framing oversold it.** I wrote *"the
prior measurement exists; the delta is arithmetic."* True for 4 rows. **The re-measure history —
and the rule that re-binding a Sales Nav URL clears the prior — means almost nothing has one.**
Register the expected counts *before* the run, per BC2: ~4 populated on `NYC Δ`, ~48 on
`Desk Jobs`. **A band that hits its pre-registered number is green. Discovering the number
afterward and calling it expected is not a test.**

**The four `months_*` fields (3e). Near-forced, and knowing that going in is correct.** RETIRE
from the board; the store keeps them. **If E1's velocity refinement later gives them a real
producer, they come back — a retired column is a display decision, reversible.**

**`Reach`'s third state.** You're right that blank collapses *never-searched* with
*searched-none-found*, and AP1 says those are different facts. **That is blank-≠-zero in a new
place and I am not waving it through — but it is not this loop's work.** Record it in
`found-not-fixed.md` with the fix named (a company-level `contacts_searched_at`), and **state the
collapse explicitly in the report** so nobody reads a blank `Reach` as "we looked."

**The view-name garble is my error.** Nine views. The ninth is `HEALTH · NYC BAND` — my
middle-dot separator made it parse as a tenth. **Read the board, not my list.**

---

## THE FOUR UNVERIFIED — two are approved work, one is mine to fix

**1 · The live Notion board.** You're right to invoke AO1 against your own evidence: a build
report is the account, not the artifact. **Do the read-only pass — views, properties, row count —
before Band A writes.** No writes. If it disagrees with the report, that outranks Band A.

**2 · The nine views' filters against the spec.** Approved, same timing, and cheap. **You are
about to feed columns those filters select on; a filter that differs from spec means your writes
land somewhere other than where the report says.**

**3 · The 39 Research rows.** That's D1 above.

**4 · Round 45's gap is real and it is mine.** The log jumps 44 → 46 because round 45 was voided
by AZ3 and I removed it rather than tombstoning it. **A ruling log with a silent hole is a log
you cannot trust the monotonic check on** — which is precisely the check you ran. **A tombstone
entry is appended.** Pull the brain again before pass 1.

---

## GO

**Pass 1: pre-register the yields, run the two verification passes, then D1's reconciliation,
then A, B, C, E in order.**

**Stop and escalate only on:** a row in D's third bucket · the board disagreeing with the build
report · a filter differing from spec. **Everything else recorded, not fixed.**

**One report at the end.**
