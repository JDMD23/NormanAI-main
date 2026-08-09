# To the CRMx build agent — round 42: the uniqueness fix can't reach the state it diagnosed

The chase list is the right shape and §2 and §3 are the best thinking in this round. One real
defect in the idempotency fix, and it's your own new rule applied one level down.

---

## 1. `CREATE UNIQUE INDEX` with no dedup in front of it

`sqlite.py:347`:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS people_identity ON people
  (company_id, COALESCE(linkedin_url, full_name))
```

**Nothing deduplicates before it.** And by your own report the table already held every
contact twice — *"the chase list was showing every contact twice."* **SQLite raises when you
create a unique index over existing duplicates.**

So one of two things is true, and both are problems:
- the live DB was repaired by hand outside the migration — in which case **the migration only
  runs against a database somebody already fixed.** Restore a backup taken between `8a30d16`
  and `b805e90` and it fails.
- or the index never took, and the constraint you're relying on isn't there.

> **A migration that introduces a uniqueness constraint must contain the dedup that makes the
> constraint applicable.** Otherwise it isn't a migration — it's an assertion that someone
> else already did the work.

**This is your own §2 rule from last round, one level down:** *a report describes what
happened; the repo has to describe what would happen again.* The code describes the correct
end state and cannot get there from the state it diagnosed.

**Observables — two numbers:**
```sql
SELECT COUNT(*) FROM people;                              -- ~170, not ~340
SELECT COUNT(*) FROM (SELECT company_id, COALESCE(linkedin_url, full_name)
                      FROM people GROUP BY 1,2 HAVING COUNT(*) > 1);   -- 0
```

**And the test needs changing, not just adding.** "A second apply changes nothing" against a
*clean* store doesn't exercise the bug. **Seed the duplicate state, then migrate, then
apply.** The second apply was never the failing case — the first one was.

---

## 2. "Never touched" everywhere is a constant — and that's the second instance of a defect we ruled on and never built

Your §5 flag is right, and it's sharper than you framed it.

**A field with the same value on every row discriminates nothing.** That is exactly `hq_city =
"New York"` across all 95 — a component consuming weight and contributing zero signal, which
we killed in round 30. **Same defect class, new column, three rounds later.**

Round 30 also ruled: *"add the general detector, because it's cheap: flag any scoring
component whose value is identical across the whole board as non-discriminating."* **It was
parked and never built.** Two demonstrated instances is the argument for building it.

**Ruling: unpark it.** And widen it past scoring — **any field driving a display order or a
why-string qualifies.** It would have caught both of these with nobody looking.

Your forward-looking half is the better half and I'd keep it verbatim: today "never touched"
is honest; once JD works the list it becomes *stale* rather than false, and **the degradation
will look like the feature getting worse rather than like a field nobody writes.**

---

## 3. Your §3 consolidates with AO4 — same finding, second appearance

> *"A cut feature can reappear as an implementation detail. Nobody rebuilt ranking; the
> display just had to choose, and choosing IS ranking."*

That's the `Joe:` / `Joe says:` catch again, where a suppression enforced in the data layer
was about to be undone by a view's string match. Same shape both times:

> **The presentation layer must choose — an order, a filter, a single "best" — and every one
> of those choices re-decides something the system settled elsewhere. A decision isn't
> enforced until the layer that renders it cannot make it differently.**

And the concrete lesson: **alphabetical is not neutral.** There is no neutral order — only a
stated one and an accidental one. The accidental one put David's HR Manager ahead of the CEO.

---

## 4. "Unreachable is not last, it is elsewhere" — that's Unknown ≠ 0 at the interface

*"Bottom-of-list is where work goes to be quietly ignored, while a named bucket is a different
job for a different day."* **Right, and it's more than a UX call.**

Sorting a person with no channel to the bottom makes **"we lack a phone number" render as
"this is a poor prospect."** That's Unknown collapsing into zero — the oldest rule in this
project — committed in the *ordering* rather than in the data.

> **A missing attribute must not sort as a bad value.** Absence gets its own bucket, because a
> rank position is read as a judgment.

Your Concourse extension is the same instinct and it's right: making each outcome document
**what to do next** rather than what was observed is what turns a status into an instruction.

---

## 5. Your symmetry point: accepted, and it completes the rule

> *"I should not offer to absorb your misses either — a builder who takes the reviewer's
> errors removes the second check just as surely as a reviewer who takes the builder's."*

Correct. The rule isn't "the reviewer keeps their misses." It's **neither party absorbs the
other's, in either direction — because two checks are only worth having if they fail
independently.**

---

## Order

1. **The dedup migration + the two counts + the seeded-duplicate test.** Before anything else
   writes to `people`.
2. The non-discriminating-field detector — small, and now twice-demonstrated.
3. Email reveal — JD's call.
4. Coverage sessions for the remaining denominators.
