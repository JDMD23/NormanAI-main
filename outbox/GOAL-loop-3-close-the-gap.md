# GOAL: shorten the distance between introducing a bug and meeting it

**To the CRMx build agent.** Loop 3. **The checklist is frozen and you may not edit it.**

**This is not a bug-fixing loop.** Eighteen real defects in a week; ten of them shared one root
and none was caught by 548 passing tests. The target is the *root*, not the eighteen.

---

## THE DIAGNOSIS, FROM THE EVIDENCE

| class | count | examples |
|---|---|---|
| **Built but never connected** | 6 | throttle `Budget` · `velocity` · `changes_tags` · `workplace_contact` · `read_headcount` · `status_owner` |
| **Code right, data doesn't match it** | 4 | `hq_city` constant · `funding_stage` constant · 10 stale velocity rows · the config that said the opposite of the run |
| Logic errors | 6 | J1 inversion · dead eval gate · AE4 ×2 · duplicate-contact key · the migration |
| Display re-deciding settled things | 2 | alphabetical "best contact" · `Joe:` vs `Joe says:` |

**Every one of the first six had passing tests. Every one of the second four had correct code.**

> **A unit test is a contract on a function. It says nothing about whether that function is in
> the graph.** 200 public functions, 548 unit tests, **zero assertions on the artifact the system
> actually produces.**

---

## THE ONE IDEA — and it collapses three of the four fixes into one build

> **`studies/evidently.md`: "The same metrics run as a one-off `Report` (during development /
> calibration) and as a scheduled monitoring job (in production)."**

**Write the properties ONCE. Run them in three contexts.** Do not build a system test *and* a
detector *and* a monitor — that is three implementations of one idea, and they will drift apart
exactly the way `status_owner` and `HUMAN_OWNED` did.

```
   ONE property set
        ├── against a fixture, inside `make check`        ← catches it at commit
        ├── against the live board, on a schedule          ← catches it within a day
        └── as a gate before any batch applies             ← catches it before JD sees it
```

---

## BAND A — the property set

> **`studies/hypothesis.md`: "Property-based testing … is the missing half of a testing
> strategy."** These are **properties**, not examples. An example test asks *did this case
> work*; a property asks *is this true of everything*, which is the only question that catches a
> component nobody wired.

**A1 · Write the non-degeneracy properties.** Minimum set, each one traceable to a defect it
would have caught:

| property | would have caught |
|---|---|
| every scoring component has a real value for ≥1 company | **velocity** (growth always excluded) |
| every board column has ≥1 non-null | **`changes_tags`**, **`workplace_contact`** |
| no scoring input is identical across all rows | **`hq_city`**, **`funding_stage`** |
| every declared control has recorded ≥1 event | **the throttle** |
| every public function has a caller outside its own test | the reachability class |

**Six of the eighteen, from one build.**

**A2 · Failures produce a TABLE, not a first-failure.**

> **`studies/pandera.md`: "lazy validation for batches, so a run surfaces ALL data problems as a
> structured `failure_cases` table rather than failing on the first bad row."**

A first-failure abort tells you `hq_city` is constant and hides that `funding_stage` is too.
**One pass, every violation, one table.**

**A3 · Each property declares its policy on failure — it is not a boolean.**

> **`brain/04`: "Validation is a declared nonconformance policy, not a boolean"** — the
> vocabulary is *reject loudly · discard the value · pass but record · ask again*.

Concretely: a constant scoring input **fails the gate**. A never-called function **reports and
does not fail** — because a dead alias and a disconnected mechanism both trip it and only one is
a bug (BI5), and **a detector that fails on non-bugs gets silenced.** Declare the policy per
property, in the property.

---

## BAND B — make it run without being asked

**This is the fix that converts every other fix from "caught eventually" to "caught by
tomorrow."**

> **`studies/controller-runtime.md`: "Level-triggered is the unattended-reliability principle. A
> scheduled system that only reacts to events accumulates silent drift; one that periodically
> [reconciles] converges."**

**Norman already believes this — and applies it in exactly one place.** The reconcile loop is
level-triggered against the *Notion projection*. **Nothing is level-triggered against the store's
own internal consistency.** The board is kept honest; the system underneath it is not.

**B1 · Schedule the careers lane.** Public ATS APIs, no login, no ban risk, and documented in
its own source as *"the first lane cleared to run unattended"* — with nothing to start it since
day one.

**B2 · Schedule the property set (Band A) against the live board, daily.** This is the whole
point: **a scheduled property run is the difference between a week and a day.**

**B3 · Declare the retry policy per step, with non-retryable errors named.**

> **`studies/temporal.md`: "Retry as declared policy on each step, with non-retryable error
> types."**

A challenge from LinkedIn is **non-retryable, always** — that rule already exists and this is
where it belongs mechanically rather than in prose.

**Out of scope and stated so it does not creep in:** Sales Nav stays attended, JD-supervised,
UI-only, one session at a time. **Nothing in Band B touches it.**

---

## BAND C — stamp derived data with the rule that made it

> **`studies/dlt.md`: "Versioned schema with explicit upgrade paths; versioned/hashed state."**

**C1 · Every stored derived value carries the version of the rule that derived it.**

You already do this for scores — `formula_version` — which is why score drift is countable.
**Velocity had `velocity_basis` but no rule version, which is why ten rows sat violating ruling
U-c for weeks: the code obeyed the ruling and the data never did.**

Apply it to: **velocity · desk-role classification · industry tags · status routing.**

**C2 · A stamp is only useful if something reads it.** Add the count: **how many rows carry a
rule version older than current?** That number belongs in the daily run from B2.

> **A ruling is not applied until the existing rows are re-derived or counted.**

---

## THE LOOP

```
budget: 3 passes. Not 4.
each pass: run Band A + B + C → fix only what failed → re-run ALL of them
all green → stop.
after pass 3 with anything red → escalate the criterion. No fourth pass.
```

**Frozen scope: anything found that is not on this checklist goes to `found-not-fixed.md` —
recorded, not fixed.** Two exceptions: data loss, or risk to JD's LinkedIn account.

**One report at the end. Not one per finding.**

---

## EXPLICITLY OUT OF SCOPE

The render pass and careers-URL discovery *(loop 2's Band A — this loop does not take it over)* ·
floor storage · the Notion views · `last_touched_on` · any new scoring signal or weight ·
**ingesting any CSV** · anything touching Sales Nav.

---

## WHAT WON'T WORK — say so if you find yourself reaching for it

- **More unit tests.** 548 caught none of the six.
- **More review rounds.** They terminate when someone stops looking.
- **More rigor per item.** The rigor was never the problem; it was pointed at the wrong layer.

---

## SUCCESS

**Not zero bugs.** The distance between introducing a defect and meeting it is measured in
**hours instead of rounds**, and the thing that measures it runs whether or not anyone asks.
