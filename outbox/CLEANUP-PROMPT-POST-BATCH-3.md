<!--
HOW TO USE THIS FILE (this note is for JD, not the agent):
This is the post-batch-3 cleanup / pre-batch-4 hardening prompt — v2, with JD's six
batch-3 issues folded into Section 5, each with its ruling and a locking test. Paste
the whole thing into the Fable build chat (the one building JDMD23/NormanAI-CRMx). It
is grounded in a real read of the phase-0 branch after batch 3 plus the round-6
rulings (M1–M6). Nothing here invents work — it hardens what exists, fixes the six
batch-3 findings, and builds the one floor (observability) that's missing before the
automation goes live.
-->

# Norman — Post-Batch-3 Cleanup & Pre-Batch-4 Hardening (v2)

You are the world-class principal engineer continuing the Norman build
(**JDMD23/NormanAI-CRMx**), with **NormansBrain** as your knowledge base. Batch 3
has just loaded. Before batch 4, you will **clean, wire, prove, and harden** the
repository per this prompt — and build the one piece of substrate that must exist
before enrichment moves from JD's hands into code. Work in **small, verifiable
slices**, show JD each result in plain language, and **stop and report at the end**
(Section 4). Do not start batch 4 until JD says go.

---

## 0. The watcher's verdict (read this first — it frames everything)

I audited the `phase-0` branch as it stood after batch 3. The honest assessment:

**The foundation is strong, and unusually faithful to the design.** This is not
flattery — it's the state of the code:
- The **decision spine is built and correct**: intake → identity resolve → store →
  Fit score → status router → Notion projection → **reconcile**. The newest commit
  is the reconcile loop, and it implements round-5 L5's six laws *verbatim and cited*
  (adopt-before-heal, heal-machine-columns-only, self-logging, idempotent,
  per-company isolation, dry-run-first). The scorer cites J1 evidence-hysteresis,
  J3 heads-hysteresis, Unknown≠0, and the data-blind cap **in its own comments**.
- Every tunable is **validated config** (`config/fit-score.json`, `cadence.json`,
  `funding-velocity.json`, `industry-taxonomy.json`, `notion-board.json`) — the J6
  ruling and the config-validated-at-boot invariant, honored.
- **~150 tests across 11 files.** Harness-first held even though the scorer was
  pulled forward.

**The gap is the Phase-1 automation substrate — and one part of it is now urgent.**
Missing as code (all designed, none built): `core/observe`, a `core/trust` /
`core/guard` module boundary, `core/lanes`, the persistent browser daemon, and the
resilience/breaker stack. A grep for any observability wiring returns **nothing** —
no logging, no correlation IDs, no metrics, no tripwires.

**The one structural risk, stated plainly:** enrichment is currently **manual** —
JD is hand-measuring NYC headcount and careers and the code scores/routes/projects
it. That has been a *valuable dress rehearsal* (it surfaced the entire F–L ruling
set). But the board is now filling with hand-measured values **ahead of the
substrate meant to produce and watch them.** Batch 3 should be the **last
comfortable hand-driven batch.** Before batch 4, the watcher (observability) must
exist, or you will be scaling an automated process you cannot see.

So: the foundation is not the worry. **The floor under the next phase is.** This
prompt pours that floor and cleans the house, in priority order.

---

## 1. The cleanup & hardening, in strict priority order

Do these top-down. Each is a slice: build it, prove it with a test, show JD, move on.

### Priority 1 — Git & wiring hygiene (JD's explicit ask: "pushed accordingly, locally and on GitHub")
1. **Local == remote.** Confirm nothing is stranded uncommitted or unpushed. `git
   status` clean; the working tree matches `origin/phase-0`.
2. **Resolve the branch story.** `main` currently holds only the scaffold; all real
   work is on `phase-0`. `main` must not lie about the state of the build. Decide and
   **record the decision in an ADR**: either (recommended) **merge `phase-0` → `main`
   at this phase boundary** so `main` is always the current truth, or keep `phase-0`
   as a named integration branch and **tag** the batch-3 state. Do not leave `main`
   silently stale.
3. **One-command health gate.** A `make check` (or equivalent) that runs the full
   test suite + `ruff` + config-load validation, green, on the tip commit. If CI
   isn't wired, wire the minimal version now — the invariants are worthless if a red
   suite can be pushed.
4. **Prove config-validated-at-boot.** Feed a deliberately malformed `fit-score.json`
   and confirm the system **fails loudly at startup**, not silently at scoring time.
   One test locks it.

### Priority 2 — The observability floor (this is the "before it's too late" item — build it NOW)
Build a **minimal `core/observe`** before any lane is automated. Three things, and
**no more** (resist gold-plating — weight-class honesty, brain/00):
1. **A correlation ID threaded through every multi-step run.** One enrichment pass
   over one company gets one ID that appears in every log line and every change-log
   and ledger row it produces — so a run is traceable end-to-end (pillar B5,
   opentelemetry). This is the difference between "something went wrong somewhere"
   and "here is exactly what this run did."
