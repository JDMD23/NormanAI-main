# To the CRMx build agent — round 30: the ruler is validated. Now kill the HQ component.

That is a proper instrument validation, and it delivered more than was asked for. Two
separate properties, separately demonstrated:

- **Unbiased** — NYC-native controls at 53–79% concentration (GovWell 50/63, Hanover Park
  50/67, Marble 84/120, Manifest OS 64/94). **An instrument that systematically lost NYC
  people cannot produce those numbers.**
- **Stable** — 39 of 41 reproduced exactly on re-measure; the two movers inside the
  already-calibrated ±1.

**The undercount thread is closed.** The low counts are true, the 21 thin companies are
genuinely thin, and **the 16 shelved companies are correctly shelved.**

---

## 1. The finding: `hq_city` is a constant, so the HQ component discriminates nothing

All 41 carry `hq_city = "New York"` — that's how they entered the board — while measured
concentration runs **0% to 79%.**

So **every company on the board receives the NYC-HQ points.** A component that awards the
same value to everyone is **a constant offset, not a signal.** It consumes weight and
contributes **zero discrimination.**

**This is the "declared but inert" family surfacing in the scoring layer** — configured,
tested, running, and informationally empty. And worse than empty: it was awarding
*NYC-native credit* to companies that are **0% NYC**, which is the exact inverse of its
intent, on a signal JD explicitly ruled should carry real weight.

**Ruling: replace the HQ proxy with measured NYC concentration.** This is the two-for-one
from AH3, now realised, and it's strictly better evidence — a *measured share* versus a
*registered-address string*.

**Gated change** (it moves companies in both directions): simulate → show JD the movers →
apply → oracle → re-freeze.

**And add the general detector, because it's cheap:** flag any scoring component whose value
is **identical across the whole board** as non-discriminating. That would have caught this
without a measurement session, and it will catch the next one.

---

## 2. On the brain's own correction — your honesty is the right call

The company-page number and the geo-dropped Sales Nav total agree **within 1–3% on 38 of
41.** Saying that plainly, rather than letting the correction look more consequential than
it was, is worth more than the correction.

**The principle stands and the definition stays** — same-query sameness is free to keep and
still the right default. But record the honest magnitude: **this was a correctness
improvement, not a rescue.**

Two notes worth keeping: the measured agreement is itself a **useful calibration result**;
and it's a result about *this* population — it may not hold for very large companies or ones
with heavy alumni tails, which is precisely why the principle remains the reason to prefer
the geo-dropped definition even where the two agree.

---

## 3. The throttle reports but does not enforce — and this one guards the account

82 views against a documented cap of 80. **2.5% over is harmless. The mechanism failure is
not.**

The tripwire is read at session start and printed; nothing decrements during a run, so it
**announced the breach after it happened.** There is no enforcement — so a bug or a longer
run could reach 200 and nothing would stop it.

You correctly identified the shape ("the throttle reports, it does not enforce"). What makes
this the **most consequential instance** of that shape: it is the **account-risk control**,
and L1/L2 explicitly traded static quotas for dynamic monitoring.

> **A monitor that cannot stop the thing it monitors is not the safety that trade assumed.**

**Ruling: the code making the calls checks and decrements per call, and the run halts itself
at the cap.** Not a session-start reading, not a post-hoc report. **And this is now a
prerequisite for unattended operation (L2)** — an unattended lane with a reporting-only
throttle has no ceiling at all.

---

## 4. The Israeli-cluster hypothesis — right to flag it untested, and reframe what it means

**For scoring it changes nothing.** Concentration already routes those companies correctly,
so confirming the cause satisfies curiosity without changing an action. Per scope honesty,
don't spend the lookups.

**Where it matters is discovery.** If a systematic share of Crunchbase-NYC-sourced companies
have a NYC *registered address* and no NYC *presence*, then **the intake filter is importing
non-prospects** — the source search is selecting on the same broken field §1 just condemned.

Park it as a **discovery-lane question**: the NYC sourcing filter may need a presence-based
criterion rather than a registered-address one. Not a scoring question.

---

## 5. JD's two outstanding items — both cleared

- **Silna Health: confirmed a real prospect**, directly from JD. Correct its industry tags,
  restore it to the board, **leave the exclusion rule untouched**, and implement the AJ3
  declared-vs-inferred routing so the next stray tag routes to review rather than exiling.
- **The 3-company drift correction (Casap 55→54, Daytona 51→47, Ilant Health 41→39): GO**,
  run alone. The 40 first-scorings stay unscored.

---

## Order

1. The 3-company drift correction; Silna's tags fixed and restored.
2. **Throttle enforcement** — it gates tomorrow's remaining 49 companies, and it's the
   account control.
3. **The last-projected baseline (AE4)** — still before Phase B wiring.
4. **The HQ → concentration swap**, gated and simulated.
5. Phase B, head-noun rule and subject-vs-role pairs.
6. Standing: the non-discriminating-component detector, shelf-vs-score `nyc_open_jobs`, the
   tracked-data-artifact CI assertion, the K1 render pass, the mirror backup.
