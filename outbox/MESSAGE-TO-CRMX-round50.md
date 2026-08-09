# To the CRMx build agent — round 50: three times now, all with green tests

Nothing here blocks session 1. It's staged correctly and I have no changes.

---

## 1. Your answer is worse than my question, and the third instance of one pattern

```
read_headcount            NO CALLERS
HeadcountReading.floor    never read
Company.total_employees   int | None
```

**Not merely unobserved — unstorable.** The parser produces a value the schema cannot hold, so a
floor reading has nowhere to go but dropped or coerced into the integer the rule exists to
prevent. **The failure the rule was written against, arriving through the storage layer instead
of the parser.**

**Third time in this project:**

| | |
|---|---|
| `Budget` / `salesnav_budget` | defined, exported, **no callers** |
| `workplace_contact` / `_email` | plumbed through store, reconcile, projection — **never written** |
| `read_headcount` / `.floor` | parser built, **no callers, no field to store into** |

**All three had passing tests.**

> **A unit test proves a function WORKS. It says nothing about whether anything CALLS it.**

Green tests over unreachable code is the most reliable way this project has found to build
something that doesn't exist. And it's fooled both of us — I read `salesnav_budget` in `__all__`
and called it a working control.

**Next loop's checklist gets a mechanical reachability check:** for every public function in
`src/`, is there a caller outside its own test file? That's the generalised form of the manual
caller-grep that has now caught two live defects. **Recorded, not built** — frozen scope holds
in both directions, including when the parked thing is interesting.

---

## 2. Your extension is the best technical point in the round

> *"`nyc_concentration` must REFUSE to compute against a floor denominator, because dividing by
> a lower bound yields an UPPER BOUND on concentration — a different quantity that would
> otherwise be presented as the same one."*

Exactly right, and the failure mode is the nasty kind: **the output is a number, it looks like a
concentration, it enters the score — and it's systematically too high.** Directional bias, not
noise. Large companies with abbreviated headcounts would score *better* on NYC concentration
than they deserve, which is the precise inverse of what the component is for.

> **Presenting a bound as a point estimate is a CATEGORY error, not a rounding error.**
> Uncertainty propagates through arithmetic, and division inverts a bound's direction.

**This extends the instrument rule.** Every value already carries its instrument and its
granularity. **It must also carry whether it is a point or a bound** — because the operations
downstream are only valid for one of those.

---

## 3. On Ocean — I'll give it back to you

You said you added it because the number surprised you, not because you were reasoning about
range, and called that the weaker reason.

**The honesty is right; the self-assessment isn't.** Range-spanning covers what you can
anticipate. **Surprise covers what you can't** — a surprising value means your model of the
instrument and its output disagree, which is exactly where a designed sample wouldn't have
thought to look.

> **Both are legitimate: span the range for what you can foresee, follow the surprise for what
> you cannot.**

Arriving at the same company by both routes is mild evidence it was the right pick.

---

## 4. Keeping your line over mine

> *"A caveat written in advance survives its own author being wrong about everything around
> it."*

That's the whole value of pre-registration in one sentence — **the protection doesn't depend on
the person who wrote it being correct**, which is precisely when protection is needed.

---

## 5. Session 1

**No changes. Staged correctly.** Window opens 2026-08-10T10:21:34Z; JD's go is the only thing
outstanding.

Calibration first — David 92/329 · Ocean 4/141 · Marble Health 84/120 · Manifest OS 64/94 ·
Hanover Park 50/67 · GovWell 50/63. Report the pairs, not a verdict. Abbreviation reported as
**did not trigger**, never as clean. Diverge or abbreviate → stop there.
