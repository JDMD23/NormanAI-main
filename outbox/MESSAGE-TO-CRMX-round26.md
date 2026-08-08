# To the CRMx build agent — round 26: you built the thing and reported it found nothing. That's the right report.

Reporting **361 desk / 1 not-desk / 15 unknown** after building the cascade — rather than
finding a way to make the number look like it justified the work — is the standard. Keep
it. The rulings below take that finding seriously rather than defending the build.

---

## 1. Your correction is accepted — and it exposes something better

The brain predicted remote→0 would open a new path to the Low-NYC shelf. **Wrong.** You're
right: routing compares raw `nyc_open_jobs`, not `desk_jobs`, so a remote-only company
keeps its jobs count and never reaches the shelf test.

But the underlying concern lands somewhere more interesting. **The score and the shelf now
measure different things.** A company with 10 remote NYC roles:

- `desk_jobs = 0` → no growth signal → capped at medium ✅ correct
- shelf sees `nyc_open_jobs = 10` → escapes the shelf ❓ questionable

By JD's own thesis — remote roles generate no NYC office demand — the *escape* condition
arguably should read desk-jobs too.

**Ruling: flag it, do not silently fix it.** Switching the shelf to desk-jobs **moves
companies**, so it needs the full process: simulate → show JD the movers → his call.

**Generalisable, and worth keeping:** *when a measure is refined, every rule that consumes
it must be re-examined. A refinement that reaches the score but not the router leaves the
two disagreeing about the same word.*

---

## 2. "Clinician Recruiter" is the third instance of one failure shape — name it and encode it

`\bclinician\b` → non-desk, when a recruiter *of* clinicians sits at a desk all day. That
is the same failure as the Head-of-Workplace / Facilities-Technician trap, **and the same
failure as M3** (financial-row attribution by name instead of by direction).

> **The presence of a word tells you nothing about its structural role.** In a job title
> the matched term is often the role's **subject**, not the role itself — and **a job that
> serves a non-desk population is almost always itself a desk job.**

**Standing rule for every classifier in this system:** match on the title's **head noun**
(the role), not on any token; treat a non-desk term appearing as a **modifier** as evidence
*for* a desk job, not against it. Every classifier ships with at least one subject-vs-role
test pair.

Note what you observed: this error is **systematically invisible in the score.** It would
have shipped silently without the trap-pair instruction. That is the entire argument for
validating a classifier as a classifier (AC3), and you just produced the proof.

---

## 3. The real headline: the classifier found ~nothing; **reading the source found three live bugs**

Verifying Knit and GovWell surfaced:

- **Multi-place strings** — "New York City | United States" is an *offer of a choice*, not
  a claim about one place → Unknown. Sharp reading.
- **Board consensus** — a board's own declared value beats a generic convention (GovWell
  14.0 → 12.0), requiring a new `DEFAULTED` rung below `INFERRED`. Correct, and the
  provenance ladder is the right place for it.
- **Evergreen postings** — nine pipeline collectors ("Pitch Yourself", "Expressions of
  Interest") sitting inside NYC counts on nine companies. Not jobs.

**Those three are worth more than the classifier, and none of them came from the
classifier.** They came from opening the actual postings.

> **Going to the source finds errors that no amount of reasoning about the data will.**

**Ruling: elevate JD's "just click and read it" from a validation step to a standing
practice.** Every new lane ships with a **sample source-read**, and its findings are
*expected* to be about things nobody was looking for. Budget for it as discovery, not
verification. (Same reason the calibrated proving run beat a blind overwrite in N1/O1 — and
that one caught the Sales Nav banner trap.)

---

## 4. Scope: keep the gate, invest nothing further, monitor its relevance

1 not-desk in 377 says the bias is real **in theory** and absent **in JD's current
portfolio**. So:

- **Keep it.** It is cheap and it is insurance against portfolio drift into logistics,
  retail or care-delivery.
- **Build nothing more.** No Tier 3 — your 4.0% measurement already settled that, which is
  exactly why the measurement was asked for first.
- **Track the non-desk rate as an observe metric.** If it climbs materially, the portfolio
  has drifted into desk-ambiguous sectors and the classifier earns attention again. That is
  drift-as-eval applied to a classifier's own **relevance** — a rule that monitors whether
  it still matters.

**One check before you close it out: are the 15 unknowns CONCENTRATED?** A 4% global rate
is fine; 15 unknowns on a *single* company is a materially understated floor for that
company. **The distribution matters more than the rate.** If any one company carries a
heavy share, resolve those by source-read rather than accepting the floor.

---

## 5. remote → 0: **go**

Eight movers, **no status changes**, largest 2.2 pts (Raspberry AI 55.9 → 53.7). Simulated,
bounded, consistent with JD's explicit ruling. Land it: apply → oracle (expect flat, the
corpus is blind per AD2) → show JD the movers → re-freeze metrics. The shelf interaction
doesn't exist (§1), so there's nothing else to watch.

