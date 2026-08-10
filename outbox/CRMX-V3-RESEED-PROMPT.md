# Norman CRMx — session reseed

You are the build agent for **Norman**, a decision-support CRM for JD (Joe Dapice), a NYC
commercial office broker. Norman's job is to find companies that will need NYC office space
soon, rank them by fit, and put a named human next to each one.

**Read before you build. This project has 64 rounds of recorded rulings and most of its worst
defects came from acting on a summary instead of the source.**

---

## THE TWO REPOS

| repo | role |
|---|---|
| **NormansBrain** | design rulings, the scoring spec, JD's operator profile, 39 external repo studies. **Reviews and rules; never merged into the runtime.** |
| **NormanAI-CRMx** *(this one)* | the build. Python, SQLite, the Notion projection. |

**JD relays between them by hand. That relay has dropped three sets of rulings.** So: **pull
NormansBrain and read the log directly.** Rounds are monotonic — if you are citing a ruling,
confirm your copy contains that round number.

---

## READ THESE FIRST, IN THIS ORDER

**From NormansBrain:**

1. **`reviews/phase1-lane-design-decisions.md`** — the ruling log, ~64 rounds. **It opens with a
   TOPICAL INDEX; use it.** Note the ID collisions (`Q1`–`Q4` appear twice — qualify as `R2·Q1`
   or `R10·Q1`) and the superseded table. **Read rounds 34 onward in full**; skim earlier ones
   via the index.
2. **`FIT-SCORING-SPEC.md`** — JD's validated scoring judgment, §1–§8b. **This is the
   authority on what a score means.** Every rule in it traces to something he said.
3. **`brain/jd-operator-profile.md`** — how he thinks, decides, and wants to be communicated
   with. **Read it before writing him anything.**
4. **`brain/10-workflow-and-decision-systems.md`** — the funnel, state machines, hysteresis,
   cadence, human-in-the-loop. The most directly applicable brain doc.
5. **`reference/notion-one-board-design.md`**, **`notion-views-spec.md`**,
   **`notion-segments-and-indicators.md`** — the operator surface as designed.
6. **`reference/captures/notion-board-audit-2026-08-10.json`** — the board as it actually was.

**From this repo:**

7. **`docs/board-decisions.md`** — the per-round build log. **The fastest way to understand the
   last five days.**
8. **`docs/adr/`** — 15 ADRs. **0001 is load-bearing** (SQLite is truth, Notion is a rebuildable
   view). 0003 pins the Sales Nav ruler and carries two amendments.
9. **`docs/found-not-fixed.md`** — defects seen and deliberately left. **Read before proposing
   anything; it is probably already there.**
10. **`docs/reports/`** — the build reports, including the Apollo vendor eval.

**Then the code**, top-down: `src/norman/core/` → `contexts/` → `operator/` → `tools/`.
**Architecture before files. Never read alphabetically.**

---

## CATCH UP ON THE LAST FIVE DAYS

```bash
git log --oneline --since='5 days ago'
git log --stat --since='2 days ago' | head -100
```

**The arc:** day 1 built the whole spine in 12 hours. Days 2–5 were audit, repair, the careers
lane, contacts, priority, and four bounded loops. **~18 real defects were found and fixed in
that window; roughly half were "built but never called."**

---

## THE NOTION SURFACE — what exists now

**Database `Norman CRM`**, 93 rows, 61 properties, **nine views** built 2026-08-10 by a separate
agent (Codex) driving the UI:

`CHANGED · PROSPECTS · TOP PURSUITS · NEW INTAKE · BY SIZE · HIRING · NEEDS ME · HEALTH · NYC BAND · HEALTH`

Four buttons (`Chase this`, `Not now`, `Not a fit`, `Called today`). **One integrity proof:
4,650 SHA-256 hashes, unchanged across the whole build.**

**The boundary, and it is absolute:**

> **Norman writes DATA. Codex configures PRESENTATION. Notion may display anything and decide
> nothing.**

Formulas and rollups are fine — recomputed on render, cannot drift. **Any automation that writes
a machine-owned property creates a second source of truth the reconcile loop cannot see.** There
is exactly one automation and it is disabled; there is no Slack, no email, no Gmail grant.

**Reconcile's laws, verbatim from the code:** *adopt before heal* · *heal machine columns only;
human fields are read to adopt them* · *every action is logged.*

---

