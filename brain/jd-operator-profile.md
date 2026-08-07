# JD — operator profile (persistent memory: read at session start)

This is the durable model of **how JD thinks and decides**, so any session picks up
where the last left off without re-learning him. Built from his labeling session and the
rounds U–W scenario interrogation. The scoring specifics live in `FIT-SCORING-SPEC.md`;
this captures the *person and the reasoning*.

## Who he is
- Founder/operator of **Norman**, a decision-support CRM for **NYC commercial office
  space** — finds companies about to need NYC desks, so he can pursue them.
- A **sharp product thinker, not a coder.** He reasons in outcomes and examples, not
  code. He is the **ground-truth authority** for what a good prospect is — his judgment
  is the answer key the Fit scorer is validated against (the eval oracle).
- He **owns the account risk** (his real LinkedIn/Crunchbase/Sales Nav identities) and
  gates each step of the build.

## How his brain works (the reasoning model)
- **Primaries first, always.** He will not judge a company on funding/sector/investors
  without first knowing **NYC headcount, HQ, and open NYC roles.** Everything else is
  context that modulates the primaries — never a driver on its own.
- **He thinks in whole pictures and concrete examples**, and **ranks** rather than
  picks a single winner ("all interesting, but 1) … 2) … 3) …"). Give him real numbers
  and A-vs-B scenarios; abstract questions get a "depends — what are the stats?"
- **Stage-relative judgment.** He reads every company against its funding stage — a
  seed with 25 people is *crushing it*; a Series B with 25 is *lagging*. Exceeding your
  stage is a strong positive; failing it (or being old and still tiny) is a red flag.
- **Concrete demand over proxies.** NYC bodies + real NYC hiring beat sector polish,
  investor tier, and estimates every time. He distrusts anything that lets a proxy
  outrank the real signal.
- **Growth is the gate to "top."** Size makes a prospect bigger, but without a growth
  signal (in-office hiring *or* a fresh raise) a company caps at "medium."
- **Office-space realism.** Remote roles don't need desks (they barely count); in-office
  NYC hiring is the purest signal; a company that just signed a lease is out for years.

## How to work with him (communication + process)
- **Plain language, no jargon.** When a message drifts technical, he will say "I have no
  idea what this means — layman's terms and directions." Lead with what it means for him
  and what to do; keep analogies concrete (filing cabinet vs. desk, answer key, etc.).
- **He learns by example.** Show a worked example / a mock of the actual thing before
  asking him to do it.
- **Clickable > typing** for structured choices — he prefers multiple-choice scenarios
  he can tap over free-text.
- **He wants to be interrogated.** He explicitly asks for scenario questions to get his
  judgment into the system; keep asking, in batches, with full stats each time.
- **Gate-and-review discipline.** Nothing irreversible without his go: design → review →
  freeze. He greenlights each batch; he reviews every board change before it lands.
- **He values elite, thorough, self-contained prompts/artifacts** he can hand to the
  CRMx build agent — and downloadable files he can forward.
- **Independence boundary:** his judgment is the ground truth. The brain protects the
  method and reads disagreements *with* him; it never supplies his answers for him.

## Decision & priority model (how he chooses what to chase)
- **Timing is a soft tilt, not a hard rank.** Imminent-need (cramped, hiring burst) and
  emerging-need (just raised, scaling) both get chased — "rank close, chase both." Don't
  over-weight "needs space this quarter" in priority.
- **Confidence gates *effort*, not *inclusion*.** He pursues both a sure-medium fit and
  a thin-data maybe-great — "both." Uncertain-but-high-upside companies get **dug into,
  not discarded**; the board should surface them for investigation (bounded second-pass),
  never bury them for missing data. (Consistent with Unknown≠0.)
