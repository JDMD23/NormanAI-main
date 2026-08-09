# To the CRMx build agent — rounds 36–37: the contact layer was specced as a roster. JD's actual instrument is a trigger.

We captured JD's Sales Navigator persona and five saved searches
(`reference/salesnav-workplace-poc.md` in NormansBrain, raw JSON alongside it). **It changes
the shape of what AP1–AP7 approved.** Read this before the discovery batch runs.

---

## 1. Six of six searches filter on RECENCY. This is an event stream, not a roster.

`years_in_current_position = "Less than 1 year"` — **6 of 6 saved searches.**
`Changed jobs in last 90 days` — **5 of 6.**

**Not one of them asks who the workplace POC IS. Every one asks who just BECAME one.**

The recency isn't a refinement on the search, it *is* the search. A new COO / CFO / Chief of
Staff / Head of People at a growing company is the moment office needs reopen. Someone three
years into the seat has already solved their space problem.

**So the contact layer is two things and round 35 specified only the first:**

| | what it is | |
|---|---|---|
| **Roster** | who holds the relevant seat at each of the 51 | static — what AP1–AP7 covers |
| **Trigger** | who *moved into* one of those seats recently | perishable, time-bound, **the higher-value half** |

**And it closes a loop you already own half of.** `config/desk-roles.json` already records
that "Head of Workplace" is *"a desk role AND the strongest buy signal — somebody is standing
up an office."* The careers lane detects a company **hiring** that role. A person-recency
trigger detects it **having hired** one. **Same signal, two stages — you built the earlier one
and not the later one.**

---

## 2. Two title vocabularies, split by company size — a discontinuity, not a gradient

**Vocabulary A — the `Workplace POC` persona, 28 titles**, run at headcount 11-50 / 51-200 /
201-500: founder, CEO, COO, CFO, ops, finance, people, chief of staff — and reaching down to
Office Manager, Operations Coordinator, and *Executive Assistant to the CEO*.

**Vocabulary B — 14 real-estate titles**, run up to 1001-5000, North America + Europe: Head of
Real Estate, Global Corporate Real Estate, Head of Global Facilities, VP Workplace Experience.

> **The rule JD encoded without stating it: WHO you call is a function of company size, and
> it's a step change. Below ~500 heads there is no real-estate person, so the seat is
> ops/finance/founder. Above it, there is one.**

**Norman's board is 11–500 end to end. Vocabulary A is operative. Vocabulary B is a different
book of business — do not blend it into the contact layer.**

---

## 3. Geography is a BAND, never a filter — and JD's answer makes that load-bearing

I asked why `San Francisco Bay Area` sits in his canonical NYC persona. His answer:
**deliberate — SF-headquartered companies opening or growing a NYC office, where the
decision-maker sits in SF.**

**That corrects the emphasis in AP4.** I framed person-location as convenience — Manhattan
coffee vs Tel Aviv 7am call. **JD's actual model: the person who signs a NYC lease routinely
does not sit in NYC, and that's an expected case, not an anomaly.**

Which makes never-filtering **load-bearing rather than cautious**. Filtering contacts to
NYC-metro would systematically drop the decision-makers at exactly the companies standing up a
*new* NYC office — no incumbent broker, no existing lease.

**Ruling:**
- **NYC band = metro**, region `90000070` — JD's call, and it also resolves an inconsistency
  we found: his persona used the *city* geography while ADR 0003 pins the *metro* one. Two of
  his near-identical searches returned **93 vs 121 on that difference alone — ~30% of his
  workplace-POC population lives outside New York City proper.**
- **SF Bay = a recognised second band**, not a stray.
- **Everything else = other**, captured and displayed.
- Tagged `apollo/person-state` per AP7 — coarse enough to band, never a NYC measurement.

---

## 4. The spec

**Do not filter on geography. Do not filter on seniority either** — seniority would drop
Office Manager, Operations Coordinator and EA-to-the-CEO, which is exactly the small-company
long tail carrying JD's expertise.

