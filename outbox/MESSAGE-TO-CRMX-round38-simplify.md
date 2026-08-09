# To the CRMx build agent — round 38: SUPERSEDES rounds 36–37. Build the simple version.

JD read the rounds 36–37 spec and said it was overbuilt. **He's right.** Ignore the tiering,
the roster-vs-trigger split, the geography banding, and the within-company ranking. None of
that was asked for; it was the brain elaborating on a plain request.

**The actual ask, in his words:** for the companies Norman enriches, get contact information
for the workplace-POC people — operations, finance, people, head of real estate, chief of
staff, the list he gave.

That's the whole thing.

---

## What to build

**One query per batch:**

```
q_organization_domains_list  : the enriched companies' domains
person_titles                : the list below
include_similar_titles       : true
per_page                     : 100
```

**Store per person:** name, title, company, LinkedIn URL, location as returned, and the date
retrieved.

**Do not filter on geography or seniority.** Not as a designed feature — just don't add
filters he didn't ask for.

---

## The title list

His original fifteen, the `Workplace POC` persona, and the real-estate titles, merged and
deduped. **No curation** — if he listed it, it's here.

```
Chief Executive Officer          Head of Operations
Founder                          Head of Finance
Co-Founder                       Head of People
Chief Operating Officer          Head of Human Resources
Chief Financial Officer          Head of Talent Management
Chief People Officer             Head of Legal
Chief of Staff                   General Counsel
Vice President Operations        Director of Operations
Vice President Finance           Operations Manager
Vice President People            Operations Coordinator
Vice President Workplace Experience   Finance Manager
Head of Workplace                Finance Executive
Head of Real Estate              Human Resources Manager
Director of Real Estate          Office Manager
Global Head of Real Estate       Workplace Manager
Director of Real Estate & Workplace   Workplace Coordinator
Global Corporate Real Estate     Executive Assistant to the CEO
Head of Global Facilities        Talent
Senior Director Real Estate      Head
                                 Vice President
```

**One flag, his call, not a design decision:** `Head`, `Vice President` and `Talent` are bare
tokens. With `include_similar_titles: true` they'll pull every VP of Engineering and Sales at
these companies. They're in his persona so they stay — but **report how many results they
alone account for** after the first run, so he can decide whether to drop them. Don't
pre-solve it.

---

## Three things that stay, because they're one line each and prevent real damage

1. **Name-echo before attach.** Your own Apollo eval found **1 of 6 domains misbound**
   (Concourse → "Concourse Labs"). Assert the returned `organization.name` matches Norman's
   company; mismatch routes to review instead of attaching. A contact bound to the wrong
   company is worse than a missing one — it's actionable and wrong.
2. **Record the zeros.** A company where Apollo returns nobody records as "searched, none
   found," not as "no contacts." Every company has a founder, so a zero is always a coverage
   gap, never a fact about the world.
3. **No constructed emails.** Your rule, unchanged. If Apollo doesn't return one, the channel
   is LinkedIn or nothing.

---

## Dropped from rounds 36–37 — do not build

- Tier 1 / Tier 2 title cascade
- Roster vs trigger as two mechanisms
- Geography banding (NYC metro / SF Bay / other) — just store the location Apollo returns
- Within-company people ranking
- The recency second-pass query

**The recency observation was real** — 6 of 6 of JD's saved searches filter on "in seat under
1 year," which is genuinely how he prospects — **but it was an observation about his
workflow, not a request.** Park it. If he wants it later it's one extra query.

---

## Order

1. **This.** Contacts for the enriched companies.
2. `contexts/priority`.
3. Email reveal — JD's call, after he sees who came back.
4. Coverage sessions for the remaining denominators.