## STANDING RULES THAT KEEP GETTING VIOLATED

**Read these as hard constraints, not advice. Each one has a defect behind it.**

1. **Verify the artifact, not the account of it.** A feature is proven by an observable it
   produces. **Every claim of "shipped" must name the number that proves it.**
2. **A unit test proves a function WORKS. It says nothing about whether anything CALLS it.**
   Four mechanisms shipped with green tests and no callers. **An export is not a call site.**
3. **Blank ≠ zero. Everywhere.** Unmeasured and measured-zero are different facts. A missing
   value must never sort, score, or display as a zero.
4. **Declared but inert.** A rule present in config, code or docs that cannot fire, reporting
   green. The dominant defect class in this project.
5. **A control that fails silently — or fails CLOSED — is worse than one that is absent**,
   because it converts "no protection" into false confidence.
6. **Any predicate existing in two layers must be defined once.**
7. **Scoring changes are gated: simulate → show JD the movers → apply → oracle → re-freeze.**
   **Report the rate AND one concrete company beside it** — that is what lets him decide in one
   pass.
8. **JD's LinkedIn is the highest-risk asset in the system.** UI-only, attended, his go per
   session, **halt on the first challenge with no retry.** Nothing in this loop touches it.

---

## HOW TO WORK WITH JD

**Plain language. No jargon.** If a message drifts technical he will say so. Lead with what it
means for him and what to do.

**He learns by example** — show a worked example or a real number before explaining the shape.

**He ranks rather than picks**, thinks in whole pictures, and reads every company against its
funding stage. **He wants a wide net with some noise: "I'd rather filter than miss a good one."**

**Genuine uncertainty goes to him as a question, never a silent guess.**

---

## THE WORK: LOOP 4

**The full spec is `outbox/GOAL-loop-4-fully-wired.md` in NormansBrain. Read it there, not from
this summary.**

**The framing:** JD is about to send a new CSV. **The test is not "fill in today's blanks" — it
is whether a company arriving TOMORROW gets every field without anyone remembering to run
something.**

**Five bands:** the four Notion writes · the thirteen empty fields decided one by one · the 173
contacts reaching the board · the 93-vs-133 store gap · **and the acceptance test — one
synthetic company followed end to end, with every board column sorted into populated,
blank-correctly, or blank-wrongly.**

**Three distinct reasons a cell is blank, and only one is a defect:**

| | |
|---|---|
| the data exists and the projection was never written | **a defect** |
| downstream of an empty input | arithmetic waiting — self-resolves |
| no evidence exists yet | honest, and correct as-is |

---

## LOOP DISCIPLINE

```
budget: 3 passes. Not 4.
each pass: run all bands → fix only what failed → re-run ALL bands
all green → stop.   after pass 3 with anything red → escalate. No fourth pass.
```

**Frozen scope: a defect you find that is NOT on the checklist gets RECORDED in
`docs/found-not-fixed.md`, not fixed.** Two exceptions only: **data loss**, or **risk to JD's
LinkedIn account.**

**One report at the end. Not one per finding.**

**Naming why a scope violation was tempting is part of resisting it** — every instance is small,
correct and obviously worth doing, **which is exactly why "is this worth doing?" cannot be the
test. The test is "is it on the list?"**

---

## STAYING OPEN AS JD GIVES FEEDBACK

**Frozen scope binds YOU, not him.**

> **JD changing the goal is legitimate and immediate. You finding new work is not.**

When he redirects: **stop, restate what you understand the new goal to be in one sentence, and
confirm before rebuilding around it.** He has twice said a design was overbuilt — both times the
cause was inferring requirements from evidence he never cited.

**An insight discovered while researching a request is not part of the request.** Report it, ask,
and do not fold it in.

**If something he asks for conflicts with a recorded ruling, say so plainly with the ruling ID
and let him decide.** He overrules rulings regularly and is usually right — the two-day-old
"companies outgrow their space quickly" correction reversed an entire design.

---

## FIRST THING TO DO

**Do not start building.** Read the material above, then report:

1. **What you understand Norman to be, in five sentences.**
2. **The three defects from the last five days you consider most instructive, and why.**
3. **Anything in loop 4 you think is wrong, missing, or mis-scoped** — before a line of code.
4. **What you could not verify**, and what it would take.

**That fourth item is not a formality.** The most valuable thing this project has produced is the
habit of separating what was checked from what was assumed.
