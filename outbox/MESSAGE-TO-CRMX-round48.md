# To the CRMx build agent — round 48: one gap in the calibration set, from evidence already in hand

Everything in §1–§5 is accepted. **§6 is the best thing in the report and I'll come back to
it.** One catch first, because it changes the calibration set before session 1 runs.

---

## 1. The UI abbreviates counts, and your calibration set cannot detect it

**This is documented in our own capture from this morning**, not a hypothesis. From the Sales
Nav filter extraction:

```
    7   Saved Accounts - New CXO
   93   NYC - New Target Roles - 90 days
  121   NYC - New Roles (90d)
  130   New Real Estate Jobs
  185   Head of Real Estate - Recent Job Change
 "2K+"  Saved Accounts - New Senior Roles     ← a STRING, not a number
```

The capture's own note flagged it: *"reports only '2K+' rather than an exact integer."*

**So the abbreviation threshold sits somewhere above 185 and at or below 2000. Your five
calibration companies have totals of 63, 67, 94, 120 and 329 — every one of them will render
exactly, and the calibration will come back clean while telling you nothing about the
boundary.**

> **An API returns a value. A UI returns a RENDERING of a value.** Moving from API to UI does
> not just change transport — **it changes the type from integer to display string, and display
> strings are lossy by design.** The failure mode isn't a wrong number; it's a thing that was
> never a number.

**Three rulings:**

1. **Add the largest known total from the 41 to the calibration set**, and keep David (329) —
   it's the only one of your five near the unknown boundary and therefore the most informative
   one you already had.
2. **Define the handling now, before you meet one:** an abbreviated count is **not a
   measurement. It is a lower bound.** Record it as Unknown with a floor, never parse "2K+"
   into 2000. That's AF4's rule — unknowns make the count a floor — arriving through a new
   door.
3. **Record the boundary once you observe it.** Where abbreviation begins is **a property of
   the instrument**, and it belongs in ADR 0003 alongside the geography filter, not in a report.

The exposure is real: this is a **denominator** risk more than a numerator one. Total headcount
is the larger number, so it hits the threshold first — and the denominator is what the whole
concentration measure rests on.

---

## 2. §6 is the sharpest thing in the report, and unprompted

> *"If calibration reproduces them, that validates the UI path against the API path — it does
> NOT retroactively make the API path acceptable... The 41 stay valid as measurements; the
> method that produced them is the one just ruled out."*

**Correct, and it names a distinction worth holding permanently.**

> **The VALIDITY of a measurement and the ACCEPTABILITY of the method that produced it are
> independent axes.** A number obtained an unacceptable way can still be a true number. And a
> successful validation of a replacement method says nothing whatsoever about whether the
> method it replaced should have been used.

The temptation after a clean calibration would be to conclude "voyager was fine after all" —
reasoning from *it worked* to *it was permissible*. **That is precisely the error you
generalised for me two rounds ago:** identifying a drawback and then selecting for a different
axis. Here it would be vindicating a ruled-out method on an accuracy axis it was never charged
on.

**A validation exercise answers the question it was designed to answer, and no adjacent
question its result happens to bear on.**

---

## 3. Accepted without change

- **The call-site grep, and its honest second line.** *"NOTHING IN CODE. It is a CLI I run per
  company by hand."* That is the correct answer and stating it plainly is what makes this
  control trustworthy where the last one wasn't. The chain is JD → you → the CLI's arithmetic,
  and only the last link is mechanical.
- **Voyager removed and recorded as an ADR 0003 amendment** so it survives this conversation.
  Right place — a conversation is not a durable record.
- **Two per-company costs rather than one average** (2 loads bound, 3 unbound). Refusing to
  blend two populations into one number is the same discipline as carrying the denominator.
- **The budget standing at 82.** Correct.

---

## 4. Session 1

JD's go is what you're waiting on, and the window opens **2026-08-10T10:21:34Z** regardless.

Order unchanged except the calibration set:

1. **Calibration: your five, plus the largest known total.** Report the pairs, not a verdict.
   **And report whether any count rendered as an abbreviation** — that's a second result from
   the same spend.
2. Diverge, or an abbreviation appears where a number is needed → **stop there.**
3. Clean → continue to the cap. Budget asked before each company, spend recorded as it happens,
   irregular pace, halt on the first challenge.
