# The funnel: one field is carrying five different questions

**A proposal for JD, not a spec for the build.** Grounded in `brain/10-workflow-and-decision-systems.md`,
which is the document this question was already answered by.

---

## THE DIAGNOSIS

Your 14 statuses, sorted by what they actually answer:

| axis | current values |
|---|---|
| **Where in the funnel** | Research · Prospect · Top Pursuit · Engaged · Active TIM · Client/Dealflow |
| **Why it's out** | Not a Fit · Low NYC Presence · Do Not Pursue |
| **How cold** | Tracking · Watchlist |
| **What's blocking** | Needs Review · Needs Angle |
| **A timing event** | Recently Signed Lease |

**Five orthogonal questions in one select field.** Which forces false choices:

- A company that is a **Prospect** *and* **needs review** has to pick one — and the operational
  state overwrites the funnel stage, so it silently leaves your chase list.
- **Low NYC Presence** is a *reason for disqualification*, not a place in the funnel.
- **Recently Signed Lease** is an *event with an expiry*. A company that signed in 2026 on a
  5-year term is a prospect again in **2030** — and nothing brings it back.

> **`brain/10 #7`: operational outcomes are a separate vocabulary from entity state.** The views
> feel hard to design because you are trying to filter one field on five different questions.

---

## THE STRUCTURE — four fields, and only one of them is new

| axis | field | values | who sets it |
|---|---|---|---|
| **Stage** | `Status` | Research → Tracking → Prospect → Top Pursuit → Engaged → Active TIM → Client | machine proposes; JD confirms the consequential ones |
| **Disposition** | `Disposition` *(new)* | *blank* · Not a Fit · Low NYC · Do Not Pursue · **Signed — revisit YYYY-MM** | JD, or machine with a reason code |
| **Blocked on** | `Action Needed` *(exists)* | `Joe: …` / `Norman: …` | machine |
| **Attention tier** | *derived, never typed* | hot · warm · cold · frozen | computed from stage + fit |

**Stage becomes a real state machine** — ordered, total, one axis, every transition with an owner
and a trigger (`brain/10 #1`). Nothing else lives in it.

**Disposition is blank for everything in play.** That is the whole trick: *out* is a separate
field, so a disqualification never destroys the funnel position it had.

