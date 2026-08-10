# The views — five views and one page, specified exactly

**Design rules, applied throughout:**

1. **One question, one axis.** A view that answers two questions answers neither well.
2. **Every view declares whether it can EMPTY.** A queue empties; a report cannot. Both are
   legitimate — **but a report needs a top-N discipline and a queue needs nothing.**
3. **Every view declares an expected size.** Blowing past it is a signal that something upstream
   broke — **not a filter to tune.** ("Changed Recently" returned 93 of 95 once; an expectation
   would have caught it without anyone looking.)
4. **Sort by value, so partial completion is still optimal.** If you clear half a queue, you want
   to have cleared the half that mattered.

---

## 1 · TODAY — "Who do I call?"

**REPORT** — cannot empty. Needs a top-N discipline.

| | |
|---|---|
| **Filter** | `Status` is any of `Top Pursuit`, `Prospect` **AND** `Reachable` is not `None` |
| **Group by** | `Status` — so Top Pursuit sits above Prospect |
| **Sort** | `Fit Raw` ↓ · then `NYC Open Jobs` ↓ · then `NYC Employees` ↓ |
| **Show** | Company · Fit Score · NYC Employees · NYC Open Jobs · Best Contact · Best Contact Title · Reachable · Action Needed · Current Angle |
| **Expect** | ~40–55 today. **Work the top 10.** |

**Why those tiebreaks.** At equal Fit Raw, **open NYC roles beat headcount** — hiring is the
company *acting*, headcount is the company *existing*. Your §1a says size leads and growth
amplifies; at a tie, growth is the tiebreak.

**Why `Action Needed` is shown but NOT filtered.** A company can be chaseable *and* owe you a
careers link. **Filtering it out would hide a live prospect behind an errand.** Showing it lets
you see the errand while deciding.

---

## 2 · MY QUEUE — "What is waiting on me?"

**QUEUE** — empties. This is your best-designed view and it stays as it is.

| | |
|---|---|
| **Filter** | `Action Needed` starts with `Joe:` **AND** does **not** start with `Joe says:` |
| **Sort** | `Fit Raw` ↓ |
| **Show** | Company · Action Needed · Fit Score · Status · Last Checked |
| **Expect** | **< 15.** At 40+, a lane is failing and filling your queue with its output. |

**The `Joe says:` exclusion is load-bearing.** `Joe:` means *the queue waits on you*; `Joe says:`
is *a fact you already supplied*. A naive prefix match refills your queue with the exact answer
you already gave.

**Sorted by Fit Raw on purpose:** clear five of twelve and you cleared the five that matter.

---

## 3 · WHAT MOVED — "What did the companies do?"

**QUEUE-ish** — should be near-empty in a quiet week.

| | |
|---|---|
| **Filter** | `Changes` is not empty **AND** change origin = `company` *(not `system`)* |
| **Sort** | score delta magnitude ↓ · then `Last Checked` ↓ |
| **Show** | Company · Changes · Fit Score · Status · Last Checked |
| **Expect** | **5–15 a week.** At 90, either a formula changed or a lane broke. |

**Magnitude before recency.** Within a week recency is nearly uniform, so it sorts almost
randomly; magnitude puts the real movement on top.

**The origin filter is the whole view.** "What moved" must mean *the company moved* — not that
**we** re-scored it. A formula change that moves 43 scores is not 43 companies changing.

---

## 4 · NO WAY IN — "Which good companies can't I reach?"

**QUEUE** — empties, and every row is a solvable problem. **This is the view that converts.**

| | |
|---|---|
| **Filter** | `Reachable` is `None` **AND** `Status` is any of `Top Pursuit`, `Prospect` |
| **Sort** | `Fit Raw` ↓ |
| **Show** | Company · Fit Score · Contacts · Website · LinkedIn · Careers Page |
| **Expect** | **1–5 today** (50 of 51 have a contact). Rising means the contact lane is failing. |

**Why it earns a view:** a high-fit company you *cannot reach* is a specific, fixable problem.
Today it is **indistinguishable** from a low-fit company you are correctly ignoring — so it never
gets fixed.

---

## 5 · OUTGROWING — "Who signed recently and is running out of room?"

**QUEUE** — and the highest-conviction list on the board: these companies have *proven* they
transact.

| | |
|---|---|
| **Filter** | `Status` is `Recently Signed Lease` |
| **Sort** | utilisation ↓ *(heads now ÷ (RSF ÷ 170))*, falling back to heads now ÷ heads at signing |
| **Show** | Company · Lease Signed On · NYC Employees · Heads at Signing · Utilisation · Best Contact |
| **Expect** | small. **Above 85% utilisation is a call.** |

**This is the only view needing new data** — `lease_signed_on`, `lease_rsf`,
`nyc_heads_at_signing`. Without the headcount baseline there is no outgrowth signal, only a
current number with nothing to compare it to.

---

## 6 · PIPELINE FLOW — a PAGE, not a view

**Say this plainly: it cannot be a Notion view.** A view filters *rows*; this counts *transitions
between states over time*, which is an aggregate over the change log.

**So Norman writes it weekly into a page:**

```
                      this wk   last wk
  → Research             12        8      inflow
  Research → Tracking     4        6
  Tracking → Prospect     3        2
  Prospect → Top Pursuit  1        0      ← the number that matters
  → disqualified          5        3      outflow, by reason
```

**Flow, not stock.** Stock tells you the shape of the funnel; **flow tells you whether the machine
is working** — inflow drying up, a stage nothing ever leaves, disqualifications spiking on one
reason.

---

## WHAT NOT TO BUILD

- **No "All Companies" view.** That is the default table.
- **No per-industry or per-HQ views.** Those are filters you apply for thirty seconds, not views
  you maintain.
- **No "Top Pursuit only".** Grouping in view 1 covers it.
- **No "Recently Added".** That is a sort, not a view.
- **No staleness view.** `Next Check Due` and the cadence own that; it is a machine concern.

> **Six surfaces total. Every additional view is a place for the board to disagree with itself.**

---

## THE SIZE ASSERTIONS, collected

| view | expect | what a breach means |
|---|---|---|
| Today | 40–55 | fine; work the top 10 |
| My Queue | < 15 | a lane is failing into your queue |
| What Moved | 5–15/wk | a formula changed, or a lane broke |
| No Way In | 1–5 | the contact lane is failing |
| Outgrowing | small | — |

**These belong in the property set** (loop 3), run daily against the live board. **A view that
silently triples is the earliest available signal that something upstream broke** — and it is the
signal that was available, and unread, when "Changed Recently" returned 93 of 95.
