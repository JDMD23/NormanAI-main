<!--
For JD: this is the complete Fit-scoring specification distilled from your labeling
session + the scenario interrogation (rounds U–W). Hand it to the CRMx build agent as
the source of truth for the scoring recalibration. It supersedes scattered notes; every
rule traces to something you said. Nothing changes on the board until the agent applies
this, re-runs the oracle against your 23 blind labels, and you review the delta.
-->

# Norman Fit-Scoring Specification — validated by JD (rounds U–W)

**The thesis, one line:** Norman rewards companies that will **need NYC office space
soon** — measured first by **how many in-office NYC people they have**, then by **how
fast they're growing that NYC presence**, all read **relative to their funding stage.**

## 1. Primary drivers (these dominate the score)

**1a. NYC in-office headcount — the leading signal.**
- Absolute NYC headcount is the main driver. When ranking real teams head-to-head,
  **bigger wins**: JD ranked the 40-NYC Series B > 15-NYC Series A > 6-NYC seed, even
  though the smaller ones had higher growth *ratios*. Size leads; growth amplifies.
- Keep the **extended headcount ladder (U1)** — points keep accruing past ~50, never a
  hard plateau.
- **Only in-office / hybrid NYC people count fully. Remote headcount barely counts** —
  a remote worker needs no desk (W5).

**1b. Growth signal — REQUIRED to reach the top tier (W6).**
A company with **no growth signal caps at "medium"** no matter how big (JD: 200 NYC
people, no jobs, no fresh funding → "only medium"; 100 NYC + PE round + 0 jobs →
"medium"). A growth signal is one of:
- **Active in-office NYC hiring** — scored on **both** the absolute count of open
  in-office NYC roles **and** the **jobs-to-headcount ratio** (10 jobs on 15 people is a
  rocket; 10 on 300 is routine), strongest when both are high (W1). At equal size,
  hiring intensity makes a **big** gap (JD: 30-NYC with 15 jobs ≫ 30-NYC with 3 jobs).
  **Weight recent job postings heavily and discount stale ones** — 10 roles posted this
  week ≫ 10 that have sat open 5+ months (they may be filled/abandoned) (Q10).
- **OR a fresh substantial raise** — a large recent round is itself a leading expansion
  signal: JD would pursue a just-raised-$40M NYC company with 20 people **now, even
  before jobs appear** (Q6). (Contrast: an *old* late-stage/PE round with no jobs is
  *not* a growth signal — it reads as settled.)

## 2. The stage-relative lens (read everything against funding type)

Expectation of headcount **scales with stage** (seed / A / B / late). Judge whether a
company is **exceeding or failing its stage**:
- **Exceeding = strong positive.** Seed with 25 NYC people beats Series B with 25 (Q7);
  a seed with 6 people hiring 4 is exciting (W3).
- **The early-rocket redemption (W3):** small headcount is **not** penalized — it's a
  strong prospect — when **young (~<1 yr) + seed + funded ($5M+) + hiring hard.** These
  four are JD-tunable config values.
- **The stall penalty (Q3):** **old + still-early-stage + tiny + not-growing = red
  flag** (founded 2016, still seed, 6 people, 2 jobs → "real red flag"). Company age
  relative to stage cuts both ways.
- **Late-stage does NOT cap a grower:** Series D, 300 NYC, 20 in-office jobs → **top
  prospect** (Q4). The discriminator is *growth*, not stage. Mature + quiet → medium.

## 3. HQ / native-NYC (open question U5 — RESOLVED)

- **NYC-HQ is a meaningful scored component, not just a tiebreak.** At identical NYC
  hiring, JD calls the NYC-HQ company "clearly better" (Q9) — it earns real points.
- **But modest enough that a large growth/momentum gap overcomes it** — JD took the
  SF-HQ company growing 10-NYC-+-50-Austin over a smaller NYC-centered one for overall
  momentum (Q3). So: real points for NYC-HQ, not dominant.
- **Real NYC hiring at scale carries a satellite.** An SF-HQ company with 5–6 NYC people
  and 3–4 in-office NYC roles is a good prospect *despite* the SF HQ (JD's own example).
  What's penalized is **thin/token** presence — 6 NYC people with **0** jobs → "low, but
  keep it" (Q2): scored low, kept on the board, **not** shelved.

## 4. Secondary / context (down-weighted — U4, W7)

- **Funding size, sector, investor tier are context, not primary rankers.** JD refused
  to rank two companies on funding without first knowing "NYC headcount, HQ, and roles."
  Sector stays at reduced weight (U4); the **industry *exclusion gate* stays full
  strength** (excluded sectors still exit regardless of headcount).
- **Exception — funding *recency*:** a fresh substantial raise is elevated to a growth
  signal (§1b), even though funding *size* is only context.

## 5. Trend over time (W2) — build now, validate later

Rising NYC heads/jobs over time beats high-but-flat. Build off the change-log history;
it is **regression-safe now** (must not break the 23 labeled pairs) and its positive
value is validated **later** as history accumulates (JD labeled snapshots, so the corpus
can't yet grade trend). Job-posting *freshness* (§1b) is the near-term proxy available
today.

## 6. New data the scorer needs (build these to feed the above)

- **Job location-type classification:** in-office / hybrid / remote, per NYC role (§1a,
  §1b). Load-bearing — remote roles barely count.
- **Job posting dates:** to weight fresh over stale (Q10).
- **HQ location** and **funding type** (seed/A/B/late) as first-class fields (§2, §3).

## 7. JD's directional sanity-checks (use as property anchors — T2, kept separate from the corpus)

These are JD-validated *directional truths* — encode as property tests, not corpus cases:
- Series B (40 NYC, 8 jobs) **>** Series A (15 NYC, 10 jobs) **>** seed (6 NYC, 4 jobs).
- Seed (25 NYC, 6 jobs) **>** Series B (25 NYC, 6 jobs) — exceeding-stage wins.
- Series D (300 NYC, 20 in-office jobs) = **top**; 100 NYC + PE round + 0 jobs = **medium**.
- 30-NYC Series A with 15 jobs **≫** 30-NYC Series A with 3 jobs.
- NYC-HQ **>** SF-HQ when NYC hiring is identical (meaningful, not dominant, gap).
- In-office 10 jobs **≫** remote 10 jobs; fresh 10 posts **≫** 5-month-stale 10 posts.
- Token satellite (6 NYC, 0 jobs) = **low but on-board**, not shelved.

## 8. Process (U6 / T3 — non-negotiable)

Apply §1–§7 as **principled** changes (never tune numbers to pass the 16 pairs) →
**re-run the oracle** → confirm **tier-match holds 7/7** and pairwise concordance
**holds or improves** → confirm the new drivers didn't break a previously-correct pair →
**review the delta with JD** → only then **freeze** the baseline. 100% concordance is not
the goal; eliminating the systematic lean is. Fold this into the same rescore JD is about
to greenlight, so the board locks on the *complete* picture, not a partial one.
