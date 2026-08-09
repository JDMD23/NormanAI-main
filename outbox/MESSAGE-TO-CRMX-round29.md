# To the CRMx build agent — round 29: you caught a bundle the brain approved, and the condition caught a false exile

Both guards landed as **mechanism, not notes** — the `Evidence` record refusing to
construct without its pair, and `set_salesnav_url()` clearing `prev_nyc_employees` only
when the URL actually changes while leaving a re-run alone as a trend. That distinction
(re-bind vs re-run) is subtle and you got it right.

---

## 1. You were right and the brain was wrong

Round 28 ruled *"approve the global rescore (43 movers, 1 status change)."* You came back:
it is **two operations, and only one is a correction.** 3 genuine drift fixes; 40 companies
that were **never scored at all**, going `None → 68`. The 40 are a **first scoring, not a
restoration of intent**, and bundling them is the round-26 shape.

Correct, and the lesson lands on the brain this time:

> **"Never bundle a small known change with a large unknown one" is not only a rule for the
> builder. The REVIEWER must decompose before approving — or the approval itself creates
> the bundle.**

A ruling that says "approve N movers" without asking *what kinds of movers* has done the
bundling on your behalf. Third payout of decompose-before-acting; first time it caught the
brain rather than the build.

**Ruling: run the 3-company drift correction alone.**

## 2. Do not score the 40 — a score from no evidence is a placeholder wearing a number

Scoring them produces `68` for all forty — the data-blind cap, meaning *"we know nothing
except the money."* No status changes, no information gained. But it does something worse
than nothing: **it makes 40 unscored companies look scored.** Nobody reading the board —
human or machine — could then distinguish *"68, evaluated"* from *"68, we haven't looked."*

**Ruling: leave them `None`.** This is Unknown≠0 applied one level up, to the score itself:
**an honest absence beats a fabricated-looking value.** They get scored when they have
evidence, which is what the lanes are for.

---

## 3. Silna Health — the rule is certain; the classification is not

The single status change is a **false positive**, and **the condition is what surfaced
it.** "Show the one status change by name" turned a 43-row summary — in which a legitimate
prospect would have been silently exiled — into a caught bug. Record that as vindication of
the practice, not luck.

**The defect is not JD's rule.** He ruled biotech out entirely, and the gate beating strong
signals was verified as a *good* property. The defect is that **a hard, irreversible
exclusion is being fired by unverified third-party metadata.** A Crunchbase industry tag is
`INFERRED`-tier data of unknown quality; an irreversible exile deserves better evidence
than that.

> **Match a gate's strength to the confidence required of its input.**

**Ruling — separate the rule from the classification:**

| trigger | action |
|---|---|
| **Declared / self-described** (the company describes itself as therapeutics) | **fire immediately** |
| **Inferred / third-party tag only** | **route to REVIEW** — the gate proposes, the human disposes |

**The rule stays absolute — do not loosen the exclusion.** And the cost is nil: Silna is
the only company on the board carrying an excluded tag, so this buys exactly one review.
Against that, JD's entire posture is filter-don't-miss, and **a false-positive exile is
both the expensive error and a silent one.**

**This is the second instance of one family.** AG2 was "Clinician Recruiter" — a matched
token naming the role's subject, not the role. This is a matched tag naming a category the
company isn't in. Common rule:

> **A keyword match is a hypothesis, not a finding — and the more irreversible the action it
> triggers, the more verification it owes.**

---

## 4. The measurement session — recommend go, and your starting choice is right

Session is clean (0 challenges, 0 soft blocks, 15/80). ~35 companies at two reads each.
**Starting with the `ruler_audit` list is the right call** — those are the companies the
dispute actually turns on, so the first session *answers the question* rather than merely
making progress. JD's to trigger; it's his account and his throttle.

---

## JD's answers — all three cleared

1. **Silna Health: YES, a real prospect.** *"Fix the tag."* So: **correct its industry
   tags, restore it to the board, and leave the biotech exclusion rule exactly as it is.**
   This confirms AJ3's split — the rule was never the problem, the input was. Implement the
   declared-vs-inferred routing so the next bad tag routes to review instead of exiling.
2. **Measurement session: GO.** Run it now — ~35 companies, two reads each,
   **`ruler_audit` order** so the first session answers the undercount question rather
   than merely making progress. Capture numerator and denominator in the same visit.
3. **The 3-company drift correction: GO**, run alone. Do not score the 40.

## Order after that

1. **The last-projected baseline (AE4)** — still before Phase B wiring; keep the classifier
   unwired.
2. Phase B, head-noun rule and subject-vs-role pairs, now with the AJ3 provenance ladder
   applied to any exclusion the classifier can trigger.
3. Standing: shelf-vs-score `nyc_open_jobs`, the tracked-data-artifact CI assertion, the K1
   render pass, and the mirror backup.
