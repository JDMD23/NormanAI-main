# To the CRMx build agent — round 22: staging the careers-lane signals

The switch landed exactly as ruled — zero movement, no re-anchor, gate passed. And the
strongest artifact of the whole build so far is the pair of results an hour apart:
**the same gate failed the naive version of this change and passed the compensated one.**
Same instrument, opposite verdicts, both correct. That is an eval harness proving itself
on its first live test, and it is worth more than the change it gated.

Replacing `TestRoutingRoundsByDesign` with `TestRoutingComparesRaw` was the right move —
the old test's sin wasn't that it existed, it's that it pinned a description that wasn't
true. Pinning is still correct; pin the real thing.

Your staging question is a good one. **Stage it — but the split line is different from the
one you proposed, and there's a prior confusion to clear first.**

---

## 1. Re-freeze ≠ re-anchor — and once you separate them, the cost objection dissolves

Your reluctance to stage rests on "two re-freezes instead of one." But those are two
different acts and only one is expensive:

- **Re-anchoring** = re-fitting the thresholds to JD's labels. *This* is what carries the
  circularity you documented in round 19.
- **Re-freezing the baseline metrics** = recording the new numbers. Cheap, no circularity.

**Ruling: run the careers lane with the thresholds FIXED. Do not re-anchor.**

If the new signals are genuinely better, agreement with JD should **hold or improve on its
own, without moving the goalposts.** That makes the post-lane oracle result a **genuine
held-out test** — the strongest validation available to you, and only available if you
*don't* re-anchor:

- **tau holds or improves** → the signals are real. Re-freeze the *metrics*; leave the
  thresholds alone.
- **tau degrades** → something is wrong with the signals. Investigate before accepting.
- Only if the distribution genuinely shifts far enough that the thresholds sit badly does
  re-anchoring become a question — and then it is a **separate, deliberate, JD-reviewed
  decision**, not a reflex bundled into the lane.

With that, staging costs two *cheap* re-freezes, not two circular re-anchors.

---

## 2. Split on EXTRACTED FACT vs CLASSIFIER — not "mechanical vs interpretive"

Your proposed line is nearly right; the principle underneath it is sharper and
generalizes better.

**Phase A — extracted facts:** posting dates, location-type. These are **read from the
source and spot-checkable against it.** Open the posting: the date is the date; the
workplace field says Remote or it doesn't. If a value is wrong, it's a **parsing bug with
an unambiguous right answer.**

**Phase B — classifiers:** seniority, facilities-role. These are **judgments encoded in a
heuristic** — *is "Staff Engineer" senior? is "Lead" senior?* There is no field to check
against; there is only a rule someone wrote.

Why the distinction matters: **a classifier can be systematically wrong across the entire
board in a way that is invisible in the score.** Ship seniority alongside everything else,
and if scores move oddly you cannot tell whether the signal is real or your title
heuristic is mislabelling half the postings.

---

## 3. A classifier must be validated AS A CLASSIFIER before it feeds the score

Two different questions, and conflating them is the trap:

1. **Does it label correctly?** — checked against real job titles.
2. **Does the resulting signal improve the ranking?** — checked via the oracle.

If (1) is unverified, a failure in (1) is indistinguishable from a failure in (2).

So for Phase B: build the classifier, then **have JD eyeball a sample of ~30 real titles
with their assigned labels.** Five minutes of his time, and he is the authority on what
reads as senior in his market. Fix what's wrong, *then* wire it into the score and let the
oracle judge the signal itself.

This is the same discipline as the blind labeling session, applied one layer down — and it
produces a small reusable labeled set for the classifier, exactly as the corpus does for
the scorer.

---

## 4. Only FOUR of the seven dormant signals belong to this lane

Worth naming, because "the seven dormant signals" has started travelling as a single unit
and that invites bundling unrelated changes into one re-validation:

| Signal | Source |
|---|---|
| location-type | **careers lane** |
| posting dates | **careers lane** |
| seniority | **careers lane** (classifier) |
| facilities-role | **careers lane** (classifier) |
| Manhattan-tight headcount | a *different instrument* — Sales Nav geo granularity |
| layoff geography | the *news lane* |
| down-round | needs a *valuation source* |

The bottom three are separate future work on their own schedules. Don't let them ride this
one.

---

## The ruling, plainly

**Phase A** (posting dates + location-type) → run the lane → oracle **with thresholds
fixed** → re-freeze metrics.
**Phase B** (seniority + facilities-role) → validate the classifier against real titles
with JD → wire in → oracle → re-freeze.

Two cheap re-freezes, **zero re-anchors**, and every change attributable to its cause.

Before either: **batch 5 session 2** — the 19 Sales Navigator headcounts, closing the
batch that has been half-finished since the throttle capped.
