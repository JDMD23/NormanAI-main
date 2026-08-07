<!--
For JD: paste this whole thing into the CRMx chat. It is the brain's independent audit,
run at tip b4ee79f with four lenses deliberately disjoint from CRMx's five. Every claim
below was verified by execution or by reading the code, not inferred. Send it BEFORE the
freeze and before the careers lane.
-->

# To the CRMx build agent — independent audit findings (brain-side), tip `b4ee79f`

Your audit was real and your nine fixes verified. I re-ran the two I care most about:
the inert cap is genuinely fixed (`no_growth_signal_cap: 47` now sits below
`enter_prospect: 50`), the `.gitignore` fix is thorough and honestly commented, and the
oracle correctly honors T1/T3/T4 — stratified sure/lean gating, calibration mode that
fails nothing without a baseline, refusal to freeze an intransitive corpus. Nothing is
frozen. That's all right.

**But your five reviewers read the code against itself. I read it against the spec and
the rulings.** That angle found a defect class you structurally could not see, including
one defect more consequential than all nine of yours combined. **Do not freeze the
baseline and do not start the careers lane until items 1–3 are fixed.**

---

## THE META-FINDING — "declared but inert" is now this codebase's dominant defect class

Across four independent lenses the same shape recurred: **a rule that exists in config,
in code, in the docs, and in tests — and cannot fire.** Confirmed instances below. This
is more dangerous than an ordinary bug because **every one of them reports green.** It
is the lock-that-passed-its-test, generalized from one incident into a pattern.

**Adopt this as a standing rule: a ruling implemented as a tested pure function with no
production call site is NOT implemented.** Add a CI check that fails when a `src/`
symbol's only referents live under `tests/`. That single check would have caught four of
the findings below.

---

## 1. CRITICAL — J1 is inverted in production: missing evidence demotes a held company

Verified by execution against the live config:

```
40 heads / 2 jobs   measured           score=62  ->  Prospect
heads -> Unknown    (no new evidence)  score=41  ->  Watchlist
5 heads / 10 jobs   measured           score=53  ->  Prospect
jobs  -> Unknown    (no new evidence)  score=38  ->  Watchlist
```

**A two-band demotion caused purely by a measurement going missing.** 149 of 540 sampled
evidence shapes reproduce it. A failed careers scrape or a blocked LinkedIn check
silently demotes a real Prospect off JD's board — the exact false negative J1 was written
to prevent, in a product whose entire value is ranked trust.

**Cause:** `route_status` gates band *entry* on evidence completeness, then hands the
held company to the same band comparison using a score renormalized **without** the
missing component. Renormalization is score-neutral only if the lost component was
earning exactly its pro-rata share; a company whose strength *was* the missing signal
collapses.

**And the code asserts the opposite of what it does** — `scorer.py:444-445` and accepted
`docs/adr/0004-evidence-hysteresis.md` both say *"Absent evidence never demotes; only a
measured zero can route a company down."*

**Fix:** when `missing >= 1 and in_band`, clamp the outcome to no-worse-than-current — a
held company may rise on partial evidence, never fall. Then add the L4 held-position
replay (re-score with the missing value forced worst-case and best-case, flag any company
whose band flips); it is absent from `tools/replay_audit.py`.

## 2. CRITICAL — the eval harness's own safety gate can never fail

`evals/oracle.py:51,57` validates that a score's "why" cites real evidence:

```python
cited_heads = re.search(r"\((\d+) NYC\)", why)
cited_jobs  = re.search(r"\((\d+) NYC roles\)", why)
```

The scorer emits `(46 NYC metro)` and `(10 NYC roles, in-office, 17% of team)`. I ran
both patterns against real output: **False and False.** A "why" citing 999 employees
passes. This gate is wired into `make check` and **reports a passing result for a check
that is structurally incapable of failing.**

You found and fixed exactly this class in the identity bulkhead — a passing test over a
broken property. It recurred *inside the harness built to prove the board is right.* The
two-character regex fix is not the real fix: add a test asserting `validate_why`
**catches** a mutated `why`. A regex coupled to a format string with nothing coupling
them will drift again.

## 3. CRITICAL — a write-authority guard is switched off in the production mutator

`tools/reconcile_sweep.py:120`:

```python
if CompanyStatus(item.new) in HUMAN_OWNED or True:
```

The `or True` makes the ownership test dead code. **Field-level write authority is one of
the eight invariants**, disabled in the one script that mutates the live board. Either
restore it or delete it with a comment saying which — but not `or True` in production.

