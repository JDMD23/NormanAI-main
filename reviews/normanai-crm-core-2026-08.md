# Review: NormanAI-crm-core — 2026-08

- **Repo:** https://github.com/JDMD23/NormanAI-crm-core at `d960994`
- **What it is:** A production CRM runtime for VC/prospect sourcing: intake →
  multi-source enrichment (Crunchbase, careers/ATS, LinkedIn) → config-driven Fit
  Score → Second Pass ranking → deterministic operator update → Notion operator
  cards → daily review. ~37k lines of Python, 75 scripts, 18 configs, 82 tests,
  119 docs, a schema-versioned causal outbox, shadow/live release gating.
- **Stated goal:** take every highly relevant, effective pattern from the 28
  studied repos and use it to build a stronger next version.
- **Context:** solo/small-team, AI-assisted build (the repo used the superpowers
  methodology — `docs/superpowers/` — and shows heavy agent involvement). Real
  operator, real Notion board, real money decisions downstream. Currently in
  read-only shadow mode pending a signed cutover.

## Verdict

This is not a naive codebase — it independently reinvented a large fraction of
the brain, and several pieces are genuinely good: a **config-as-formula scoring
engine**, a **schema-versioned causal outbox with exactly-once receipts**,
**identity-before-writes**, **missing≠zero renormalization**, and **shadow/live
gating**. The single highest-leverage move is to turn the scoring engine's
correctness into a **CI-gated evaluation harness** (you already have the labeled
data and a comparison script — it isn't a regression gate yet); today "is this
weight change an improvement or luck?" is answered by human review, not a number.
Right behind it: **property-test the scoring/outbox invariants** (they are
textbook Hypothesis targets), and **collapse the doc/authority sprawl** (119 docs
+ 40 receipts + an "authority map" fighting confusion + 13 superseded prompt
files) into a generated, CI-checked single source of truth with explicit
tombstones. The one hard problem is strategic, not code: the enrichment layer's
value rests on **logged-in Crunchbase/LinkedIn scraping**, whose legitimacy
ceiling caps everything built above it — your public-ATS careers lane is on far
firmer ground than the other two.

## What it already gets right (and the study that validates each)

Naming these first because they are real strengths, and the plan below builds on
them rather than churning them.

| Existing mechanism | Study it validates | Note |
|---|---|---|
| `fit_score.py` (pure engine) + `fit-score-weights.json` (weights/bands/enable) | **JustHireMe** (deterministic rubric core), **jsonschema** (spec-as-data), **RapidFuzz** (logic/impl split) | "Change weights in config, rescore the board" is exactly right. Judgment in a rubric is measurable. |
| `lib/causal_outbox.py` — schema-versioned intents + exactly-once score/lane receipts | **superpowers/brain-09** (write-ahead ledger), **brain-04** (event-sourced facts), **brain-05** (idempotency keys) | The best-engineered thing in the repo. Recoverable per-page intents survive crashes. |
| Identity (name+domain **or** LinkedIn) required before funding/headcount writes | **linkedin-mcp-server** (provable ownership before mutation), **ats-scrapers** (identity-first) | "Search is a lead only. Unknown ≠ 0." Correct epistemics. |
| Missing/disabled components rescale to 100; `dataBlindCap` | **brain-04** (nullability is a modeling statement), **graphify** (don't fabricate certainty) | Missing ≠ zero is the rule most scoring systems get wrong. |
| Shadow/live compiler, release-readiness gate, one-mode invariant | **brain-06** (canary/expand-contract), **autoresearch** (frozen-judge discipline), **langchain** (rename-and-freeze) | "Exactly one compiler mode so an old contract can't silently become active" is a real safety property. |
| `skills/prospect-research/{crunchbase,careers}` with consensus/evidence/benchmarks | **anthropic-skills** (knowledge-delta), **ats-scrapers** (per-source adapters) | The skill decomposition instinct is right. |
| `notion_write_guard.py`, `linkedin_security.py`, `browser-human-pace.json` | **linkedin-mcp-server** (guarded writes, human-paced, security module) | The guard instincts exist — the plan tightens them into invariants. |
| `crm_calibration_compare.py` — frozen v3 vs shadow-v4 vs approved JD labels | **JustHireMe** (labeled eval), **graphify** (same-harness comparison) | You are *one step* from a real eval harness. This is the biggest latent asset. |

## Findings, ranked by impact

### F1. Turn calibration into a CI-gated scoring eval harness — CRITICAL

- **Source:** JustHireMe (`backend/evals/`), graphify (benchmark fairness).
- **Target:** `scripts/crm_calibration_compare.py` + `fit_score.score_row` +
  `config/crm-calibration-baseline-v1.json` + JD labels.
- **Why here:** The Fit Score *is* the product; every weight edit reranks the
  operator's world. You already compare scores against approved JD labels — but
  it's a manual script, not a gate. Right now a scoring change ships on human
  eyeballing, which JustHireMe names exactly: "before this harness there was no
  way to tell an improvement from a lucky change." You have the labels and the
  comparator; you're missing the gate.
- **Change:** Promote calibration to a harness with JustHireMe's shape:
  labeled `(company_row → expected band/rank)` cases run through the real
  `score_row`; **invariant cases** that fail CI alone (e.g. "biotech excluded
  stays excluded," "a data-blind row never exceeds `dataBlindCap`," "an in-region
  confirmed head-count company never floored"); **directional bounds** (in-fit
  cases set a `min` you fear dropping; exclusions set a `max`), calibrated with a
  few points of headroom. Wire it into `.github/workflows/ci.yml` beside the
  pytest step. Non-deterministic inputs (live enrichment) are stubbed so the
  score is reproducible.
- **Effort:** ~3–5 days (the data and comparator exist; this is packaging +
  labeling + a CI gate).

### F2. Property-test the scoring and outbox invariants — HIGH

- **Source:** Hypothesis (property-based testing, shrink-to-minimal).
- **Target:** `scripts/fit_score.py`, `scripts/lib/causal_outbox.py`; 82
  example-based tests today.
- **Why here:** `fit_score`'s renormalization is a *pure function with stated
  invariants* — the ideal property-testing target. Example tests check the rows
  you thought of; a property test checks the whole input space and hands back the
  minimal failing row.
- **Change:** Add `@given` properties: for any subset of enabled components and
  any input row, `0 ≤ Fit Score ≤ 100`; disabling a component never raises another
  component's absolute contribution incorrectly; missing input ≠ zero contribution;
  enabled weights always rescale to 100. For the outbox: applying the same intent
  twice is identical to applying it once (exactly-once is a property, not an
  example); a receipt round-trips. These find the edge cases 82 examples won't.
- **Effort:** ~2–3 days; highest ROI on the two files where a bug is most expensive.

### F3. Collapse doc/authority sprawl into a generated, checked single source of truth — HIGH

- **Source:** ECC (three-conflicting-catalogs failure), agency-agents
  (`check-divisions.sh` CI-checked duplication), JustHireMe (tombstones),
  mattpocock (lifecycle buckets).
- **Target:** 119 `docs/*.md` + 40 receipts; the README "Authority map"; the 13
  superseded `FABLE_*` prompt files under
  `docs/archive/operator-experience-superseded/`.
- **Why here:** The README needs an "authority map" *because* the docs sprawl —
  that map is a good mitigation of a real disease (ECC shipped three different
  catalog counts in three hand-maintained docs; you're one drift away from the
  same). Superseded prompt/spec files left in-tree mislead the next agent with
  authority — exactly the guidance-decay JustHireMe tombstones.
- **Change:** (a) Make the authority map **generated** from a single machine-
  readable manifest (`config/authority-map.json`: question → owning doc), and add
  a CI check that fails if a doc claims authority the manifest doesn't grant
  (agency-agents' pattern). (b) **Tombstone** every superseded doc with an explicit
  self-disclaiming header ("Superseded by X. Do not treat as runtime authority.")
  instead of relying on a folder name. (c) Move receipts out of `docs/` into a
  `state/receipts/` tree that isn't confused with authority.
- **Effort:** ~2–4 days; large payoff for every future agent session and for you.

### F4. Split the mega-scripts into functional core + imperative shell — HIGH

- **Source:** langchain (the 6.7k-line file cautionary tale), graphify (7-stage
  pure pipeline), brain-02 (functional core / imperative shell).
- **Target:** `crm_funding_handoff.py` (1,652), `crm_second_pass_agent.py`
  (1,336), `crm_score_agent.py` (1,300).
- **Why here:** You already proved you can do this — `fit_score.py` is a pure
  engine with the I/O pushed out. The three biggest files haven't had that
  treatment: scoring/ranking decisions are braided with Notion reads/writes,
  which makes them hard to test (F1/F2 need the pure core exposed) and hard to
  reason about. This is the precondition that *unblocks* F1 and F2 on second-pass
  and score-agent, not just fit_score.
- **Change:** Extract the pure decision logic (ranking math, status routing,
  handoff selection) into importable functions over plain dicts; leave the scripts
  as thin shells that fetch → call pure core → write. Test the core directly.
- **Effort:** ~1 week per file, incremental (preparatory-refactoring style, one
  behavior-preserving commit at a time — brain-03).

### F5. Unify the three enrichment lanes behind an adapter registry — MEDIUM

- **Source:** ats-scrapers (ABC + decorator registry; capability as data;
  per-adapter docstrings capturing the source's quirks), brain-05 provider pattern.
- **Target:** `crm_crunchbase_agent.py` (1,028), `crm_careers_agent.py` (814),
  `crm_linkedin_agent.py` (686) + their `skills/prospect-research/*` engines.
- **Why here:** Three lanes with parallel structure (identity → fetch → evidence →
  write, Need-\* markers, receipts) implemented as three large separate scripts.
  ats-scrapers runs 50 sources off one `BaseScraper` + registry because a new
  source is one self-registering file. Your three would share the outbox, receipt,
  identity, and Need-\* machinery through one `BaseLane`, with each source's
  quirks in a docstring beside it (the knowledge-delta) — and a 4th source (e.g.
  a compliant funding API) becomes a small adapter, not a fourth 1k-line script.
- **Change:** Define `BaseLane` (identity, fetch, evidence, write-through-guard,
  Need-\* lifecycle) + a lane registry; port the three lanes onto it. Declare
  per-lane capability (engine, rate limits, auth mode) as data.
- **Effort:** ~1–2 weeks; do it *after* F4 exposes the pure cores.

### F6. Harden the scraper posture: coherence-not-invisibility + one write path — MEDIUM

- **Source:** linkedin-mcp-server (browser coherence rules; `_owned()` as the sole
  destructive path), brain-04 (one writer per value).
- **Target:** `lib/browser_coordination.py`, `linkedin_security.py`,
  `notion_write_guard.py`, `config/browser-human-pace.json`.
- **Why here:** Your instincts are right but partial. linkedin-mcp's rules are
  sharper and battle-tested: *the browser must not contradict itself* (coherence
  is provable, invisibility isn't); *never inject a fingerprint*; *detect on
  locale-independent signals*; and route **every** Notion write through the guard
  the way linkedin-mcp routes every delete through `_owned()` — make
  `notion_write_guard` the only write path, enforced, not conventional.
- **Change:** Adopt the coherence rules as documented invariants in the browser
  module; assert (in tests or a lint) that no Notion write bypasses the guard.
- **Effort:** ~3–5 days.

### F7. Add a standing `rationale.md` and a 3-condition ADR gate — MEDIUM

- **Source:** OpenTelemetry (`rationale.md`), mattpocock (ADR gate: hard-to-reverse
  ∧ surprising ∧ real-tradeoff), gstack (decisions-with-scars).
- **Target:** the spec/authority docs and `docs/superpowers/`.
- **Why here:** You have *many* authoritative specs but no single "why is it
  shaped this way" — why the shadow/live compiler, why the causal outbox, why
  identity-first, why biotech is excluded. That reasoning is currently spread
  across dated audits and will be lost. OTel keeps one `rationale.md` precisely so
  "decisions don't get lost over time."
- **Change:** One `docs/rationale.md` capturing the load-bearing irreversible
  decisions and their reasons; gate new ADRs on the three conditions so you write
  them only where they earn it.
- **Effort:** ~1–2 days.

### F8. Expose the CRM as annotated agent tools; dual-reader daily review — LOW/MEDIUM

- **Source:** linkedin-mcp-server + anthropic-skills (tool interfaces are APIs for
  agents: readonly/mutating annotations, confirmation-gated writes, section
  selection, partial-failure returns), rendergit (dual-reader outputs).
- **Target:** `agent_cli.py`, the daily-review/operator-card surface.
- **Why here:** If Norman is agent-operated, the enrichment/score/second-pass
  actions should be tools with explicit read-only vs mutating hints, writes
  confirmation-gated, and partial-failure returns (one lane fails, the others
  still report). And the daily review is human-facing — add an LLM-view of board
  state (rendergit's Human/LLM toggle) so an agent can consume it cheaply.
- **Effort:** ~1 week if you go the MCP route; the dual-reader view is ~1 day.

## The hard problem (name it plainly)

Two of your three enrichment lanes — Crunchbase and LinkedIn — run against
**logged-in sessions of services whose terms forbid automation**. The ats-scrapers
study established the rule the whole collection kept confirming: *the legitimacy
of the data source is the ceiling on everything you can responsibly build above
it.* Your **careers/ATS lane hits public endpoints and is on firm ground**; the
other two are the fragile, legally-exposed, redesign-brittle foundation under the
most valuable signals (funding velocity, NYC headcount). Every investment above
them — the outbox, the eval harness, the operator cards — compounds on a base
that can be cut off by a ToS enforcement action or a login-wall change.

This isn't a reason to stop; it's a reason to **derisk the base deliberately**:
prefer official/compliant paths where the data justifies the cost (Crunchbase has
a licensed API; LinkedIn firmographics are available through compliant data
vendors — the orca and JustHireMe studies both routed LinkedIn data through a
provider rather than a logged-in session for exactly this reason). Treat the
logged-in lanes as the *fallback* tier, not the primary, and let the
capability-ladder pattern (RapidFuzz, Scrapling) make the official path the
default with the scrape as graceful degradation. This is the single decision with
the largest effect on whether Norman is still running in a year.

## Suggested sequence

**Weeks 1–2 (make correctness measurable — do these first):**
1. F1 scoring eval harness in CI (you already have the data). 
2. F2 property tests on `fit_score` + `causal_outbox`.
3. F3 doc/authority SSOT + tombstones (cheap, compounding, helps every later step).

**Weeks 3–5 (make the core reasonable):**
4. F4 functional-core split of the three mega-scripts (unblocks F1/F2 on
   second-pass and score-agent).
5. F7 `rationale.md` (write it *while* refactoring, when the reasoning is fresh).

**Weeks 6–8 (consolidate and derisk):**
6. F5 lane adapter registry (after F4).
7. F6 scraper-posture hardening + single write path.
8. Begin the **hard-problem** work: pilot one compliant data path (Crunchbase API
   or a LinkedIn data vendor) behind the existing lane interface.

**Later / optional:** F8 MCP tool surface + dual-reader review.

## What NOT to change

- **The causal outbox.** It's the best-engineered part; leave it, and route the
  new lane registry (F5) *through* it, don't replace it.
- **Config-as-formula scoring.** Don't move Fit Score logic back into code to
  "simplify" — the data-driven formula is a strength (jsonschema/JustHireMe both
  validate it). Sharpen it with F1/F2 instead.
- **Shadow/live gating and the one-mode invariant.** Keep it; it's real safety.
- **Don't chase microservices or a rewrite.** This is a modular monolith with a
  clean scoring core and a good outbox — the right architecture at this scale
  (brain-02). The work is decomposition and verification inside it, not a new
  system.
- **Don't add more docs to fix the doc problem.** F3 is *fewer, generated,
  tombstoned* — resist the instinct to write another authority doc.