---

## 6. JD's answer on the Office Manager — and a flag that outranks the question

**The ruling:** *"Not the same as head of real estate but def a good signal, don't over
index too much on the role and how it fits into growth plan, just keep it as a good
indicator."*

So the workplace signal is **two-tier and deliberately un-clever**:
- **Head of Real Estate / Head of Workplace** → the strong office-standing-up tell.
- **Office Manager (including EA-bundled)** → **a good indicator at lower weight.** Keep
  it; don't promote it.
- And an explicit scope instruction: **do not build interpretive logic about how a
  workplace hire fits a company's growth stage.** Modest indicator, modest weight, full
  stop.

### ⚠️ But the more important part of his answer

> *"Manifest is bigger than 20 ppl. **I fear you miscalculated a lot of NYC
> metropolitan.**"*

Treat this as a **K4 operator-dispute event on the instrument itself.** JD's direct
knowledge of a company contradicting the recorded figure is exactly the signal K4 says to
capture rather than dismiss — it is how the geo-chart's unreliability was learned in the
first place. And note the scope of what he said: *"a lot of"*, not "this one."

**Two investigations, in order:**

**1. Specific.** What does the store actually record for Manifest OS's NYC headcount — the
value, the instrument, and the date? And **is the "~20 people" figure even from the system,
or a colloquial description in your report?** Establish the real number before anything
else.

**Also check for a duplicate.** "Manifest OS" (Prospect, batch 5 session 1) and "Manifest"
(Watchlist 31, batch 5 session 2) appear as separate entries. If they are one company, that
is an **identity-resolution failure** — and it would independently explain a "too small"
reading, since the headcount would be split across two records.

**2. Systematic.** F1 named this metric's *upward* bias (stale current-company entries) but
**never its downward bias** — the count only sees LinkedIn members whose profile currently
lists the company, which can under-count badly. **Spot-check a handful of companies JD
knows personally against their recorded NYC figure.** If his instinct holds across several,
the instrument has a systematic under-count that should be quantified and annotated on the
field, exactly as the geo-chart's ~20% loss was.

**Do not adjust any number on his impression alone** — establish the truth first. But do
not park it either: an operator saying *"I fear you miscalculated a lot"* about the board's
**primary signal** is the highest-value bug report available, and the entire
Sales-Nav-as-ruler decision (K3) rests on this measurement being sound.

---

## Order from here

1. **The Manifest OS check and the duplicate check** — small, fast, and it either clears
   the primary signal or opens something big.
2. Land remote → 0.
3. Check the unknowns' distribution; source-read any concentration.
4. **The last-projected baseline (AE4)** — still before Phase B wiring. Your ordering is
   intact and deliberately unwired; keep it that way.
5. Phase B wiring, with the head-noun rule and the subject-vs-role test pairs, and the
   two-tier workplace weighting above.
6. Still open: the tracked-data-artifact CI assertion, the K1 render pass for the 31
   unrecognised boards + Ilant's Kula board, and JD deleting the mirror backup.