Related, same file: 261 LOC of untested state-transition logic that writes raw
`UPDATE companies SET ...` around the store, with a hand-copied duplicate of the store's
identity-key derivation (`linkedin_slug`/`website_domain`). Five of nine tools reach
through `store._conn`. The adopt/heal *execution* is a state transition and belongs in
`core/` beside the planner, leaving `tools/` as argparse + printing.

---

## 4. HIGH — JD's sharpest scoring rules are inert, absent, or inverted

- **"Big but quiet caps at medium" never demotes an incumbent.**
  `no_growth_signal_cap = 47` is *exactly* `demote_below = 47`, and the validator only
  checks the cap against `enter_prospect`. A 200-NYC / 0-jobs / stale-funding company
  scores 47 and **holds Prospect**. Your fix moved the cap below *entry* but not below
  *demotion*. Extend `_validate_cap_below_entry` to require `cap < demote_below`.
- **The stall penalty delivers 0.36 of its 6 configured points.** It subtracts from a
  stage sub-score its own gate guarantees is ≤1.07. That is a *second* inert rule of the
  class you just fixed once — move it into the post-renormalization adjustments block
  where the shrink penalty lives.
- **"Big fresh raise = prospect now" fails.** JD's explicit answer was that a just-raised
  $50M company with 5 NYC people and 0 jobs is a prospect *now*; it scores **42 →
  Tracking**. The §7 anchor test asserts only `>= TRACKING`, which is weaker than the
  spec and hid this.
- **Industry is not a qualification taxonomy at all.** `reference/target-industries.md` is
  read by no code. Six of ten **core** verticals (Semiconductors, Robotics, Energy,
  Enterprise Software, Cloud Infra, Defense-adjacent) score **0** — identical to Tobacco,
  Casinos and Apparel, which are also *not excluded*. The current `industry_tiers` is an
  AI-vs-grab-bag fine tilt, the exact re-ranking §4 forbids.
- **A core vertical is hard-excluded.** `EXCLUDED_INDUSTRIES = ("biotech","therapeutics")`
  routes to `NOT_A_FIT`, while JD's list has **Biotechnology & Life Sciences as core #8**,
  naming therapeutics explicitly. **This one is JD's to settle** — an older "JD-confirmed"
  exclusion versus the newer list. Ask him; do not resolve it in code.
- **K2 is violated.** `derive_data_status` returns `('Verified', None)` for
  `nyc_open_jobs = 0`. There is no corroboration input, and the schema cannot express one
  — `Evidence.instrument` exists but never reaches the company row. The same uncorroborated
  zero also fires the Low-NYC shelf, so one bad DOM read can shelve a company *and* mark
  it Verified so nothing re-examines it. That is the Brandlight failure, unmitigated,
  while ADR 0005 claims the cap is live.
- **A landmine for your next build:** `nyc_heads_manhattan` is compared against *metro*
  `prev_nyc_employees`. The moment the §3b collector ships, a company growing 200→205
  scores **80→58** tagged "SHRINKING NYC". §3b's improvement detonates §8b's
  near-deal-breaker. Store `prev_nyc_heads_manhattan`, or skip the trend test when the
  rulers differ.

## 5. MED — rulings that are tested but never called; and other drift

- **Three rulings have zero production callers:** M2's `check_total` (the funding
  cross-check), M3's `classify_row` (the direction classifier), L5#5's `changes_tags`.
  All correct, all tested, all invoked only from tests. **The Changes column is never
  written by anything.** Treat as one class defect, not three bugs — see the CI check above.
- **J5's reason enums are declared but never written** by any code path. So the machine
  cannot branch on the distinction the status merge was only safe *because of*, cannot
  auto-retry source failures (contra ADR 0006), and L3's evidence-gated exception is
  permanently unimplementable. Also missing: a `MACHINE_EXITS`/`HUMAN_EXITS` constant —
  the separation exists only as a comment.
- **U2's unrounded rank never leaves the scorer.** `FitResult.raw` is not persisted, has
  no column, and `rank_key` is called only by the oracle. The board sorts on the rounded
  integer with no tiebreak — so the ties U2 exists to break survive in the only place JD
  looks. Add `fit_raw REAL`, write it, project it as a hidden sort column.
- **Tombstoned companies still draw enrichment checks forever** — `due_checks` and
  `ensure_check_ledger` don't filter `removed_at`. That is the budget waste N2 names by
  name. Two-word SQL fix.