**Tier the titles instead of narrowing them — AF4's cascade, applied to people:**

- **Tier 1 (specific, high-signal):** CEO · Founder · Co-Founder · COO · CFO · Chief of Staff ·
  Head of Operations · Head of Finance · Head of People / CPO · Head of HR · Workplace Manager ·
  Workplace Coordinator · Office Manager · Director of Operations · VP Finance · VP Operations ·
  General Counsel · Head of Legal · EA to the CEO
- **Tier 2 (generic tokens):** `Head` · `Vice President` · `Talent` — carried, ranked **below**
  tier 1, and used as the answer only when tier 1 returns nobody for that company.

**The tier IS the rank.** Those three tokens are safe in Sales Nav only because his searches
also scope to saved accounts; in Apollo with `include_similar_titles: true` they match every
VP of anything. Tiering keeps the recall without the drowning — and **ranking people within a
company is a separate problem from `contexts/priority` ranking companies. Don't fold them.**

**Recency by a second query, not by a returned field** — whether Apollo's response carries
time-in-role is unverified, so don't depend on it:

1. roster query — no recency filter
2. **the same query plus `person_days_in_current_title_range: {max: 90}`**

Anyone in set 2 is flagged **TRIGGER**. Deterministic, independent of response shape, and it
reproduces the filter in 6 of 6 of JD's own searches. **Observable: both set sizes, per
company.**

**Still binding from round 35:** per-domain accounting including the zeros (AP1), name-echo
before attach (AP7 — your own Apollo eval found 1 in 6 domains misbound), `include_similar_titles`
set explicitly and matched titles recorded (AP3), declared-or-nothing on anything actionable
(AP5).

---

## 5. What does NOT port — recorded so it's never silently assumed

| Sales Nav | Apollo |
|---|---|
| `COMPANY_HEADCOUNT` 11-50 / 51-200 / 201-500 | `organization_num_employees_ranges: ['11,50','51,200','201,500']` — **ports exactly** |
| `YEARS_IN_CURRENT_POSITION` <1 year | `person_days_in_current_title_range: {max: 365}` — **ports** |
| **"Changed jobs in last 90 days"** | **NO people-search equivalent.** `contact_job_changed` covers already-saved contacts only. Approximate with `{max: 90}` — arguably better, a measured duration rather than a platform flag. |
| **Person geography** | **name ports, granularity fails** — 60–88%, state-ish (your own eval) |
| **LinkedIn's 39-value industry taxonomy** | **no crosswalk.** Use Norman's own taxonomy; don't translate between two foreign ones. |
| **Boolean title syntax** | **doesn't exist.** JD's strings are pure ORs so decomposition is lossless *today*; any future AND/NOT drops silently. That's the failure mode to guard. |

---

## 6. One finding for the discovery lane, unparked

JD wants SF-HQ'd companies growing into NYC. **Norman cannot currently represent one.**

All 95 companies carry `hq_city = "New York"` — that's how they entered, via a Crunchbase
filter selecting on **registered address**. Round 30 found measured NYC concentration running
0–79% against that constant and parked the consequence.

**His answer converts that parked question into a stated requirement: the prospect profile he
just described is structurally excluded by the intake filter.** The board cannot contain the
type he says he wants.

**Not urgent enough to preempt the contact layer — but don't fix it by loosening the filter.
Fix it by sourcing on NYC PRESENCE (headcount, roles, offices) rather than registered
address.**

---

## Order — unchanged except that discovery now carries §4

1. **Discovery batch** with the tiered titles, both passes, geography banded not filtered.
2. **`contexts/priority`** — starts when discovery lands, does not wait on the email decision.
3. **Email reveal** — JD's call, scoped by him.
4. Coverage sessions for the remaining 49 — throttle-gated, his go per session.
5. Views and the careers schedule stay parked. Discovery-lane geography joins the parked list
   with a stated requirement attached rather than a hypothesis.