> **CORRECTION (JD's ruling): `Recently Signed Lease` is NOT a disposition. It stays a live
> stage — companies outgrow their space quickly.** See the section at the end; the revisit
> trigger is **growth, not time**, and this changes the design.

**Attention tier is derived and never hand-set** — `brain/10 #9`: *"attention is a budget; make
cadence a function of tier and freshness."* Watchlist was never a stage; it was a cadence.

---

## THE VIEWS FALL OUT OF IT — each answers ONE question on ONE axis

1. **Chase list** — `Stage ∈ {Prospect, Top Pursuit}` ∧ `Disposition` blank, sorted by Fit Raw.
2. **My queue** — `Action Needed` starts with `Joe:`. Empties. Already your best view.
3. **What moved** — change origin = *company*, not *system*.
4. **Coming back** — `Disposition = Signed` ∧ revisit date within 6 months.
5. **Pipeline flow** — see below.

**View 4 does not exist today and is the one that pays for itself.** Every lease you lose on
timing is a company that should reappear automatically at the right moment. Right now "Recently
Signed Lease" is a dead end.

---

## THE THING YOU ASKED FOR AND DON'T HAVE: FLOW, NOT STOCK

> **Every view you have shows what IS. None shows what MOVED.**

A funnel is monitored by **flow** — how many entered and left each stage this week — not by how
many are sitting in each bucket. Stock tells you the shape; **flow tells you whether the machine
is working.**

```
                    this wk   last wk
  → Research           12         8      inflow
  Research → Tracking   4         6
  Tracking → Prospect   3         2
  Prospect → Top        1         0      ← the number that matters
  → disqualified        5         3      outflow, by reason
```

**That single table answers "are the ins and outs healthy":** inflow drying up, a stage where
nothing ever leaves, disqualifications spiking on one reason. **You already store the change log
this is computed from.**

> **`brain/10 #11`: score change and state change are different truths — surface both.** The flow
> table is the state truth; the mover list is the score truth. **You have the second and not the
> first.**

---

## WHAT KEEPS IT FROM BEING OVERDONE

- **Four fields, one of them new, one of them derived.** Not a redesign.
- **Five views, and you already have three.**
- **`brain/10 #2` — hysteresis, which you already have.** Asymmetric enter/exit thresholds so a
  score wobbling 59↔60 doesn't thrash a company between stages and spam the moved view. **This is
  what stops the structure from generating noise**, and it is already built.
- **No new scoring.** Fit Score is untouched; this is only about where a company sits and what
  you see.

---

## THE HONEST ANSWER TO "IS THERE A REPO FOR THIS"

**No, and the two closest are already in your studies:**

- **`studies/controller-runtime.md`** — desired state vs actual, level-triggered convergence.
  Your stage machine decides *what* the state should be; the reconciler makes the world match.
- **`studies/temporal.md`** — the workflow/activity split: orchestration logic separate from side
  effects.

**Neither is about funnels.** The funnel knowledge is `brain/10`, and it was written from those
studies precisely so you would not have to go back to them. **What has never happened is anyone
applying it to your status vocabulary** — which was designed on day 1, before most of `brain/10`
landed.

---

# CORRECTION — JD: keep Recently Signed Lease, because companies outgrow their space quickly

**He is right and it breaks the model I proposed.** I treated a signed lease as a parked state
with a revisit date at lease expiry. **That is the wrong clock.**

> **The revisit trigger is GROWTH, not TIME.** A company that signed 8 months ago and has doubled
> its NYC headcount is out of room *now*. A company that signed 4 years ago and hasn't grown is
> not a prospect just because the term is ending.

## Why this is the strongest prospect type on the board, not a parked one

A recently-signed company has **proven it transacts** — it has a budget, a decision process, and
a signature. Everything else on the board is a hypothesis about whether they will ever move.
**These are the only companies where that question is already answered.**

So: **`Recently Signed Lease` stays a stage, and it gets its own clock.**

## What it needs, and the data does not exist today

Verified: `Company` has **no lease fields at all** — no signed date, no square footage, no
headcount at signing. `nyc_office_verified` is the closest and it is a boolean.

**Three fields, and only the third is hard:**

| field | why |
|---|---|
| `lease_signed_on` | the baseline date |
| `lease_rsf` | square feet, where known |
| **`nyc_heads_at_signing`** | **the baseline that makes outgrowth computable** |

**Without a headcount baseline there is no outgrowth signal** — only a current number with
nothing to compare it to. This is the denominator problem again (AH2), in a new place.

## The signal, and it uses a number already in JD's profile

`brain/jd-operator-profile.md` records **170 RSF per employee** — captured months ago and never
scored. **This is where it earns its place:**

```
capacity      = lease_rsf / 170
utilisation   = nyc_employees_now / capacity
```

**Above ~85% they are out of room.** And where RSF is unknown, the cruder form still works:

```
growth since signing = nyc_employees_now / nyc_heads_at_signing
```

**Doubled since signing means out of room regardless of what they signed for.**

## Why this is cheap to build

**Norman already measures NYC headcount on a cadence.** The numerator is flowing today. The only
new data is the baseline at signing — three fields, entered once per company, by JD, at the
moment he learns of the lease.

> **One new view: "Outgrowing" — `Stage = Recently Signed Lease`, sorted by utilisation
> descending.** That is a call list of companies who have already proved they will sign and are
> now running out of room.

## What I got wrong, stated plainly

I assumed the trigger was the lease **term**, because that is how a parked record thinks. **JD's
model is that the trigger is the company's own growth against the space it bought** — which is
the same signal Norman already exists to measure, pointed at a population that has already
demonstrated it transacts.

> **When a state looks like it should be parked, ask what would bring it back. If the answer is
> a date, it is a disposition. If the answer is a measurement you already take, it is a stage.**