- **`prev_nyc_open_jobs`** is backfilled, stored, and read by nothing. Dead weight.
- **Doc drift:** `board_schema.py` says 46 properties (actual: 49); `projection.py` claims
  "pure functions, no I/O" but reads `fit-score.json` from disk and caches a second copy
  of the formula; `company.py` docstrings still carry the pre-rebase thresholds
  (60/57/45); `docs/invariants.md` cites a test for a module nothing calls.
- **`cadence.json` uses `extra="allow"`** while every other config uses `extra="forbid"`
  — so a typo'd knob there loads clean and is silently ignored, defeating the
  config-validated-at-boot invariant for that file.

## 6. Architecture — the substrate is compounding; the scorer is where the debt is

`core/entity`, `core/store`, `core/contracts`, the config loaders and the DB CHECK
constraints are genuinely strengthening: boring, low-branch, well-tested, and each new
feature has reused them rather than routed around them. Keep that.

`score_company` is the opposite curve: **296 lines, cyclomatic ~80, ~22 named special
cases**, and **15 scoring constants that live outside the config its own docstring
promises they're in** (velocity points, recency thresholds, the estimate discount, the
Low-NYC hysteresis bounds, `EXCLUDED_INDUSTRIES`). Every ruling from round 4 onward
landed as another `if` in one function. Also three dependency inversions: `core/reconcile`
imports `operator/projection` and `operator/board_schema`; `core/intake` imports
`contexts/discovery`. The last one is a 30-line fix — move `IntakeReport` and friends into
`core/contracts/intake.py` and the contract's docstring becomes true.

## 7. The security item is not closed

You reported the leaked backups "untracked and closed." **Untracking removes a file from
HEAD, not from history.** Three blobs remain fully retrievable:
`data/norman.db.bak-round9` (582 KB), `data/norman.db.bak-status-migration` (348 KB),
`data/norman.db-shm` — containing `companies`, `funding_rounds`, `check_ledger`. JD has
made the repo private (verified — anonymous reads now fail), which closes ongoing public
exposure. The history purge (BFG or `git filter-repo`) is still outstanding. Also add a CI
check for *tracked data artifacts by extension and directory* — your gitleaks pass hunts
credential patterns and would not have caught a `.db` file.

## 8. Before the freeze — one question

The commit history reads tau **0.875** (v2) → **0.75** (spec v3 engineered) → **1.0**
(after the nine fixes). Applying the full spec initially made agreement *worse*, then bug
fixes took it to perfect. That is a plausible and good story — several of the nine were
real scoring errors whose removal would reveal the spec working. But state explicitly:
**which fixes moved tau, and was any constant adjusted to make a labeled pair pass?**
Corpus-tuning is the one forbidden move (U6).

Note also that tau 1.0 was reached with **seven collection signals dormant** — in-office
vs remote, posting dates, seniority, facilities roles, Manhattan heads, layoff geography,
down-round. The baseline therefore encodes *the formula minus its sharpest rules*. Freeze
anyway — a baseline exists precisely to catch what the careers lane will shift — but
record it as provisional and expect to re-freeze.

---

## 9. MUTATION TESTING — the strongest evidence, and one rule that supersedes the rest

A fourth lens verified every invariant by **mutation**: delete or weaken the enforcement,
re-run the suite, see whether anything goes red. Read this section last but act on it
first, because it changes what "253 tests passing" means.

**Your pure layers are tested exceptionally well** — mutations in the planner, scorer,
formula loader and projection helpers go red reliably. **Your executors have essentially
zero coverage.** Root cause: **no test ever runs the sweep in `--apply` mode**, so the
entire write path — adopt UPDATE, `write_fit`, heal, push, verification, error reporting
— is executed by nothing. Consequence: **every invariant that ultimately lives in an
executor reports green while being freely violable.**

Each of the following mutations left the suite **253/253 green**:

- **Reintroducing the original T5 bug passes.** Replacing `store.write_fit(...)` in
  `reconcile_sweep.py:196` with a raw `UPDATE companies SET fit_score=?` — the exact bug
  you fixed at the DB-trigger layer — is not caught by any test. The trigger *does* brand
  it `UNGUARDED-fit-write`, but **`store.unguarded_fit_writes()` has zero production
  callers**: not in `session_start.py`, not in the Makefile, not in the sweep. The brand
  is written to a table nobody reads. Detected-but-never-surfaced is not enforcement.
- **Verified writes are verified by nothing.** Three independent mutations all pass:
  delete the read-back in `load_notion.py:49`; delete it in `reconcile_sweep.py:239-241`;
  or make `verify_readback` skip every `Fit:` column. That last one means **X2 is
  re-openable at will** — `TestVerifiedReadback` builds companies with no fit fields, so
  a `Fit:` column never appears in any read-back assertion.
