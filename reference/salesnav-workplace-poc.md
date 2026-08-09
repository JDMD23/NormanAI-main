# JD's Sales Navigator workplace-POC instrument — captured and decoded

**Captured:** 2026-08-09 via Codex (8 page loads, no interstitials).
**Raw:** `reference/captures/salesnav-workplace-poc-2026-08-09.json`
**Persona `Workplace POC`, updated 7/23/2026 — this is the canonical definition.**

This is JD's tacit knowledge about who signs an office lease, made explicit. It is the most
valuable operator artifact in the repo, and it does **not** say what the round-35 contact
plan assumed it said.

---

## 1. THE HEADLINE: this is not a roster search. It is a TRIGGER.

**`years_in_current_position = "Less than 1 year"` appears in 6 of 6 searches.**
**`Changed jobs` / `Changed jobs in last 90 days` appears in 5 of 6.**

Not one saved search asks *"who is the workplace POC at company X."* Every single one asks
**"who just BECAME one."**

| search | n |
|---|---|
| NYC – New Target Roles – 90 days | 93 |
| New Real Estate Jobs – Tech/Media/Finance | 130 |
| NYC – New Roles (90d) | 121 |
| Head of Real Estate – Recent Job Change | 185 |
| Saved Accounts – New CXO | 7 |
| Saved Accounts – New Senior Roles | 2K+ |

**The recency IS the signal.** A new COO / CFO / Chief of Staff / Head of People at a growing
company is the moment office needs get reopened. Someone three years into the seat has
already solved their space problem.

**Consequence for Norman:** the contact layer as specced in round 35 is a **static roster** —
for each of 51 companies, who holds the seat. JD's actual working instrument is an **event
stream**. Norman has never modeled the second one, and it is the higher-value half because it
is perishable: a new COO is a call *this month*.

**And it closes a loop the build already has half of.** `config/desk-roles.json` already
knows that "Head of Workplace" is *"a desk role AND the strongest buy signal on the board —
somebody is standing up an office."* The careers lane detects a company **hiring** that role
(a posting). A person-recency trigger detects the company **having hired** one (in seat <90
days). **Same signal, two stages. Norman built the first and not the second.**

---

## 2. There are TWO title vocabularies, and they are two theories split by company size

**Vocabulary A — the `Workplace POC` persona (28 titles)**

> Founder · Co-Founder · CEO · CFO · COO · VP Finance · VP Operations · Director of
> Operations · Head of Finance · Head of Operations · Finance Executive · Chief of Staff ·
> Head of HR · Chief People Officer · Talent · Workplace Manager · Head of Talent Management ·
> **Head** · **Vice President** · Executive Assistant to CEO · Workplace Coordinator ·
> Operations Manager · Office Manager · HR Manager · Head of Legal · General Counsel ·
> Operations Coordinator · Finance Manager

Used with headcount **11-50 / 51-200 / 201-500**.

**The small-company theory: nobody has "real estate" in their title, so the person who finds
the office is ops, finance, people, or the founder.** It reaches down to Operations
Coordinator and *Executive Assistant to the CEO* — which is the knowledge that at a 40-person
company the EA is often the one who actually tours space.

**Vocabulary B — the real-estate searches (14 titles)**

> Head of Workplace · Global Head of Real Estate · Senior Director Real Estate · Global Head
> of RE & Workplace Services · Director of RE & Workplace · Global Corporate Real Estate ·
> Head of Global Facilities · Senior Manager RE & Workplace · RE & Workplace leader · Global
> RE & Workplace Experience · Head of Global RE + Workplace · Head of Real Estate · Director
> of Real Estate · VP Workplace Experience

Used with headcount **11-50 through 1001-5000**, geography North America + Europe.

**The large-company theory: there IS a dedicated real-estate function, so call it.**

> **The rule JD encoded without stating it: WHO to call is a function of company size, and it
> is a discontinuity rather than a gradient.** Below roughly 500 heads there is no real-estate
> person and the seat is ops/finance/founder. Above it there is one.

**Norman's board is 11–500 across the whole of it. Vocabulary A is the one that matters for
the 51 prospects. Vocabulary B is a different book of business** (enterprise, national,
Europe) and should not be mixed into the contact layer.

---

## 3. The geography is inconsistent, and JD ran a natural experiment without meaning to

| search | person geography |
|---|---|
| **Persona `Workplace POC`** (canonical) | `New York, New York, United States` **+ San Francisco Bay Area** |
| NYC – New Target Roles – 90 days | `New York, New York, United States` |
| **NYC – New Roles (90d)** | **`New York City Metropolitan Area`** (region `90000070`) |
| New Real Estate Jobs | North America + Europe |
| Head of Real Estate – Recent Job Change | **none set** |

"NYC – New Target Roles – 90 days" (**93**) and "NYC – New Roles (90d)" (**121**) share the
same title boolean, the same seniority, the same headcount buckets and the same recency
filter. **They differ essentially only in geography — and that is a 30% swing.**

