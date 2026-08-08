# To the CRMx build agent — round 21: purge verified independently, and the sequencing ruling

## 1. Purge — independently verified, clean

Verified the way you asked for it: a **fresh `git clone` of the remote**, then scanning
that clone's own object graph — not your local copy, not my existing checkout.

```
HEAD:                     776badb
commits:                  59
db/sqlite/bak objects:    0   (across all refs: main, phase-0, origin/HEAD)
data/norman.db.bak-round9              -> 0 commits
data/norman.db.bak-status-migration    -> 0 commits
data/norman.db-shm                     -> 0 commits
```

And the decisive check — the two blob SHAs the brain identified back in round 18:

```
dacf657434cb68deb78aa279ba5cca9235270a87   GONE
5be742497df72e0dfbd952338727a475277f36b8   GONE
```

**Confirmed clean.** ADR 0013 is the right artifact, and the part that generalizes beyond
this incident is the root cause stated plainly: *a .gitignore extension glob is not a
control.* Keep the tracked-data-artifact CI assertion on the list — as you noted, a
credential scanner skips binaries, so it is a genuinely separate check.

---

## 2. The sequencing ruling: **do it now — the dilemma is false**

You framed it as: switch now (re-anchor and re-freeze twice, doubling the label-fitting
circularity) versus bundle with the careers lane (and let a known-imperfect mechanism keep
deciding live bands — "which is how inert rules are born"). Both horns are real **if the
switch requires re-anchoring. It doesn't.**

### A mechanism change and a value change are separable

Switch routing to `raw` **and simultaneously set each threshold to its current effective
value** — `enter_prospect: 49.5`, and likewise down the ladder. The comparisons
`round(raw) >= 50` and `raw >= 49.5` select the same companies. Therefore:

- **Zero companies move.** Haast stays in Tracking. Brandlight stays in Prospect.
- **No re-anchoring** — the ladder is never re-fitted to JD's labels, so the circularity
  is not re-incurred. Not once, not twice.
- **No re-freeze** — the frozen baseline still holds, untouched.
- **The gate passes.** And this is the elegant part: **the armed gate becomes the proof
  that the refactor was behavior-preserving.** If it fails, the change wasn't neutral and
  you find out immediately, before it lands. You have a gate that just correctly failed a
  real change — this is exactly the instrument to lean on.

Afterwards the mechanism is explicit and correct permanently, and **any future threshold
decision becomes a clean, separate, deliberate choice on the raw scale** — not entangled
with a rounding artifact.

**The general rule, worth carrying:** when a mechanism is wrong but its *current effect*
is acceptable, change the mechanism at zero behavioral cost by compensating the values,
then decide the values separately. **Never bundle "fix how it works" with "change what it
does"** — you lose the ability to attribute either outcome.

### And a second, independent reason not to bundle: attribution

The rounding switch is a **small, known, fully-simulated** change — you have already
enumerated its exact effect. The careers lane is a **large, unknown** one: seven dormant
signals switching on across ~95 companies. **Bundling a small known change with a large
unknown one destroys attribution** — when the post-lane oracle result looks odd, you will
not be able to tell which change caused it. This project has been disciplined about
precisely this (the calibrated instrument migration, the proving-run pattern rather than a
blind overwrite). Same discipline applies here. Land the known-neutral refactor, confirm
green, then let the lane be measured against a clean, unchanged baseline.

---

## 3. Why "document and defer" is no longer available

Verified: `score = round(raw_pct)`, and Python's `round()` is **banker's rounding** — ties
go to even. So the effective offset is **not a constant −0.5; it alternates with the
parity of the configured threshold**:

| threshold | parity | `.5` boundary | effective |
|---|---|---|---|
| `enter_prospect: 50` | even | rounds **up**, included | `T − 0.5`, inclusive |
| `enter_tracking: 42` | even | rounds **up**, included | `T − 0.5`, inclusive |
| `demote_below: 47` | odd | rounds **down**, excluded | just *above* `T − 0.5` |
| `tracking_floor: 39` | odd | rounds **down**, excluded | just *above* `T − 0.5` |

So the interim `thresholds_note` — *"each threshold's EFFECTIVE value is configured −
0.5"* — is approximately right and precisely wrong, and the direction of the error depends
on whether the number happens to be even or odd.

That matters more than the arithmetic: **you cannot accurately document a rule whose
behavior alternates with parity — you can only fix it.** And because the note is now
pinned by `TestRoutingRoundsByDesign`, the *wrong* description is currently locked in
until changed. Pinning was the right instinct; it just pinned a description that isn't
true.

---

## 4. The ruling, stated plainly

**Switch to raw routing now, compensating each threshold to preserve current behavior.
Confirm the gate passes (that is the proof of neutrality). Then proceed to the careers
lane against an unchanged baseline.**

Then: batch 5 session 2 (19 Sales Navigator headcounts), and the careers lane — four ATS
parsers behind the adapter interface with per-provider contract tests, capturing job
location-type and posting dates to switch on the dormant rules, two-phase (browser binds
once, API counts on cadence), applying K1 and O1. Expect scores to move when those signals
come online; re-run the oracle, review the delta with JD, and re-freeze then — once, for
a change that actually changes something.
