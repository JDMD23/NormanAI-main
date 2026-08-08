<!--
For JD: paste this whole thing into the CRMx build chat. It's the brain's post-audit
message — what the audit found, the one drift to fix, the next build in order, and the
questions the build agent should answer. Grounded in the studied repos and in how batch
5 actually behaved. It changes the emphasis (prove the board is right before filling it
faster) but keeps the cheap wins you already ruled.
-->

# To the CRMx build agent — from Norman's Brain (via JD): post-audit findings + the next build

You've built something clean. This message is not a course-correction because anything
is broken — the audit found the opposite. It's a correction of *emphasis*, backed by
one objective finding, and a concrete plan for the next build grounded in the repos we
studied. Read it in full before you touch code.

## 1. What the audit found — and credit where it's due

I audited both repos at tip `b737439` across git, code, and docs. The result is
genuinely reassuring: **the fast cadence did not breed drift.**
- **Git:** clean. `main == phase-0` (ADR 0007 honored), no divergent branches, no stray
  worktrees, nothing uncommitted.
- **Code:** tight. 209 tests verified. No stubs in live paths — the `NotImplementedError`s
  in `resolve.py` are a proper `KnownEntities` interface, not half-finished work. The
  unbuilt contexts are *clean absences*, not broken scaffolding.
- **Docs:** current and self-honest. `board-decisions.md` tracks through round 11.
  `invariants.md` **names its own two gaps** (all-or-nothing lanes, LLM grounding) rather
  than papering over them.

Specific things you did right, that I want reinforced because they're the culture to
keep: `reconcile.py` implements L5's six laws verbatim and *cites them*; the identity
bulkhead is mechanized with a locking test (not a convention); field ownership is
enforced at *type construction*; the batch-5 barrier held 19 companies statusless in
public view with zero flapping; and your R7 attribution was **honest** — you said half
the pipeline gain is just the safe API lane and the rest is stuff interleaving gets too,
which is exactly right and exactly what a trustworthy engineer reports. Keep all of that.

## 2. The one real drift — and it's the one that matters

There is exactly one true drift, and the audit turned it from an opinion into a fact.
**The brain's own handoff plan said, verbatim: "build the scoring eval harness BEFORE
touching the scorer."** In the code: there is no `evals/` harness, and the scorer is
**live, ranking 95 companies**, validated by invariant tests plus two directional
anchors (Artemis > Bold Security). An explicit *before* was skipped.

Here's why this is the finding and not a nitpick. Norman's product is **ranked trust.**
For twelve rounds we've made the *inputs* to the scorer more correct — the Sales Nav
ruler, the cross-checks, the zero-state traps, the direction classifier. All real, all
excellent. But **every one of those rulings improved the inputs; none validated the
function that turns those inputs into the ranking JD acts on.** We've sharpened the lens
to sub-pixel and never checked the prescription. A perfectly-measured input to an
unvalidated ranking function produces a board that is precisely, verifiably, confidently
ranked — with no evidence the ranking is *right*. That is the largest exposure in the
system, and batch 5 sharpened it: the barrier and lanes performed beautifully, but
supervision was *narration* — nothing in the system can currently tell JD the board is
right, only that it *ran*.

**The scorer was pulled forward to production; its validation was not. That debt is now
due.**

## 3. The next build, in strict order (grounded in the repos we studied)

Do these before resuming any enrichment expansion. The order matters — each rests on the
one before it.

