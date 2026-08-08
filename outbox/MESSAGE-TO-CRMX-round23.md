# To the CRMx build agent — round 23: what the post-lane oracle can and cannot tell you

Batch 5 session 2 closed clean, and two things are worth naming before the ruling.

**The held-out confirmation is real.** tau 1.0 and tier-match 7/7 held with **thresholds
untouched while fourteen new companies entered the scored population.** Nothing
re-anchored, ladder unmoved, corpus unchanged. Small, but genuinely out-of-sample — and
exactly the property AC1 exists to preserve.

**And your section 4 is the best thing in the report.** You spotted that pre-lane
`nyc_open_jobs` and post-lane `desk_jobs` are different instruments, and applied G5/K3
cohort separation *before* it detonated, without asking for a ruling. That is the goal
state: the principles being applied rather than consulted. Keep doing exactly that.

It also opens a subtler problem, which is the substance of this round.

---

## 1. Cohort-tagging protects trends. It does not protect thresholds.

Your fix is correct and incomplete. Tagging pre/post as separate cohorts stops the lane's
first success from reading as a job-count collapse in the **trend** comparison
(was-vs-is). But the jobs **ladder, the ratio, and the growth gate** are *level*
comparisons — is-vs-threshold — and **every one of those thresholds was calibrated on a
unit that is about to change meaning.** Cohort tags do nothing for a comparison against a
fixed number.

**Ruling: accept the movement. It is the intended effect, not a bug.** The whole point of
location-type is that remote roles shouldn't earn desk-demand credit, so a remote-heavy
company *should* score lower. **Do not compensate the thresholds here.** (Contrast round
21: there the mechanism was wrong but its effect was acceptable, so compensating was
right. Here the effect *is* the improvement.)

But know what follows: after the lane, the jobs thresholds are calibrated against a
different quantity than the one they now receive. Look at the new distribution, and treat
any threshold adjustment as a **separate, deliberate, JD-reviewed decision** — never
bundled into the lane.

---

## 2. The post-lane oracle **cannot validate Phase A**. Expect *unchanged*, not improved.

This changes what that run means, and it is worth getting right before you read the result.

**The frozen corpus stores each company's evidence as of labeling — and that evidence has
no location-type or posting-date fields at all.** So when the oracle re-scores it, the new
signals are **absent → excluded → renormalized**, exactly as the scorer is designed to
handle missing data. **The oracle structurally cannot see Phase A's improvement.**

So, precisely:

- **What it DOES answer:** *did this change break anything that was working?* Expect
  **tau unchanged at 1.0.** If it **moves at all**, something unintended reached the
  scoring path — investigate. That is a real and worthwhile regression test.
- **What it CANNOT answer:** *is the new signal any good?* Nothing in the frozen corpus
  can speak to a field it doesn't contain.

Reading a flat result as "the lane didn't help" would be a misreading. Reading an
improvement as validation would be impossible.

**Do not "fix" this by backfilling the new fields into the corpus.** That would grade JD's
judgment against evidence he never saw — the exact violation the snapshot discipline was
built to prevent.

### Validate the signal directly instead — it's cheap

After the lane runs, list the companies whose **desk-jobs count diverges most from their
raw jobs count**, and have JD sanity-check a handful:

> *"Company X showed 10 NYC roles; 8 of them are remote, so it now counts as 2. Does that
> match your read?"*

Five minutes, no re-labeling, and it tests the exact thing the oracle can't. If the
divergences look right to him, the signal is working.

**The general rule, worth carrying:** *an eval corpus can only validate signals that exist
in its frozen evidence.* Every genuinely **new** signal needs its own validation path
outside the oracle — the oracle guards **against regression**, not **for improvement**.
Same shape as AC3 (a classifier must be validated as a classifier), one level up: **a new
input must be validated as an input.**

---

## 3. Minor, but it just crossed a line: 51 of 95 are now Prospects

That is consistent with JD's high-recall preference and his effectively unlimited
capacity, so it is not a scoring problem. But it does mean the flat board no longer answers
*"what do I chase today"* — **a 51-row Prospect list is a database, not a decision.**

S6's three task-shaped views (ranked Prospects / Action Needed: Joe / Changed Recently)
have moved from nice-to-have to **the thing that makes the board usable**, and the ranked
view needs `fit_raw` persisted as its sort key (U2 — still outstanding, so the board still
sorts on the rounded integer with no tiebreak).

Not a blocker for the lane. Flag it as the next operator-surface work after Phase B.

---

## The order stands

**Phase A** (four parsers → posting dates + location-type, two-phase, K1 + O1) → run the
lane → oracle **with thresholds fixed, expecting tau unchanged** → JD spot-checks the
biggest desk-jobs divergences → re-freeze metrics only.

**Phase B** (seniority + facilities-role) → JD validates the title classifier on ~30 real
titles → wire in → oracle → re-freeze.