- **Warm path is a PRIORITY/sequencing tilt, separate from Fit.** A company where he
  knows a decision-maker gets his attention *first* (easier meeting), with the strong-fit
  one "right after." Warmth affects pursuit *order*, not the Fit score — it feeds the
  `warm_path` → priority layer, kept as its own axis (don't blend into Fit).
- **Hard deal-breakers (instant pass):** **too big / enterprise** (already have space),
  **wrong industry** (his exclusion list), and **already repped / CBRE conflict.** These
  are exclusion gates, full strength.
- **Recently signed a lease is NOT a deal-breaker** — it's a *deprioritize + track*:
  keep them, rank them low, watch for the next expansion (they re-enter the market).

## What Norman should do for him (surface, alerting, uncertainty)
- **Lean high-recall.** He wants a **wide net with some noise** — "I'd rather filter
  than miss a good one." Err toward *surfacing*; don't over-shelve. The cost of missing a
  real prospect outweighs the cost of some weak ones on the board. (Tune thresholds
  permissive; keep the Low-NYC exit conservative.)
- **Layered surface.** A **short daily "chase these" action list on top, the full ranked
  universe underneath** to explore. (Validates the working-views design: a tight ranked
  Prospects view + the full board.)
- **Ping triggers = business-EXPANSION events** (the "strike now" moments, and the
  effective news-lane signal set): **new funding, leadership change, an acquisition they
  made, a big account/customer win, an announced headcount increase.** These are worth
  interrupting him for on companies he tracks. (Lease-signing is a secondary "adjust
  down" signal, not one of his named strike-triggers.)
- **Genuine uncertainty → ASK him.** When data is thin or conflicting, surface it as a
  **question for him to weigh in on** (human-in-the-loop review) — never hide it, never
  silently guess. He wants to be the tiebreaker on real uncertainty.
- **Expansion events are OUTREACH ANGLES, not ranked signals.** He doesn't rank funding
  vs. HC surge vs. big-account vs. acquisition vs. new-exec — "all of them give me an
  angle." The news lane should capture *all* of them, each tagged as a usable outreach
  hook that feeds the **Current Angle** field — not just as a fit signal.
- **Tight recency for "act now."** A signal has to be **last-few-weeks fresh** to count
  as live momentum worth a ping. Older events are weaker context, not strike-triggers.
- **Re-engagement trigger = a rise in NYC hiring on the careers page.** A passed/shelved
  company comes back the moment its NYC roles increase. So **keep monitoring shelved
  companies' careers pages** (lower cadence) and re-surface on a hiring uptick — shelved
  is never dead.

## What his trust requires (the product rests on all four — fail one, lose him)
Asked what would make him stop trusting the board, he said **all of them.** So "ranked
trust" stands on four pillars, each mapping to a build investment:
1. **Correct data** — no wrong numbers (verified writes + instrument cross-checks).
2. **Complete discovery** — no obvious prospect he finds elsewhere is missing (coverage
   + the high-recall wide net).
3. **Freshness** — the board keeps up with changes he knows happened (reconcile loop +
   news lane + re-checks).
4. **Ranking that matches his gut** — no weak company above a strong one (the scoring
   eval/calibration).
Any single failure loses him. This is the acceptance bar for the whole system.

## Target universe & geography (his definitions)
- **"NYC" means Manhattan + a little Brooklyn — NOT the full commuter metro.** The Sales
  Nav metro ruler over-counts (NJ/Westchester/LI); his real target is Manhattan-centric.
  Skew Manhattan where granular location exists; treat the metro count as an upper bound.
- **Target industries = a structured 20-industry taxonomy** he supplied (10 core + 10
  expansion + overlay tags), heavily AI / deep-tech / enterprise-infrastructure oriented —
  captured in `reference/target-industries.md`. Industry is a **qualification + coarse
  tier** (core > expansion; off-list = not a target), **not** a fine ranking tilt; a
  great-fit AI company and a great-fit fintech excite him equally.
- **Facilities/workplace hires** (Head of Workplace, Office Manager, Facilities) are an
  elevated office-space tell — a real bonus, between "normal role" and "huge."
- **Urgency is relationship-driven:** a live warm intro is what makes him chase *today*;
  company signals set fit/rank, warm-path availability sets timing. (Plus all-signals-
  maxed = a chase-today tier.)

## Live threads (update as they resolve)
- `FIT-SCORING-SPEC.md` — the complete, JD-validated scoring spec (rounds U–W), pending
  application + oracle re-run + his rescore review + freeze.
- Ongoing scenario interrogation to deepen this profile (his standing request).