### 3.1 — Build `evals/` and validate the live scorer (justhireme · autoresearch · graphify)
This is #1 and it closes the drift.
- **A labeled corpus, not more anchors** (justhireme's eval-harness pattern). Take
  ~25–30 of the 95 live companies and have JD label them. Prefer **pairwise judgments**
  over absolute scores — JD can't assign "73," but he can say "DualEntry should rank
  above Concourse" and "Ilant is not a real Prospect." Pairwise ranking is the robust
  ground truth here.
- **Measure ranking quality, three ways:** (a) tier-match rate — does the scorer put
  each company in JD's tier? (b) rank correlation (Kendall/Spearman) against JD's
  pairwise orderings; (c) **the disagreements themselves** — every place the scorer and
  JD differ is the highest-value signal in the whole system ("why does the model rank X
  over Y when JD wouldn't?"). Surface those explicitly.
- **Freeze the corpus as a regression oracle** (autoresearch's frozen judge). Every
  scorer or `fit-score.json` change re-runs it; a drop in tier-match or rank-correlation
  **blocks the change**. This extends your existing L4 replay audit from "did routing
  flip" to "did *quality* regress against JD's judgment."
- **Validate the explanations too** (graphify's extracted/inferred/ambiguous discipline).
  The scorer is self-explaining — assert each score's "why" cites real evidence, no
  invented drivers.
- **Make the corpus grow itself** (claude-mem episodic memory): every time JD overrides a
  placement live, capture it as a new labeled case. His overrides *are* ground truth —
  the system should be assembling its own calibration set from them, not discarding them.

### 3.2 — Add PRODUCT observability, not just operational (evidently · opentelemetry)
`core/observe` today watches the *lanes* (did they run, are we challenged). It does not
watch the *product*. Add a product layer:
- **Score-stability check:** on each reconcile, diff every company's score vs. last. A
  score that moved **without an evidence change** is a bug or config drift → flag it.
  Evidence that moved **without the score moving** is a scorer gap → flag it. (This is
  evidently's drift-as-eval applied to the scoring layer.)
- **Tier-distribution monitor:** track the Prospect/Tracking/Watchlist/Low-NYC mix across
  batches. A sudden shift is either a real market signal or a scorer regression — surface
  it either way.
- **JD-agreement trend:** as the eval corpus grows from overrides, track the scorer's
  agreement rate with JD *over time* — is it getting more aligned or less?
- Frame these as the product's **golden signals** (opentelemetry): not latency/errors,
  but score-stability, tier-distribution, evidence-completeness, and JD-agreement. Chart
  them; alert on them. This is also what makes supervised operation real — the collapsed
  health line (R5) should carry these, not just the lane counters.

### 3.3 — THEN build `contexts/priority` (orca · brain/10) — not before
Priority is the product's top layer and the thing that turns "95 scored companies" into
"pursue *these five* this week." But it must come **after** 3.1, because **Priority ranks
on top of Fit — if Fit is unvalidated, Priority amplifies the error.** Don't rank on an
unproven base.
- **Bounded second-pass investigation** (orca): for already-qualified Prospects only (not
  all 95), do a deeper, *time/step-boxed* urgency read — funding recency, NYC hiring
  velocity (jobs delta), news/lease-timing signals (the news lane, F4), warm-path
  availability. Bounded means it deepens a fixed budget per company, never runs open-ended.
- **Priority is a separate vocabulary from Fit** (brain/10): Fit = "is this a good fit,"
  Priority = "should I chase it *now*." The Second Pass is Priority, not Fit.

### What to keep running in parallel, and what to pause
- **Keep (cheap, safe, already ruled):** S1's careers-parser build-out (it crosses careers
  to the unattended-safe side of the L2 line — real autonomy progress) and the S3 domain-
  liveness gate. These don't compete with the above and they reduce JD's manual load.
- **Pause until the board is proven right:** the vendor eval (keep S5's shadow-mode
  *discipline* for when it resumes), the working views (S6), and any further parallelism
  (S2 already said skip the two-browser topology — that stands). Filling the board faster
  is the wrong investment while the ranking is unvalidated.

### Backfill while you're here
Write **ADRs 0010–0012** for the rounds 10–12 architectural decisions currently living
only in `board-decisions.md`: pipeline restraint / skip two-browser (S2), vendor-as-
unattended-unlock + shadow-mode migration (Q3/S5), careers crossing the L2 line (S1).
They're expensive-to-reverse; they deserve the ADR tier.

## 4. Questions for you (answer from the system before building)
1. **Override capture:** when JD moves a company on the board, is that disagreement
   recorded anywhere as signal today, or only adopted as data? (It's the seed of the eval
   corpus — 3.1.)
2. **Score stability:** is there *any* current check that a company's Fit didn't move
   without an evidence change, across the batches so far? Have any silent score shifts
   already happened?
3. **The two anchors:** what exactly do the Artemis/Bold Security directional tests assert,
   and have they ever caught a regression — or have they never fired?
4. **Security:** has a secret-scan or security review run since the system began holding
   real LinkedIn/Crunchbase sessions and storing company data? Where do the session
   artifacts and any credentials live, and what's their blast radius if the datastore
   leaks? (brain E3 — linkedin-mcp-server/ats-scrapers legitimacy ceiling.)
5. **Durability:** is there a tested backup/restore of the SQLite source of truth (now 95
   companies)? What's the recovery story if the file corrupts mid-batch?
6. **Bus factor:** is there a single current doc a new engineer could read to understand
   the whole system, or is it 9 ADRs + `board-decisions.md` + context? (Not urgent, but
   name the answer.)

## 5. Where we need JD (judgment, not code)
- Will you sit for ~30 minutes and label a validation set — pairwise "this beats that"
  and "this isn't a real Prospect" — on a sample of the live board? This is the single
  highest-value half-hour available; everything in 3.1 depends on it, and it's the only
  source of ground truth that exists.
- A gut check first, before formal labeling: scanning the current board, does the top of
  it feel right? Is anything in Prospect obviously wrong, or anything shelved that feels
  like a miss? Your instinct there tells us how big the validation gap actually is.

## The one-line marching order
**Prove the board is right before you fill it faster.** Build `evals/` and validate the
live scorer against JD's judgment; add product observability so the board can report that
it's right, not just that it ran; then — and only then — build Priority so the accurate
list becomes an actual decision. Keep the cheap safe wins (careers parsers, liveness
gate) rolling alongside. Report back with the answers to §4 and your proposed `evals/`
shape before writing it, and I'll pressure-test the design.
