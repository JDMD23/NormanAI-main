<!--
For JD: paste this whole thing into the CRMx build chat. It tells the agent to engineer
the full scoring recalibration from the spec, re-run your labels, show you the before/
after, and only then rescore all 95 companies. Nothing locks or changes the live board
until you review the delta.
-->

# To the CRMx build agent — engineer + apply the Fit-scoring recalibration

The Fit-scoring model is fully specified from JD's labeling + a long scenario
interrogation. **Read these in NormansBrain first, in order:**
1. **`FIT-SCORING-SPEC.md`** — the authoritative spec (§1–§8b). This is the source of truth.
2. **`reference/target-industries.md`** — JD's 20-industry target universe (qualification).
3. **`brain/jd-operator-profile.md`** — how JD thinks + the business context behind the rules.
4. **`reviews/phase1-lane-design-decisions.md`**, rounds **U–W** — the derivation and the
   eval/process rulings (U6, T3, V2) you must follow.

## The task
Engineer every rule in `FIT-SCORING-SPEC.md` into the scorer, then apply it. Highlights
(the spec is authoritative — this is orientation, not a substitute for reading it):
- Headcount leads (extended ladder, in-office only, **Manhattan-tight geography** —
  treat the Sales Nav metro count as an upper bound; skew Manhattan/Brooklyn where
  granular data exists).
- Growth is required for top (in-office hiring **or** fresh raise); ratio + absolute +
  freshness + intensity + **role seniority** + **facilities-role bonus**; trend +
  acceleration.
- Stage-relative lens (exceeding/failing stage, early-rocket redemption, **HQ-conditional
  stall**). HQ = meaningful but modest.
- Funding: recency elevated, size/sector/investor down-weighted, **down-round = yellow
  flag**, missing-funding = no penalty, floor only when early.
- Industry = **qualification taxonomy + coarse tier** (core > expansion; off-list = not a
  target), not a fine tilt; **keep the exclusion gate full strength**.
- The §8b conflict edges (shrinking = pass, huge ratio loved, big-fresh-raise, traction-
  overrides-funding, layoffs-relative-to-NYC, everything-maxed = chase-today tier).

## New data the scorer needs (and be honest about backfill)
Some rules need data the board may not have yet. Build the scorer to use them, and
**report which signals you can apply to the current 95 now vs. which need a data
backfill** (don't silently score around missing inputs):
- Job **location-type** (in-office / hybrid / remote) and **posting dates** (fresh vs stale).
- Job **role seniority** (exec/senior vs junior) and **role-type** (facilities/workplace).
- **HQ location**, **funding type** (seed/A/B/late), **valuation direction** (down rounds).
- **Layoff signals with geography** (NYC-hit or not).

## The process — non-negotiable (U6 / T3 / V2)
1. **Principled changes only — never tune numbers to pass the 23 labels.** Fix the rules;
   let the oracle report the effect. (Overfitting the corpus is the one forbidden move.)
2. **Re-run the oracle** against JD's frozen corpus. Confirm **tier-match holds 7/7**,
   pairwise concordance **holds or improves**, and **no previously-correct pair breaks**.
3. **Rebase the ENTIRE threshold ladder together** (V2) — entry, hysteresis floor, all
   tier boundaries — preserving each gap's *width*, not its old number. **Grep for any
   hardcoded old thresholds** and confirm none survive on the new scale.
4. **HARD GATE — show JD the before/after and STOP.** The disagreement/delta report, every
   band change, the tier-match and concordance numbers. **Do not freeze; do not touch the
   live board until JD reviews.** 100% concordance is not the goal; eliminating the
   systematic lean is.
5. On JD's go: **rescore all 95 companies**, run the replay audit, and **show every band
   change before the board updates**. Then, on his word, **freeze** the baseline.
6. Commit + push each step; keep `main` current; write ADRs for the load-bearing changes.

## Boundaries — build exactly this, not more
- **170 RSF/employee** (headcount × 170 = projected NYC space): **capture the formula,
  do NOT score deal-size yet** — JD's explicit call. Hold it for later.
- **Current-space-situation** (coworking/sublease/lease-expiry): **not pursued** — data
  isn't reliably gettable. Skip it.
- **Do NOT build Priority, warm_path, deal-size, or outreach here.** This is the **Fit-
  scoring recalibration only.** (Those layers are captured in the profile for later.)
- If applying a rule reveals a genuine design question the spec doesn't answer, **flag it
  for JD via the brain** — don't guess.

## What to send back
A short report: what you engineered, which signals applied now vs. need backfill, the
oracle result (tier-match + concordance, before → after), the threshold rebasing, and
the band-change preview — then wait for JD's go on the rescore and the freeze.
