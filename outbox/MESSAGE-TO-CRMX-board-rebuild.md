# To the CRMx build agent — the board rebuild

**Not now — after loop 3.** Recorded so it is ready when it comes up. Full specs in NormansBrain:
`reference/notion-one-board-design.md`, `notion-views-spec.md`, `notion-segments-and-indicators.md`.

**One database. Six surfaces. Nine new properties, and eight of them are arithmetic on values
already stored.**

---

## A · NINE NEW PROPERTIES

**Free — arithmetic over fields already in the store. No measuring, no fetching, no credits.**

```
NYC Δ         nyc_employees      − prev_nyc_employees
Jobs Δ        nyc_open_jobs      − prev_nyc_open_jobs
Desk Jobs     nyc_jobs_in_office + 0.8 × nyc_jobs_hybrid     ← JD's own weighting
Intensity     Desk Jobs ÷ nyc_employees
NYC Band      banded nyc_employees     ← fills `employee_band`, which exists and is EMPTY
```

**Run the distribution query before choosing the band cuts.** JD's bands are linear and startup
headcount is log-distributed; if most of the board lands in the first two, use
`0–10 · 10–25 · 25–50 · 50–100 · 100–200 · 200+`.

**From the 173 people already in SQLite — currently projected nowhere:**

```
Best Contact · Best Contact Title · Reachable (LinkedIn/Email/Both/None) · Contacts (count)
```

**Full roster into the company page body**, written by reconcile, same as the fit math.

**Needs JD, once per company** — only for view ⑥:
`lease_signed_on` · `lease_rsf` · `nyc_heads_at_signing` → `Utilisation`

---

## B · DEMOTE 26 PROPERTIES TO THE PAGE BODY

**50 → 24.** Nothing is lost — ADR 0001 makes the board a projection and the page body is part of
it.

- **The eight `Fit:` columns.** Never filtered; `Fit Drivers` is what gets read. **Round 3 already
  ruled this and they came back** — a ruling nothing checks regresses.
- **The four `Months:` columns.** All four flagged EMPTY by the detector.
- Funding detail (6) · reference links (4) · provenance (4)

---

## C · SIX SURFACES

| | view | filter · sort |
|---|---|---|
| ① | **Hiring** | `Desk Jobs > 0` · sort `Intensity` ↓ *(second saved sort: `Desk Jobs` ↓)* |
| ② | **Momentum** | `NYC Δ ≠ 0` · sort `NYC Δ` ↓ |
| ③ | **Outgrowing** | `Status = Recently Signed Lease` · sort `Utilisation` ↓ |
| ④ | **No Way In** | `Reachable = None` ∧ `Status ∈ {Prospect, Top Pursuit}` · sort `Fit Raw` ↓ |
| ⑤ | **My Queue** | `Action Needed` starts `Joe:` **and not** `Joe says:` · sort `Fit Raw` ↓ |
| ⑥ | **Pipeline Flow** | **a page, not a view** — weekly transition counts from the change log |

**Group by `Status` or `NYC Band` in any view.** A segment is a property you group by, not a view
you maintain — that is how 8 bands × 5 statuses stays at six surfaces.

**No chase-list view.** The default table sorted by Fit Score *is* the chase list.

---

## D · SIZE ASSERTIONS — into the property set

| view | expect | breach means |
|---|---|---|
| My Queue | < 15 | a lane is failing into JD's queue |
| No Way In | 1–5 | the contact lane is failing |
| What Moved | 5–15/wk | a formula changed, or a lane broke |

**A view that silently triples is the earliest signal something upstream broke.** *"Changed
Recently"* returned 93 of 95 and was caught only because a human read the number.

---

## ORDER

1. **The five computed properties.** Arithmetic, no new data.
2. **The four contact properties + the roster in the page body.**
3. **Demote the 26.**
4. **The six surfaces.**
5. Lease fields when JD supplies them.

**Steps 1–4 need nothing from anyone.**