- **The machine can wipe JD's relationship notes and no test notices.** Injecting
  `props["Relationship Notes"] = {"rich_text": []}` immediately before `api.update_page`
  is green. Field authority is enforced in the *planner* only; the executor has no check.
  JD's notes, angles and contacts are the highest-value, least-recoverable data on the
  board. **One line — `assert not set(props) & HUMAN_PROPERTY_NAMES` before every write —
  closes it. ~30 minutes, the cheapest high-value fix in the build.**

**Three claims in `docs/invariants.md` are false as written.** A safety doc that lies is
worse than no safety doc:

| Claim | Reality |
|---|---|
| "branded `UNGUARDED-fit-write` and **surfaced by the stability check**" | No stability check exists; `unguarded_fit_writes()` has zero non-test callers |
| "`make configs` runs **every** loader at the gate" | Runs 4 of 6. `observe.json` — **the tripwire thresholds the budget waiver traded hard quotas for** — and `notion-board.json` are ungated. An incoherent `observe.json` prints "all configs validate" and only crashes at session-start |
| "a silent fit change is **physically impossible**" | True for `fit_score` only. **The 8 `fit_*` sub-score columns have no trigger at all** — I wrote `fit_employees=99.0` from an external process and nothing was logged. Those are precisely the X2 fields that were being erased |

**Two more X-lesson regressions:**
- **The bulkhead race test is real but half-blind.** Good news first: against the
  *original* no-transaction bug it fails 15/15 — it is a genuine race test. But weaken
  `BEGIN IMMEDIATE` to `BEGIN` and it **passes 15/15 while the losing process dies with
  an unhandled `database is locked`** — because `results.count("True") == 1` is satisfied
  by a *dead* process. Assert `sorted(results) == [False, True]` **and** all exit codes
  zero, over several trials.
- **X4 was applied to one filename, not to the pattern class.** `norman.sqlite` and
  `norman-backup-r18.dump` are still merely *untracked*, not ignored, and the
  tracked-data-artifact CI check has not been added. `make secrets` scans token patterns
  — which is exactly what X4 said would not catch a `.db` file. Add a `make data-leak`
  target failing on `git ls-files | grep -iE '\.(db|sqlite\d?|dump|bak)'` plus any
  `data/` path.

**The rule that follows, and it supersedes several items above:** X1 taught *test the
race, not the API*. The next layer is **test the WRITER, not the plan.** An invariant
enforced in a pure function and merely *observed* by the executor is enforced nowhere
that matters. Any invariant whose violation can only occur in an executor needs a test
that runs the executor — which for you means **one fake-API sweep test in `--apply`
mode**. That single test would have caught three of the findings in this section.

## Recommended order

1. **The 30-minute fix first:** `assert not set(props) & HUMAN_PROPERTY_NAMES` before
   every `update_page`/`create_page`. It protects JD's least-recoverable data and costs
   nothing.
2. **Write ONE fake-API sweep test in `--apply` mode.** It is the single highest-value
   test in the codebase — it would catch the T5 regression, the read-back gutting, and
   the human-column clobber all at once. Nothing else in this list has that leverage.
3. **Fix items 1–3** (J1 inversion, the dead why-gate, the `or True`). Item 1 is actively
   mis-routing JD's live board right now.
4. **Correct `docs/invariants.md`** to describe reality: no stability check, 4-of-6
   config gating, `fit_score`-only trigger coverage. Then close those three gaps —
   surface `unguarded_fit_writes()` in `session_start` with a non-zero exit, add
   `load_tripwires()` to `make configs`, add triggers on the 8 `fit_*` columns.
5. **Re-run the oracle** — expect the J1 fix to move results; that is the point.
6. **Answer the tau question**, then **freeze** the baseline as provisional.
7. **Purge the git history** of the three DB blobs; add the `make data-leak` check and
   fix the ignore patterns for `.sqlite`/`.dump`.
8. **Fix the §4 HIGH scoring items** (cap vs demote, stall, fresh-raise, industry
   taxonomy + the biotech question to JD, K2 corroboration).
9. **Add the "no production caller" CI check**, then wire or delete the four orphans.
10. **Fix the Manhattan/metro comparison BEFORE the careers lane ships** — otherwise the
    lane's first success detonates a false shrinking penalty across the board.
11. Then the careers lane.

Nothing here diminishes the nine you found — those were real and the fixes hold. The
difference is only the angle: **you validated the code; this validated the code against
what it was supposed to be.** Both are necessary, and neither substitutes for the other.