City ⊂ metro, so 121 > 93 is the expected direction. The useful part is the magnitude:
**about a third of JD's NYC workplace-POC population lives outside New York City proper** —
Westchester, NJ, CT — and the *narrower* of the two is the one baked into his canonical
persona.

**Region `90000070` is the NYC-metro region, the same geography ADR 0003 pins as the ruler.**
So: **his canonical persona is narrower than his canonical ruler.** One of them should move.

**San Francisco Bay Area sits in the canonical persona and is unexplained.** It would silently
import Bay Area people into any port of the persona. Flagged, not resolved.

---

## 4. Three tokens that are safe in Sales Nav and destructive in Apollo

`"Head"` · `"Vice President"` · `"Talent"`

These work in Sales Nav because they are **tempered by company scope** — the searches using
them also set `SAVED_LEADS_AND_ACCOUNTS: All my saved accounts`, so the company set is
already narrow, and `SENIORITY_LEVEL` constrains the rest.

In Apollo, `person_titles: ["Head", "Vice President", "Talent"]` with
`include_similar_titles: true` matches **every VP and every Head of anything** — VP
Engineering, VP Sales, VP Product, none of whom sign a lease.

**Norman's Apollo batch is scoped to 51 known domains, so the blast radius is bounded** — but
at a 200-person company it would still return a dozen irrelevant VPs.

> **Ruling: pull broadly, then RANK — do not filter narrowly.** Ranking preserves the real
> insight in Vocabulary A (the EA to the CEO matters at a 40-person company) without drowning
> JD. Filtering would discard exactly the long-tail titles that encode his expertise.

This means **a second ranking problem exists that Norman has not modeled: ranking PEOPLE
within a company**, distinct from ranking companies.

---

## 5. The Sales Nav → Apollo mapping table

**The "does not port" rows are the valuable part.**

| Sales Nav filter | Apollo equivalent | verdict |
|---|---|---|
| `CURRENT_TITLE` (value list) | `person_titles` | **ports** |
| `CURRENT_TITLE` (boolean string) | — | **partial** — Apollo has no boolean syntax; `person_titles` is an implicit OR list. JD's strings are pure ORs, so decomposition is lossless *today*. Any future AND/NOT would be silently dropped. |
| `SENIORITY_LEVEL` [CXO, VP, Director] | `person_seniorities` ['c_suite','vp','director'] | **ports** — different vocabulary, same concept |
| `YEARS_IN_CURRENT_POSITION` "Less than 1 year" | `person_days_in_current_title_range: {max: 365}` | **ports — and this is the one that matters** |
| `RECENTLY_CHANGED_JOBS` / "Changed jobs in last 90 days" | **none in people search** (`contact_job_changed` exists only for already-saved contacts) | **DOES NOT PORT** → approximate with `person_days_in_current_title_range: {max: 90}`. Arguably better: a measured duration rather than a platform event flag. |
| `REGION` (person geography) | `person_locations` | **NAME ports, GRANULARITY FAILS** — measured 60–88% of Sales Nav metro, state-ish only. See `docs/vendor-evals/apollo-2026-08.md`. Usable for *in-NY vs elsewhere*; never as a NYC measurement. |
| `COMPANY_HEADCOUNT` [11-50, 51-200, 201-500] | `organization_num_employees_ranges: ['11,50','51,200','201,500']` | **ports exactly** — identical buckets |
| `INDUSTRY` (39 LinkedIn values, person-applied) | `q_organization_keyword_tags` / NAICS / SIC | **DOES NOT PORT** — different taxonomies with no crosswalk. Norman already has its own industry taxonomy; use that, not a translation. |
| `PERSONA` | — | **no equivalent** — it is a saved filter bundle, not a filter |
| `SAVED_LEADS_AND_ACCOUNTS` | `q_organization_domains_list` | **ports, and better** — Norman holds the 51 domains explicitly rather than by reference |

---

## 6. Two smaller notes worth keeping

- **"Saved Accounts – New Senior Roles" returns 2K+** with only persona + <1 year + all saved
  accounts, and **no job-change recency at all**. That is a firehose, not a work queue — the
  one search in the set that is not operational.
- **"People in CRM" is present but disabled**: *"To enable filter, upgrade contract."* A
  filter that exists and cannot fire — relevant to any future CRM-sync design.

## 7. On the capture itself

Codex reported the one thing that mattered: during a bulk expansion the results page drifted
to an unrelated excluded-company filter; it **discarded the transient state, re-opened the
saved search, expanded each section individually, and verified the encoded filter signature
unchanged after every expansion.** Nothing was saved, 8 page loads, no interstitials.

**That is verify-the-artifact behaviour (AO1) from a tool that was only asked to read.** It is
also why the capture can be trusted: the URL signature is the authority, and it was checked.
