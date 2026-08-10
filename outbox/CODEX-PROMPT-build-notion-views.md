# Codex — build the Norman CRM views

Database: **Norman CRM** · `3b43930e-64f4-8136-a6ef-c8dfb4ac09a5`
Today it has **one unfiltered table view showing all 50 properties.** Everything below is new.

---

## STEP 1 — CREATE 6 PROPERTIES FIRST (views depend on them)

| property | type | definition |
|---|---|---|
| `NYC Δ` | number | `NYC Employees` − previous reading *(Norman writes; create as number)* |
| `Desk Jobs` | number | in-office + 0.8 × hybrid NYC roles *(Norman writes)* |
| `Intensity` | formula | `Desk Jobs / NYC Employees` — show as % |
| `NYC Band` | select | `0-20` `20-40` `40-60` `60-80` `80-100` `100-150` `150-200` `200+` |
| `Signal` | formula | text: `{NYC Employees} NYC · {NYC Δ with +/-} · {Desk Jobs} desks` |
| `Reach` | select | `LinkedIn` · `Email` · `Both` · `None` |

---

## STEP 2 — THE SEVEN TABS, left to right

### ① CHANGED · table
```
FILTER   Changes  is not empty
     AND Changes  does NOT contain  "First check"
     AND Last Checked  is within  the past week
SORT     Last Checked ↓
COLUMNS  Company · Changes · Fit Score · Status · NYC Δ · Last Checked
```
**Expect 5–15/week.** Excluding `First check` is what makes this "what companies did", not "what we scored".

### ② PROSPECTS · table
```
FILTER   Status is  Prospect
SORT     Fit Score ↓ , then NYC Open Jobs ↓ , then NYC Employees ↓
COLUMNS  Company · Fit Score · Signal · Status · Reach · Action Needed · Current Angle
```
**~51 rows.** At equal fit, open roles break the tie — hiring is the company *acting*.

### ③ TOP PURSUITS · table
```
FILTER   Status is  Top Pursuit
SORT     Fit Score ↓
COLUMNS  Company · Fit Score · Signal · Reach · Current Angle · Relationship Notes
```

### ④ NEW INTAKE · table, grouped
```
FILTER   Added On  is within  the past month
GROUP BY Added From          (collapse all groups by default)
SORT     Added On ↓
COLUMNS  Company · Added On · Status · Fit Score · NYC Employees · Data Status
```

### ⑤ BY SIZE · table, grouped + sub-grouped
```
FILTER   NYC Employees  is not empty
GROUP BY     NYC Band     (collapse all by default)
SUB-GROUP BY Status
SORT     NYC Δ ↓  within each group
COLUMNS  Company · NYC Employees · NYC Δ · Desk Jobs · Intensity · Fit Score
```
**Sorting by growth inside each band is the point: the fastest-growing company *of its size*.**

### ⑥ HIRING · table
```
FILTER   Desk Jobs  >  0
SORT     Desk Jobs ↓ , then Intensity ↓
COLUMNS  Company · Desk Jobs · Intensity · NYC Employees · Status · Fit Score
```

### ⑦ NEEDS ME · list
```
FILTER   Action Needed  starts with  "Joe:"
     AND Action Needed  is not  "Joe says: no careers page"
SORT     Fit Score ↓
COLUMNS  Company · Action Needed · Fit Score        ← three only; it is a queue
```
**Must be able to reach zero. Expect under 15.**

### ⑧ HEALTH · chart
```
TYPE     bar
X        Status          Y  count
```
**Free plan allows ONE chart.** If paid, add a second: X = `NYC Band`, Y = count.
Chart views are read-only.

---

## STEP 3 — AUTOMATIONS (4)

| # | trigger | action |
|---|---|---|
| 1 | `Status` → `Top Pursuit` | Slack notification |
| 2 | `Action Needed` changes to any `Joe:` value | Slack notification |
| 3 | Page added | Slack: new company + its `Added From` |
| 4 | Every Friday 8am | Email me — the week's changes |

**No automation may write a machine-owned property** (anything Norman computes: Fit, NYC counts, Status, Changes). Notifications only, plus the buttons below.

---

## STEP 4 — BUTTONS (4)

| button | sets |
|---|---|
| **Chase this** | Status → `Top Pursuit` |
| **Not now** | Status → `Tracking` · Next Check Due → +90 days |
| **Not a fit** | Status → `Not a Fit` |
| **Called today** | Last Touched → today |

---

## RULES — apply to every view

1. **Max 7 columns.** More and it scrolls sideways and stops being scannable.
2. **Every view has an explicit sort.** There is no neutral order — only a stated one and an accidental one.
3. **Same columns wherever possible.** If columns move between tabs, the screen has to be re-learned on every click.
4. **Empty ≠ bad.** A blank `NYC Employees` must never sort as though it were zero. Sort ascending only where blank-last is correct.
5. **No view may return the whole board.** If one does, the filter is wrong — do not widen it, report it.

---

## DO NOT

- Do not create a Board view *(deferred — deal flow isn't built)*
- Do not create a Timeline *(needs lease dates that don't exist yet)*
- Do not hide or delete any property — **views control visibility, the schema stays intact**
- Do not add a Notion formula that computes a score

---

**Report back:** each view created, its row count, and anything Notion wouldn't let you configure.
