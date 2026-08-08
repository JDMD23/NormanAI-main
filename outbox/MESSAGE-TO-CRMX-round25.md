# To the CRMx build agent — round 25: JD's spot-check answers. One weight change, and one signal we don't have.

JD reviewed the seven divergences. Two directives came back, and the second one is a
**gap in the model**, not a tuning note.

---

## 1. Remote job credit: 0.15 → **0**

Asked directly whether the weights matched his valuation, JD: *"Remote should be a true
zero."* A fully-remote role generates no NYC desk demand, so it earns nothing.

**Confirmed weights: in-office 1.0 · hybrid 0.8 · remote 0.0.** Hybrid at 0.8 is
explicitly confirmed as correct — he wants hybrid valued, and 0.8 matches the physical
reality of a shared desk.

Consequences to expect, all of them the intended effect:
- A company hiring **only** remotely now has **0 desk-jobs**, therefore no hiring growth
  signal, therefore capped at medium (W6). Correct — ten remote hires need no NYC office.
- Haast 0.6 → 0.0. Raspberry AI 2.4 → 1.6.
- **Watch one interaction:** desk-jobs of 0 plus ≤4 heads at Series A+ now shelves a
  company that *is* hiring, just remotely. Coherent with the thesis, but it's a **new path
  to the Low-NYC shelf** — verify it fires only where intended.

Process: this is a weight change whose movement **is** the improvement, so **do not
compensate** (contrast AB1, where the mechanism was wrong but the effect acceptable).
Apply → run the oracle (**expect no change** — the corpus is blind to location-type per
AD2) → **show JD every board mover before it lands** → re-freeze metrics.

---

## 2. The gap: not every in-office role is a desk role

JD's exact words: *"sometimes medical companies have like 'therapists, or medical' which
isn't really an in-office user."*

He's right, and this is a real hole in the model. **The desk question has two independent
gates, and we only built one:**

| gate | question | status |
|---|---|---|
| 1 | Is the person physically in NYC most days? | **location-type — BUILT** |
| 2 | Does this role occupy a desk in a commercial office? | **role-type — NOT BUILT** |

A licensed therapist at a health-tech company is "in-office" in the sense of not-remote —
but she's in a clinic seeing patients, not at a desk in an office tower. Same for field
sales, field service techs, drivers, warehouse and fulfilment, retail floor, lab bench,
manufacturing, on-site security.

**Why this matters more than it looks:** it systematically overstates the space demand of
exactly the sectors JD targets. **Healthcare Technology is core #7 on his own list.** This
is not an edge case, it's a bias in his primary hunting ground.

**Ruling: desk-generating role classification joins Phase B — and it outranks seniority in
priority.** Seniority changes *how much* a role counts. This changes *whether it counts at
all*.

**One distinction to encode very carefully**, because the words overlap and the meanings
are opposite:

- **"Head of Workplace" / "Head of Real Estate"** → a desk role **and** a strong positive
  signal (the facilities bonus — they're standing up an office).
- **Facilities technician / janitorial / on-site maintenance** → **not a desk role at
  all.**

Both go through the same classifier. **Test it on that pair explicitly.**

**Live test case: Conduit Health** — 14 NYC roles, 12 hybrid, a health company, currently
reading 10.8 desks. That is precisely JD's concern sitting in the current data. Check what
those roles actually *are* before anyone relies on that number.

---

## 2b. How to build it — a tiered cascade, declared-first, Unknown-honest

JD asked directly how the function should work. Build it as a **cascade that stops at the
first confident answer**, using the same `declared > inferred > unknown` hierarchy already
in the system — so it reuses machinery rather than introducing a new concept.

**Tier 1 — the DECLARED department field.** Free, deterministic, highest confidence.
Greenhouse, Ashby and Lever all publish a department/team on the posting. Map it through a
small **JD-tunable config list**:
- → **desk**: Engineering · Product · Design · Finance · Marketing · Sales (inside) ·
  Legal · People · Data
- → **non-desk**: Clinical · Care Delivery · Nursing · Field Operations · Field Sales ·
  Warehouse · Fulfilment · Retail · Lab · Manufacturing · Facilities (maintenance)

This is data you already have and it should resolve the majority at zero inference cost.
Unmapped → Tier 2.

**Tier 2 — title role-family rules.** A tested rules table, both directions — not a vibe.
Non-desk: `therapist, clinician, nurse, RN, LPN, caregiver, phlebotomist, driver, field
service, field technician, installer, warehouse, fulfilment, retail associate, security
guard, custodial`. Desk: `engineer, developer, designer, product manager, analyst,
accountant, controller, recruiter, counsel, marketer, chief of staff, operations manager`.
Ambiguous → Tier 3.

**Tier 3 — read the posting body.** Only for what Tiers 1–2 can't resolve. Decide on the
text: *"on-site at our clinic," "travel to customer sites," "on the warehouse floor"* vs
*"from our NYC office," "hybrid from our Manhattan office."* **If an LLM does this, it must
quote the sentence it decided on** — evidence-grounded output; no citation, no
classification.

**Scope honesty: do not build Tier 3 speculatively.** Ship Tiers 1–2, measure the
unresolved fraction, build Tier 3 only if that number is material.

**Tier 4 — UNKNOWN, and it stays Unknown.** A role no tier resolves is
`desk_status = unknown`. **Never default it to desk (that's today's bug) and never to
non-desk.**

**What unknowns do to the count — reuse the FLOOR pattern, don't invent a rule.** A desk
count computed with unresolved roles present is a **lower bound** — the unknowns might be
desks. Tag it exactly as the city-vs-metro headcount is tagged (G5):

```
desk_jobs = 8.4 · is-floor: true · unresolved: 3
```

Note this is a **different shape from the freshness rule.** Freshness is a *proportion*, so
one gap corrupts the whole reading — hence "one undated role withholds the count." The desk
count is a *sum*, so a gap **bounds** it rather than invalidating it. Withhold entirely only
when the unresolved fraction crosses a configured threshold; the number stops being useful
before it stops being computable.

**Store the classification per role, not just the aggregate** — that satisfies AE2 (JD
wants to *see* the split) and makes his spot-checks self-serve.

## 3. How to verify — JD told you the method

*"Can't you click a job post on the careers page to vet all this out… if you are
questioning a job posting maybe just click and read it."*

Adopt this as the validation method for inferred readings, and make the distinction
structural:

- **Declared** by the provider (explicit workplace-type field, Comeet's
  `experience_level`) → trust it; tag `declared`.
- **Inferred** from a location string or a title heuristic → tag `inferred`, and **verify
  a sample by opening the actual posting and reading it** before the signal is trusted at
  scale.

This is K1/O1 one level up: **structure over display, source over summary.**

It also hands Phase B its validation method for free. The ~30-title check becomes **"open
these postings and confirm the classification"** rather than labelling titles in the
abstract — stronger evidence, and it is exactly how JD wants to work.

**Immediate:** Knit and GovWell were inferred. Verify them by reading the actual listings
before the Phase A numbers are relied on.

And reinforcing the earlier guidance: **prefer a provider's declared field over any
heuristic wherever one exists.**

---

## Order

1. Apply remote → 0; oracle; **show JD the movers**; re-freeze.
2. Verify Knit and GovWell by reading their actual postings.
3. **The last-projected baseline** (round 24, AE4) — still before Phase B, because Phase B
   writes more lane data into the path that just tried to revert itself.
4. **Phase B**, now three classifiers in priority order: **desk-generating role**
   (highest — it gates whether a role counts), then facilities-role, then seniority.
   Validated by opening real postings with JD, not by labelling titles cold.
