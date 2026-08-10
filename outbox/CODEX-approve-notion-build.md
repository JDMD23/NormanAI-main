# Approved — with one change and two notes

The design is right, and the three limitations you surfaced unprompted are the parts that make
it trustworthy: the `Action Needed` select constraint, the email-subject inference (correctly
labelled as an inference), and refusing to claim delivery you can't verify. **Keep doing that.**

---

## ONE CHANGE — drop the filter on BY SIZE

**Specified:** `NYC Employees is not empty`. **Change to: no filter.**

Converting `Default view` into `CHANGED` is right, but it leaves no view showing the whole
board. **Removing this filter makes BY SIZE the complete board, grouped** — and it does something
better than that: **52 companies have no NYC headcount yet, so they form their own empty-band
group, which makes the measurement backlog visible instead of hiding it.**

An unmeasured company disappearing from a size view is exactly the kind of silent omission we've
been eliminating all week.

Everything else in BY SIZE stands: group by `NYC Band`, sub-group by `Status`, sort `NYC Δ ↓`,
collapsed by default.

---

## TWO NOTES — both "expected, not broken"

**1 · `Signal` will be mostly empty at first.** It concatenates `NYC Δ` and `Desk Jobs`, which
**Norman does not write yet**. The formula is correct; its inputs arrive later. Build it, expect
it sparse, and don't treat the emptiness as a defect.

**2 · Same for `NYC Band` if grouping-by-formula fails** and you fall back to a select — every row
stays blank until Norman projects it, as agreed. **No backfill either way.**

---

## APPROVED AS PROPOSED

- **Hybrid build** — structured for properties, UI for presentation. Correct call.
- **`Default view` → `CHANGED`.** Yes.
- **`NYC Band` as formula, select fallback, no backfill.** Yes.
- **Formulas preserve blanks.** That's the blank-is-not-zero rule applied to display — good.
- **View order, filters, sorts, groups, 7-column max.** As specified.
- **`NEEDS ME` OR-filter over the existing `Joe:` options**, excluding `Joe says: no careers page`,
  documented as needing manual additions. Correct and the caveat is the important half.
- **Buttons hidden from working views, live on opened pages.** Right — a button column is noise.
- **Automations 1–3 omitted entirely.** Yes.
- **Static subject `Norman — weekly CRM changes`.** **Accepted.** The requirement was never the
  dynamic count — it was that the email **sends unconditionally every Friday**, so that a missing
  email means something is broken. A static subject satisfies that completely. The count is a
  later Norman-side nicety.
- **Test email now, and report "Notion sent it" rather than claiming delivery** if you can't see
  the inbox. Correct.

**Write the build specification for review, then build.**