2. **A work-state view derived from `check_ledger`.** You already have the table
   (`last_checked_at`, `last_outcome` ∈ success/partial/blocked/manual,
   `consecutive_failures`, `next_due_at`). Surface it as a queryable view / small CLI:
   *what ran, what outcome, what's blocked, what's overdue, what's failing
   repeatedly.* This is JD's literal question — "what is the agent doing, what's it
   getting right/wrong, what blocks is it in" — and the data is already being written;
   it just isn't visible.
3. **The L1 tripwires as live counters with thresholds** — even while the lanes are
   still manual: **challenge-frequency** (rolling window), **soft-block rate** (F3
   category d), and **Sales Nav commercial-use-limit throttle**. Wire the counters and
   their alert thresholds now, so the instant a lane goes automated they are already
   watching. Per L1/L2 these are the **precondition for the budget waiver being safe
   unattended** — the waiver traded a static safety (quota) for a dynamic one
   (monitoring), and the dynamic one has to exist before it's relied on.

Why this is Priority 2 and not later: you cannot verify that *any* other pattern held
in production without observability (pillar B5), and JD is about to move enrichment
from hand to code. **The watcher must exist before the thing it watches.**

### Priority 3 — Reconcile: prove the laws, wire the session-start sweep
The L5 laws are coded and cited. Now make them **adversarially provable and wired**:
1. **Adversarial tests for the laws that protect JD's edits:** a heal that *would*
   clobber a JD board edit must **fail a test**; a second sweep over a converged board
   must **plan nothing** (idempotency); a forced per-company failure must **not abort**
   the sweep (isolation). These three tests are the guarantee that the "one
   unforgivable failure" (silently reverting an operator edit) cannot regress.
2. **Wire the mandatory session-start sweep** as the actual first action of every
   working session — this is what notices "JD pasted a careers link while Norman was
   off" (the H6 gap). Confirm the **dry-run/diff runs first** against JD's real edits
   before anything writes.
3. **Stale-jd-manual surfacing (L5 #5):** confirm (or add) that a materially newer
   machine measurement surfaces as a **Changes delta** for JD, rather than either
   silently overwriting his value *or* letting a month-old manual value ossify. Both
   failure directions must be closed.

### Priority 4 — Pay down migration debt before it compounds (K3 / L4)
1. **Put the whole board on one ruler.** Re-measure the hand-measured NYC values (the
   `?facetGeoRegion=` geo-param values and the earlier JD-manual counts) onto the
   **pinned Sales Nav instrument** so every count and delta is comparable (K3). This
   is a **one-time migration job, not a recurring reconcile duty** — run it, verify,
   retire it.
2. **Run the replay audit (L4) immediately after**, to confirm the new instrument
   flips **no band silently**. A flip is a finding, not a surprise.
3. **Audit instrument + granularity tags (K3/G5):** every enrichment value must carry
   which instrument produced it and at what granularity (metro vs city floor). Fix any
   untagged values now, while the volume is still payable.

### Priority 5 — Mechanize the 8 invariants as CI, not convention
The handoff's non-negotiables must each be a **test that fails if violated**, not a
habit. Map the ~150 existing tests to the eight and fill the gaps:
single-write-path · verified-writes (write → read-back → confirm) · Unknown≠0 ·
identity-before-write · all-or-nothing lanes · config-validated-at-boot ·
field-level write authority · evidence-grounded LLM output. **A green suite that
doesn't cover an invariant is a false sense of safety** — name which invariant each
test defends, and write the missing ones.

### Priority 6 — ADR the round F–L decisions into the build repo
The lane rulings currently live only in NormansBrain
(`reviews/phase1-lane-design-decisions.md`). Distill the load-bearing ones into
**build-repo ADRs** so the runtime is self-documenting and doesn't depend on a remote
brain read (bus-factor, brain/08): the budget-waiver mode-scoping (attended vs
unattended, L1/L2), Sales Nav as the pinned ruler (K3), evidence-hysteresis (J1/J3),
the render protocol (K1), and review auto-resolution (L3). Short ADRs, one decision
each.

---

## 2. What NOT to do before batch 4 (scope honesty — this matters as much as the list above)
- **Do not** speculatively build the full browser daemon + every lane. Build
  `core/observe` (Priority 2) and, when JD is ready, **one** real lane (Sales Nav),
  prove it end-to-end, *then* decide the next. Weight-class matching (brain/00, E1).
- **Do not** scale the board further by hand past batch 3 without tagging every
  hand-value `jd-manual` + instrument-tagged, or you compound the migration debt
  (Priority 4) faster than you can pay it.
- **Do not** merge NormansBrain into the runtime. It informs; it never ships.
- **Do not** add a background reconcile timer yet — session-triggered is correct
  until the unattended cutover (L5). The timer is unattended-mode machinery.

---

## 3. The audit checklist (run this, report the results verbatim)
A pass/fail line for each, so "cleaned up" is verifiable, not a vibe:
- [ ] `git status` clean; `phase-0` fully pushed; `main` no longer lies about state (ADR recorded).
- [ ] `make check` green on the tip: tests + ruff + config-load validation.
- [ ] Malformed config fails **loudly at boot** (test proving it).
- [ ] `core/observe` exists: correlation IDs threaded, `check_ledger` work-view queryable, L1 tripwire counters live.
- [ ] Reconcile: clobber-a-JD-edit test **fails correctly**; double-sweep plans nothing; per-company failure isolated. Session-start sweep wired, dry-run-first.
- [ ] Stale-jd-manual surfaces as a Changes delta (test).
- [ ] Board on one ruler: hand-values re-measured onto Sales Nav; replay audit shows no silent flips; all values instrument+granularity tagged.
- [ ] The 8 invariants each mapped to a failing-if-violated test; gaps filled.
- [ ] Round F–L ADRs written into the build repo.

---

## 4. Report back to JD, then stop
Produce a short **State of the Build** note in plain language:
1. The audit checklist above, each line pass/fail with a one-line note.
2. What moved this cleanup, what you deliberately deferred, and why.
3. The honest one-liner: **is the foundation still strong, and is the observability
   floor now in place before batch 4?**
Then **stop and wait for JD.** Do not begin batch 4.

---

## 5. JD's batch-3 issues (v2 — folded in, each with the ruling and the locking test)
All six were ruled in NormansBrain round 6 (`reviews/phase1-lane-design-decisions.md`,
M1–M6). Every one becomes a **fix + a test that locks it** — a batch-3 miss not turned
into a test recurs in batch 4 (K1, "same reader, same bug"). Triage into the priority
list is noted per item.

**5.1 — Camp Network re-ask bug (M6) — HIGHEST PRIORITY, it's a trust bug.**
"Joe says: no careers page" returned after JD acked it, because the intake fires as an
event but never persists the durable state that suppresses the ask. Fix: acking
transitions the company to a durable `careers_status = no-page-per-jd` (jd-manual
provenance + date) that **suppresses the board ask, switches enrichment to the
LinkedIn-jobs fallback, and schedules careers re-discovery to +1 month (not
immediate).** **Locking test:** ack "no careers page" → run a reconcile sweep → assert
the "paste careers link" ask does not return and the state persists. *DataLane's "Joe:
paste careers link" rides the same mechanism — this fix makes that intake trustworthy
too.* → Fits **Priority 3** (reconcile correctness).

**5.2 — Velocity merge window (M1).** Fig Security's 21-day seed→A (same lead
investors) computed a noise "Fast." Fix: **two windows** — a short flat window (≤~14d,
collapse on time alone) and a wide window (≤~45d) that collapses **only when
corroborated** by a same-raise signal (shared lead investors / tranche labels). Both
tunable config, boot-validated; tag the collapsed event `announced-in-tranches`.
**Test:** Fig collapses (21d + same leads); a 21d gap with different leads stays two
rounds. → **Priority 1** (config) + a velocity test.

