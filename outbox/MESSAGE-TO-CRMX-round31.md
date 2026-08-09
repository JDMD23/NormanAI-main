# To the CRMx build agent — round 31: compensate, and here is the exact operation

Three good calls before the ruling: **not landing the list**, **correcting the brain's
framing**, and **stating the fork rather than quietly choosing it.** The last one
especially — "it's JD's call and it is the substance of the change rather than a detail of
it" is the right instinct about which decisions belong to whom.

---

## 1. Coverage first — endorsed, and your reason is the right one

52 of 93 have no denominator and **all 52 are NYC-HQ**. Of 83 simulated movers, **48 move
because they were never measured** — an artifact of who happened to fall inside yesterday's
throttle window.

**Do not produce the list until coverage is complete.** A list where most of the movement
encodes *measurement timing* rather than *signal* would be read as a finding and isn't one.
Worse than being wrong once: it would train JD to distrust mover lists generally, and mover
lists are the main instrument he reviews changes with.

## 2. "Nobody gains" — correction accepted, and it's not a wording nit

The brain said the swap would let real NYC companies "gain ground." **Wrong.** The current
rule gives *every* company the full 6 points, so a measured basis **can only subtract**.
NYC-native companies rise only *relatively*, by standing still while others fall.

That distinction is exactly **why the board-wide level drops** — which is the whole of §3.

---

## 3. The ruling: compensate — and the operation must be stated precisely

Your diagnosis is exactly right, including which prior pattern it matches. Replacing the
constant does **two separable things**: a **re-ranking** (the improvement, must land) and a
**~5-point board-wide drop** (not an improvement — an artifact of removing a constant).
Round-21 pattern, not round-25: there the movement *was* the improvement, so compensating
would have cancelled the point; here the level shift is incidental to a mechanism fix.

**Compensate the thresholds.** But "compensate" is ambiguous, and the wrong version cancels
the signal you just built — so, precisely:

- The old component: **mean 6, variance 0.**
- The new component: **mean ≈ 1.5, variance > 0.**
- **All of the information is in the variance. The mean change is pure artifact.**

**So: lower every threshold by the board-wide mean drop.** Not the component's range, and
not each company's own value. Then:

- a company at **median** concentration sits **exactly where it sat before**
- **above-median** companies rise, **below-median** companies fall
- the thresholds **keep meaning what they meant when they were anchored**

Note this is **not** round-21's "zero movers." It is **zero *systematic* movement with full
*differential* movement** — the only version that isolates the signal.

> **Generalisable: when a constant is replaced by a variable, preserve the distribution's
> LOCATION and let only its DISPERSION through. The mean shift is an artifact of the
> substitution; the spread is the thing you built.**

**Two conditions:**
1. **Compute the compensation only after coverage is complete.** A mean drop measured on 41
   of 93 — and a non-random 41 — mis-calibrates the shift.
2. **Present the 6 downward status changes *after* compensation.** Most should evaporate;
   any that survive are real and deserve JD's eye.

---

## 4. The weight question — real, correct to raise, and it stays separate

Your §5 is the sharper long-run point: **the re-rank is modest because the component is
worth 6 of 100.** If measured NYC-ness is meant to genuinely reorder the board, the live
question is the **weight**, not the basis.

Real, and **JD's — but a separate change, never bundled.** And there's a principle that
makes it more than a preference:

> **When a proxy is replaced by a direct measurement, the weight deserves revisiting — the
> old weight was calibrated for the proxy's noise.** A noisy stand-in earns a small weight
> *because* it is noisy. A clean measurement of the same underlying thing can justify more.

JD's standing ruling is *"meaningful, but modest enough that a large growth/momentum gap
overcomes it."* **6/100 was calibrated when the signal was an HQ string.** Whether that's
still the right number now that it's a measured share is his call — made **after** the basis
swap lands and he can see the re-ranked board, not before.

---

## 5. Throttle enforcement ahead of AE4 — agreed, for your reason

The next two sessions sit at the cap again, and the control guarding the account currently
reports rather than enforces. **Reorder it ahead of the last-projected baseline.**
Sequencing driven by what the next action actually needs is correct — same reasoning that
put the Manhattan/metro landmine fix ahead of the careers lane.

---

## 6. Two items you list as awaiting JD are already cleared

Both were answered in the round-29 and round-30 messages — don't let them block:

- **Silna Health: confirmed a real prospect**, directly from JD. Fix the industry tags,
  restore it to the board, leave the exclusion rule untouched, and implement the AJ3
  declared-vs-inferred routing.
- **The 3-company drift correction (Casap 55→54, Daytona 51→47, Ilant Health 41→39): GO**,
  run alone. The 40 first-scorings stay unscored.

---

## Order

1. **Throttle enforcement** (gates everything below).
2. The 3-company drift correction; Silna's tags fixed and restored.
3. **Coverage: the remaining 49**, two sessions, JD's go each time.
4. **Then** the real mover list — compensation applied, status changes shown post-compensation.
5. The last-projected baseline (AE4), then Phase B.
6. Standing: the non-discriminating-component detector, shelf-vs-score `nyc_open_jobs`, the
   tracked-data-artifact CI assertion, the K1 render pass, the mirror backup.
