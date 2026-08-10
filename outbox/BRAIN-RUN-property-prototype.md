# Property-set prototype — run against `6d54b06`, and it found one immediately

Not built into the repo. **Prototyped and executed** against the committed scorer, no live data.
Two of the five properties are runnable without a database; both ran.

---

## PROPERTY 1 — is every scoring component reachable by SOME input?

Stronger than *"is it present on today's board"*: **does an input exist that makes it fire at
all?**

```
employees  jobs  growth  industry  funding  investors  stage_fit  hq
  FIRES    FIRES  FIRES    FIRES     FIRES     FIRES      FIRES   FIRES
```

**All eight reachable.** No structurally dead component. Green.

---

## PROPERTY 2 — does each component CHANGE the score when its input changes?

```
employees   79 -> 54   moves
jobs        79 -> 62   moves
growth      79 -> 79   NO EFFECT
industry    79 -> 76   moves
funding     79 -> 74   moves
investors   79 -> 78   moves
stage_fit   79 -> 72   moves
hq          79 -> 73   moves
```

### The mechanism, isolated

```
growth weight            10
fresh_raise_growth_pts   14        ← the floor EXCEEDS the ceiling it feeds
```

```python
pts = VELOCITY_POINTS[velocity]
if fresh_raise:  pts = max(pts, 14)      # floor
pts = min(pts * scale, 10)               # ceiling
```

**14 > 10, so any company with a big fresh raise clamps to the full weight regardless of
velocity.** Measured:

```
BIG FRESH RAISE ($25M, 60d)   Fast 79  Normal 79  Slow 79    spread 0
old round ($25M, 900d)        Fast 74  Normal 71  Slow 69    spread 5
```

> **For every recently well-funded company, funding velocity is non-discriminating.** The
> fastest-compounding and the slowest score identically on growth — and recently well-funded is
> exactly the population JD is chasing.

**A unit test on the growth function passes.** The function is correct. **The defect is in the
relationship between two constants in a config file**, and nothing owns relationships.

### And boot validation catches this class — just not this instance

`formula_is_coherent` and `hysteresis_is_coherent` already exist, and the config **correctly
refused to load** in round 44 when `demote_below` fell below `no_growth_signal_cap`. That was
two constants in the wrong relative order and it was caught.

**This is the same class and is not checked.**

> **A floor that can exceed the ceiling it feeds erases the signal beneath it.** Every "at least
> X" bonus must be validated against the maximum of the thing it floors — as a boot check, beside
> the coherence rules that already exist.

---

## What this says about the loop-3 spec

**The property set earns its place — it found this in one run, with no live data, in minutes.**

**And it sharpens A1.** "Every scoring component has a real value for ≥1 company" would have
passed here: growth *had* a value. **The property that caught it is the second one — does the
component's input actually move the output.** Presence is not discrimination, and the board has
now produced two instances of that distinction (`hq_city` awarding 6 to everyone, and this).

**Add to A1's list:** *for every component, an input exists that changes its contribution* —
distinct from *the component produces a value*.

---

## Not run

Three properties need the live board: every column ≥1 non-null · no field constant across rows ·
stale-rule-version count. **Those are yours.** The reachability property I ran separately at
round 53.
