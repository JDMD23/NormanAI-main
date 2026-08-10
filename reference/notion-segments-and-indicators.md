# Segments and indicators — group, don't proliferate

**8 headcount bands × 5 statuses = 40 combinations. You do not build 40 views.**

> **A segment is a PROPERTY you group by. A view is a QUESTION you ask.** Notion's *Group by*
> gives you every band as a collapsible section with a count — that *is* the segmented view, on
> one surface.

---

## 1 · THE TWO GROUPING PROPERTIES

**`NYC Band`** — computed from `nyc_employees`, never typed:

```
0–20 · 20–40 · 40–60 · 60–80 · 80–100 · 100–150 · 150–200 · 200+
```

**`employee_band` already exists as a field and the detector flagged it EMPTY.** This is what it
was for. Nothing has ever written it.

**`Status`** — already exists. Top Pursuit / Prospect / Tracking / Research / etc.

**Group by either, in any view, and you get the segmentation without maintaining it.**

---

## ⚠ CHECK THE DISTRIBUTION BEFORE COMMITTING TO THOSE BANDS

```sql
SELECT CASE WHEN nyc_employees < 20 THEN '0-20'
            WHEN nyc_employees < 40 THEN '20-40'
            WHEN nyc_employees < 60 THEN '40-60'
            WHEN nyc_employees < 80 THEN '60-80'
            WHEN nyc_employees < 100 THEN '80-100'
            WHEN nyc_employees < 150 THEN '100-150'
            WHEN nyc_employees < 200 THEN '150-200'
            ELSE '200+' END AS band,
       COUNT(*) FROM companies WHERE nyc_employees IS NOT NULL GROUP BY 1;
```

**Startup headcount is roughly log-distributed, and your bands are linear.** The measured
companies we have on record sit at 4, 50, 50, 64, 84, 92 — so **most of the board will land in
`0–20` and `20–40`, and four or five bands will hold almost nothing.**

**A band with two companies in it tells you nothing.** If the query comes back skewed, the
log-spaced version spreads evenly:

```
0–10 · 10–25 · 25–50 · 50–100 · 100–200 · 200+
```

**Run the query first. Choose the bands from the distribution, not from round numbers** — this is
the same discipline as anchoring score bands on the measured distribution rather than on
intuition.

---

## 2 · THE KEY INDICATORS — what actually predicts a lease need

Six, and they answer different questions:

| # | indicator | question it answers | status |
|---|---|---|---|
| 1 | **NYC headcount** | *how much space* | ✅ on the board |
| 2 | **NYC headcount Δ** | **when** — the leading indicator | ⚠ **computable today, NOT on the board** |
| 3 | **Desk-generating open jobs** | forward pipeline — people not yet hired | ⚠ computed, not surfaced |
| 4 | **Hiring intensity** (desk jobs ÷ heads) | *how urgently* | ❌ not computed |
| 5 | **Funding recency + amount** | *can they sign* | ✅ on the board |
| 6 | **Lease utilisation** | *are they out of room* | ❌ needs the lease baseline |

### #2 is the gap that matters most

**`prev_nyc_employees` and `prev_nyc_open_jobs` are stored** — verified in the entity and the
schema. **The prior measurement exists. The delta is arithmetic. It is on no view and no
property.**

> **You measure NYC headcount on a cadence and never show the change.** The *level* tells you how
> much space a company needs; **the CHANGE tells you when they will need it** — and *when* is the
> entire business.

### #4 — "hiring the most" is ambiguous, and both readings are useful

- **Absolute desk jobs** → *how much* new space they will need
- **Intensity** (desk jobs ÷ current heads) → *how urgently*

**5 open roles at a 20-person company is 25% growth. 5 at a 200-person company is 2.5%.** Raw
count favours the big; intensity favours the ones about to run out of room.

**And it must be DESK-generating roles, not all roles.** You already built the classifier — a
company hiring 20 remote engineers needs no desks. `nyc_jobs_in_office` and `nyc_jobs_hybrid`
exist; the number to show is `in_office + 0.8 × hybrid`, which is your own weighting.

---

## 3 · THE VIEWS — four, all grouping or sorting, none proliferating

**① BY STAGE** — *"where is everything?"*
Group by `Status` · sort `Fit Raw` ↓ within each group · show Company · Fit · NYC Employees ·
NYC Δ · Desk Jobs
→ **Top Pursuit, Prospect, Tracking, Research, all in one collapsible surface with counts.**

**② BY SIZE** — *"what does the board look like by company size?"*
Group by `NYC Band` · sort `NYC Δ` ↓ within each group · show Company · Status · NYC Employees ·
NYC Δ · Desk Jobs · Intensity
→ **Sorting by Δ inside each band is the point: the fastest-growing company *of its size*.**

**③ HIRING** — *"who is hiring hardest?"*
Filter `Desk Jobs > 0` · sort `Desk Jobs` ↓ · show Company · Status · NYC Band · Desk Jobs ·
Intensity · NYC Employees
→ **Keep a second saved sort by `Intensity` ↓. Same view, two questions.**

**④ MOMENTUM** — *"who is actually growing?"*
Filter `NYC Δ` ≠ 0 · sort `NYC Δ` ↓ · show Company · Status · NYC Employees · NYC Δ · Desk Jobs ·
Last Checked
→ **This is the view you do not have, built on data you already store.**

---

## 4 · WHAT TO BUILD, IN ORDER

1. **`NYC Δ` and `Jobs Δ` as properties.** Pure arithmetic on fields already stored. **Cheapest
   thing on this page and the most meaningful.**
2. **`Desk Jobs` and `Intensity` as properties.** `in_office + 0.8 × hybrid`, and that ÷ heads.
3. **Run the band query. Then write `NYC Band`** — from the real distribution.
4. **The four views.** All grouping and sorting, no new data.

**Steps 1 and 2 are arithmetic over values you already have.** Nothing needs measuring, nothing
needs fetching, no credits, no sessions.

---

## 5 · THE ONE INDICATOR YOU CANNOT COMPUTE YET

**#6, lease utilisation** — needs `lease_signed_on`, `lease_rsf`, `nyc_heads_at_signing`. Three
fields you enter once per company.

**Without `nyc_heads_at_signing` there is no outgrowth signal** — only a current headcount with
nothing to compare it against. It is the same denominator problem as NYC concentration, in a new
place.
