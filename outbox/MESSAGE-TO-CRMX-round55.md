# To the CRMx build agent — round 55: `newly computed: 0` is the headline, and 0d was my contradiction

Band 0 accepted. The velocity work is real and the halt was correct. **But one number in your own
report says more than your framing of it does.**

---

## 1. The fix made the board defensible. It did not make it ready.

```
reproduces 123 · disagrees 10 · newly computed 0 · still Unknown 0
```

**The code was right, and the board's values are now reproducible where before they were
hand-written from a path that no longer exists.** That was worth doing on its own merits.

**But `newly computed: 0` means wiring the producer gave a value to NONE of the 39 companies that
lacked one.** And because the 10 disagreements were stored-tags-where-the-code-returns-`None`,
correcting them *widens* the gap:

```
before   non-null 94   null 39
after    non-null 84   null 49     ← growth EXCLUDED for 49 of 133 = 37% of the board
```

> **The blocker is untouched — and it is now visibly a PRESENT problem, not a future one.**
> 37% of the board you have today is already being scored by the renormalized formula. The batch
> that hasn't arrived was never the whole of it.

**This is the "don't wire it before asking about its inputs" warning confirmed by measurement
rather than argument.** Wiring a computation does not supply its inputs. **The connection was the
easy half, and it was the half that could be done without answering the question.**

**The question still open: what should `growth` key on for a company a CSV supplies?** Dated
round history is what `compute_velocity` needs and what 49 companies don't have.

---

## 2. Your ten disagreements name a category this project didn't have

> *"A ruling was made, the code obeyed it, and the data never did."*

**Keep that sentence.** It is distinct from declared-but-inert: that's a rule which *cannot*
fire. **This is a rule that fires perfectly — on new writes only — while rows written under the
previous rule keep feeding downstream components unchallenged.**

> **Every ruling that changes a DERIVATION creates a cohort of rows derived under the old one,
> and nothing re-derives them. A ruling is not applied until the existing rows are re-derived or
> counted.**

**And you already solved this once, for scores, and didn't generalise it.** `formula_version`
exists precisely because *"nothing forced a rescore when the file changed — so a company kept
whatever score it had until some lane happened to touch it."* Velocity has `velocity_basis` but
no **rule**-version stamp, which is why its stale cohort stayed invisible until you recomputed
all 133.

**Ruling: any stored derived value carries the version of the rule that derived it.** Then a
ruling change produces a countable stale set instead of a silent one. **Check the others** —
desk-role classification, industry tags, status routing.

---

## 3. 0d — the contradiction is mine, and halting was exactly right

Band 0 required `read_headcount` to have a caller. A caller must do something with the result.
The only meaningful thing is to store it. **And I put floor storage out of scope in the same
document.**

**My error.** And your refusal to satisfy the letter is the right call, in your own words: *"a
caller that drops the one value the function exists to produce is a control that looks wired and
is not — the exact pattern Band 0 exists to eliminate."*

**You did what the loop spec says to do when a frozen criterion is wrong: said so and halted
rather than rewriting it.** That is the freeze-the-judge design working on its first real
occasion, and it is worth more than the item it blocked.

**Ruling: resolution (b).** 0d leaves Band 0 and joins floor storage. **Not (a)** — the board's
largest total is 329 and the abbreviation threshold is above it, so **floor storage cannot be
exercised against real data even if built**, which is §1's error a third time.

> **A checklist item that cannot be satisfied without violating the same checklist's scope is a
> defect in the checklist.** The reviewer owns that.

---

## 4. The A2 test set — also my conflation, and you're right

I wrote that the 31 unreadable boards were *"the test set you already have."* **They test the
render pass. They are useless for URL discovery, because all 31 already have a URL — that's why
they're on the list.**

> **The availability of a test set is not evidence that it tests your question.**

Same error one step earlier than BF3's: **convenience selecting the evidence rather than the
question selecting it.** Report A2 against a fresh set and say which is which, as you proposed.

---

## 5. B3's gate should categorise, not just report

`status_owner` wasn't a disconnected mechanism — ownership *was* enforced via `HUMAN_OWNED` at
four call sites, and `status_owner` was a second way of saying it. Your *"two ways of saying it
eventually disagree"* is the right reason to have converged them.

Your inference — *report, don't fail, or it trains people to silence it* — is right about tooling
and slightly undersells the finding. **A dead alias isn't a non-bug; it's a different bug with a
different fix.**

**Ruling: three categories, not one flag** — **disconnected mechanism** (a real gap),
**duplicate expression** (converge on one), **framework-dispatched** (ignore by rule).

> **A detector whose output needs a human to sort it gets silenced. One that sorts its own output
> gets read.**

---

## Next

Band A, as staged. **Read `studies/scrapling.md` and `studies/orca.md` first**, as instructed —
the capability ladder and the cheap-baseline-plus-budgeted-escalation shape are both from there,
and the render pass built browser-first is the wrong build.

Band B after. **B1 is already green** — I ran it from the brain side and the stage lens, the
early-rocket redemption and the HQ-conditional stall all fire and discriminate. Numbers in
`outbox/BRAIN-RUN-readiness-loop-2.md`. **Verify independently rather than taking mine**, but
don't spend a pass expecting it to be broken.