**5.3 — Funding total from duplicate/tranche rows (M2).** Daytona's rows doubled;
$38M headline kept. Standing rule: **the headline Total is authoritative — never sum
rows to get the total**; dedupe rows to `(round_type, announced_on)` for structure;
**cross-check the deduped-row sum vs the headline and drift-flag a material
divergence.** **Test:** duplicated tranche rows yield one structural round each, the
headline total is preserved, and an injected divergence raises a review flag.

**5.4 — Other-entity rows leaking into financials (M3).** Etherealize's "Ethereum
Institutional" seed and Daytona's "BeatAI" grant are the company acting as *investor*,
not raiser. Fix: **discriminate on DIRECTION (recipient vs investor), not a name
substring** — count the company's own inbound funding rounds; exclude rows attributed
to a *different named entity*; flag the ambiguous. (JD's name-match was reaching for
"is this row about a different entity" — encode it that way, or "require the company's
own name" will drop legitimate round-type-named raises.) **Test:** a raise row named
"Series A" counts; an outbound row named after another entity is excluded.

**5.5 — US-wide postings + verified NYC office (M4).** Fig shelved at Low NYC despite a
real 488 Madison office, because roles post "United States"/"Remote, U.S." Fix: a
**verified NYC office** turns "US-wide/remote, no explicit NYC" from a measured-0 into
**`nyc_jobs = Unknown`** (not 0, not a fabricated positive) — which, per J1, **may not
drive the Low-NYC exit.** The office blocks the demotion; the data-blind cap prevents
an unearned Prospect seat. NYC-*excluding* roles (explicit other cities, no office)
still exit. **Test:** Fig (US-wide + verified office) holds off the Low-NYC shelf; Echo
(Tel Aviv/SF, no office) still exits. *This one re-routes a live company — surface it
to JD explicitly when it lands.*

**5.6 — Embedded ATS boards are the majority (M5).** 5/12 Ashby boards were embed-only.
Confirm the two-phase lane (browser+embed-parse to bind → API to count) is the
**default**, and add a **static-discovery-hit-rate metric to `core/observe`** (now
~50% embed-only; a further drop means more browser binds = more account surface). No
behavior change — a validation and an observe metric. → **Priority 2** (observe).

*(v2 issued after batch 3. If a later batch surfaces a design question the brain
hasn't ruled on, flag it for JD — a new ruling belongs in NormansBrain first.)*
