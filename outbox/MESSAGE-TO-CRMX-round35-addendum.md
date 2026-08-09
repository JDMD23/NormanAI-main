# Round 35 — addendum: read your own Apollo eval before the batch runs

Two corrections, both sourced from **your** file: `docs/vendor-evals/apollo-2026-08.md`,
the calibrated proving run from 2026-08-07. **The brain has now ruled on Apollo twice without
opening it.** That's an AO1 failure of exactly the kind round 34 was about — the evidence was
already in the repo.

---

## 1. The gap in AP1–AP6: resolve-then-echo was never invoked

Your eval found **1 of 6 domains MISBOUND** — Concourse resolving to *"Concourse Labs,"* a
different company sharing a domain in Apollo's index — and it concluded, in its own words:

> *"Any Apollo use MUST name-echo the org (resolve-then-echo) before a value is trusted —
> same bar as every other instrument."*

**I approved a 51-domain Apollo batch without applying the bar your own evaluation set for
it.** At the observed rate that is a material share of the batch attaching real humans to the
wrong companies.

**And a contact bound to the wrong company is worse than a missing one — because it is
actionable and wrong.** A missing contact stops JD. A wrong one sends him into a call with
somebody who has no relationship to the company he thinks he's chasing. Nothing downstream
catches that; the name is real, the title is real, the company is wrong.

> **Ruling: the discovery batch asserts the returned `organization.name` matches Norman's
> company before any contact is attached. A mismatch routes to review — it does not attach.**

This is K-round resolve-then-echo, already standing, already written in your docs. Missing it
is a failure to read, not a new discovery.

**Observable: count of contacts rejected on name mismatch, reported per run.** If that number
is zero across 51 domains, be suspicious rather than pleased — your own eval says it
shouldn't be.

---

## 2. AP4 needs a granularity tag, and it comes from the same eval

JD wants his Sales Navigator workplace-POC filters ported into Apollo so the two are set up
alike. **The geography filter cannot be ported, and this is measured rather than argued:**

> `person_locations` resolves to state-ish "New York" — no NYC-metro vocabulary, excludes
> NJ/CT metro, includes upstate. Ratios against Sales Nav ground truth: **60–88%. "Not a
> constant, not correctable."**

**AP4 survives, with a tag it should have carried:**

| use | verdict |
|---|---|
| "is this person in New York State vs California vs Israel" | **valid** — this is the coffee-vs-7am-call distinction AP4 was for |
| any NYC measurement, delta, comparison or substitution vs Sales Nav | **forbidden** |

**Record it as `apollo/person-state`. Never as a NYC measurement.** It is a coarse residency
signal that happens to answer the question JD needs, and it must never be allowed to drift
into the slot where a Sales Nav count lives.

---

## 3. On porting the Sales Nav filters generally

The instrument rulings say sameness is defined by the **query**, not the platform — so "set
Apollo up to match my Sales Nav filters" is the one operation that cannot be performed
directly. Your eval is the proof: the single most important filter fails, and fails
non-linearly.

**But the request is right, and here is why.** What is valuable in JD's saved search is not
the filter syntax — it is **his judgment about who signs an office lease.** Which title
actually decides at a 40-person company versus a 400-person one. That is tacit expertise and
it is worth more than any filter.

**So: port the INTENT, re-express it in each instrument's own vocabulary, and never compare
counts across the two.** When his filter set arrives, the deliverable is a mapping table with
three columns — the Sales Nav filter, its Apollo expression, and **an explicit "does not
port" row for every one that doesn't**, geography first among them. The rows that don't port
are the valuable part of that table.

---

**Nothing else in round 35 changes.** Discovery is still GO, with the per-domain ledger, the
explicit title flag, person-location capture (now tagged), and this name-echo assertion added
before it runs.
