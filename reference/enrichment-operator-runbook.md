# Enrichment on a logged-in Mac Chrome — operator runbook

**For a new operator doing 80 companies.** Clicks, URLs, fields, stop conditions.

---

## READ THIS FIRST — three things that change the plan

**① There was no "old computer-use enrichment automation."** What is actually on record:

| what ran | evidence |
|---|---|
| Codex captured JD's Sales Nav saved searches | `reference/captures/salesnav-workplace-poc-2026-08-09.json` — **8 page loads, zero interstitials** |
| Codex captured and rebuilt the Notion board | `notion-board-audit-2026-08-10.json` |
| **JD measured Sales Nav by hand** | round 28 — **82 interactions across 41 companies** |
| **JD pasted every careers URL** | **all 85 came from `jd-board-edit`** |

**A per-company enrichment loop was never automated.** Sections below marked **[RECOVERED]** come
from recorded rulings. Sections marked **[NEW]** are specified here for the first time — they are
consistent with the rulings but have not been run.

**② 80 companies is not one day.** Round 28 measured **2.0 Sales Nav views per company**, and a UI
path counts **a page load as one view**. The cap is **80 views/day**.

```
80 companies × 2+ views = 160+ views = TWO sessions minimum, probably three.
```

**Plan 30–40 companies per session. Do not try to finish 80 in a day** — and if the UI path turns
out to need fewer loads than the API path did, **that is headroom, not licence to cover more
companies.**

**③ One thing must be settled on company #1, before the other 79.**

> **The ruling pins the headcount ruler as Sales Nav geography `New York City Metropolitan Area`.
> JD's own captured saved searches use person geography `New York, New York, United States`.**

**I cannot verify from here whether Sales Nav treats those as the same entity.** If they are
different populations, **every headcount on the board is measured on a ruler nobody wrote down**,
and new measurements will silently disagree with old ones.

**Settle it on company #1: run both, compare the counts, write the winner down, never vary it
again.** This is also what the mandated opening test is for — see §9.

---

## 1 · The order of sites for ONE company — and never batch by site [RECOVERED]

```
1  WEBSITE      → canonical domain, careers bind, HQ, summary, founders
2  CRUNCHBASE   → funding fields + the dated round history
3  LINKEDIN     → About: HQ, founded, size band, specialties, website
4  SALES NAV    → the NYC headcount.  LAST, always.
```

**Website first because everything downstream depends on the canonical domain.** You cannot
disambiguate a Crunchbase twin without it. It is also free and carries zero account risk, so a
company that dies here dies cheaply.

**Sales Nav last because it is the only expensive, risky step.** If the company disqualifies on
anything upstream, you never spend a view on it.

### Do NOT batch by site. Two independent reasons.

**Risk.** 80 Crunchbase loads then 80 LinkedIn loads produces a tight uniform block of LinkedIn
traffic. **The danger is not daily volume — it is inhuman regularity.** Interleaving by company
paces the risky lane for free.

**Correctness.** Score, route and status compute only at the **per-company barrier** — when every
lane has a terminal result for *that* company. **Per-company completion means a company scores the
moment its slowest lane lands.** Batch-by-site means nothing scores until the last batch finishes.

---

## 2 · Browser and profile [RECOVERED, with one substitution]

**The ruling is: a dedicated managed Chrome profile, NOT the daily driver.** The reason is blunt —
a LinkedIn ban on your everyday profile costs you your professional network, not a scraping run.

**If you are running on JD's logged-in Chrome anyway** (his call, and it is his account), then at
minimum:

**One window. Three tabs. Reuse them.**

```
TAB 1   the working tab   — website, careers, Crunchbase, LinkedIn company pages
TAB 2   Sales Navigator   — PINNED, never closed, never reloaded from scratch
TAB 3   the scratch record — Notion or a sheet
```

**Pin the Sales Nav tab and keep it alive for the whole session.** Reloading the Sales Nav app
shell costs a page load every time, and page loads are the budget.

**Do not open a tab per company.** 80 tabs is a memory problem and it makes the session
un-auditable — you lose track of which company you are on.

---

## 3 · How to drive the browser [RECOVERED — this one is absolute]

> **UI navigation only. No internal endpoints. No XHR interception. No CDP network capture.**

| allowed | not allowed |
|---|---|
| clicking | calling LinkedIn's voyager API |
| typing a URL in the address bar | intercepting XHR responses |
| reading the rendered page | reading network traffic for data |
| scrolling, waiting | any endpoint the UI does not navigate to |

**A value obtainable only through an internal endpoint is not obtainable.** Record it unavailable.

> **No amount of pacing disguises a voyager call. A slow voyager call is still a voyager call.**

### Pace — irregular, not uniformly slow

**A uniform 8-second gap is as mechanical as a uniform 1-second gap. It is just a slower robot.**

| | |
|---|---|
| between page loads | **4–20 seconds, varied.** Never a constant |
| dwell on a results page | **3–10 seconds** — actually read it |
| session shape | **not N identical cycles.** Vary the order of companies; take a real break |
| session length | **30–40 companies, then stop** |

**And the control that actually protects the account is independent of pace: halt on the first
challenge, no retry.** Pacing addresses behavioural detection. The halt addresses the consequence.

---

## 4 · How you start a company [NEW]

**From the stored card links. Always. Never by typing the name into a site's search box.**

**Name-search is the single largest source of wrong data in this system.** Apollo's own vendor eval
measured **1 in 6 domains misbound** on name matching. A twin gives you confident numbers about a
stranger, and nothing downstream can detect it.

**When a stored link 404s:** search is allowed — **and then you must re-prove identity before
binding anything** (§6, §8). A searched result is a candidate, never a match.

---

## 5 · Crunchbase — what to click and what to copy [NEW]

**Click the stored Crunchbase URL from the card.** Do not search.

**Copy:**

| field | note |
|---|---|
| Latest round name | `Series A` etc. |
| Latest round amount | |
| **Latest round DATE** | **the field that makes funding a growth signal** |
| Total raised | |
| Round count | |
| Lead investors / all investors | |
| Founded year | |
| HQ | cross-check against the website |
| One-line description | for the twin check |

### The high-value ten seconds: copy the ROUND HISTORY TABLE

**This is the most valuable thing an operator can do on Crunchbase, and it is currently nobody's
job.**

`Months: Seed→A`, `A→B`, `B→C` and `Late Stage` are **empty on every row of the board**, and the
growth component **cannot compute for any CSV company**, because the CSV carries a round *name*
and a *count* and **no dates**. Nothing in the system feeds the dated round history.

**You are already on the page that has it.** Copy the funding-rounds table as
`round name + announced date` pairs.

**One rule when you do:** **collapse rounds announced within 7 days of each other.** A company
coming out of stealth discloses Seed and Series A on the same day — that is a **disclosure
artifact**, not a 0-month interval, and recording it as "Fast" is noise.

---

## 6 · Crunchbase twins — how to pick, and when to leave it blank [RECOVERED]

**Match in this order:**

1. **Website domain on the Crunchbase profile === your canonical domain.** ← decides it alone
2. **Description names the same product**
3. **HQ + founded year both agree**

**Never on logo. Never on name alone.**

**The bar: a domain match, or two independent non-name signals.**

### When to leave funding blank

> **Blank when you are not certain. Always.**

**The asymmetry makes this easy:** **missing funding does NOT penalize the score** — a company
with 25 NYC people and 8 in-office roles and no funding record on file scores fine, because *heads
and jobs carry it.*

**But a twin's $50M round manufactures a growth signal that does not exist**, and a fresh
substantial raise is one of only two ways a company reaches the top tier.

> **A blank costs you nothing. A twin's number can promote a stranger to the top of your chase
> list.**

---

## 7 · LinkedIn company page [NEW]

**Click the stored `/company/{slug}` URL. Do not start from Sales Nav home and type the name** —
that is name-search, and it costs an extra page load out of the same budget.

**Read the About tab:**

| field | why |
|---|---|
| **Website** | **the identity cross-check** — must match your canonical domain |
| Headquarters | HQ is load-bearing: the stall penalty fires only for NYC-HQ companies |
| Founded | feeds the early-rocket rule |
| **Company size band** | **this is your total-employees number.** Take it here — do not spend a second Sales Nav search on it |
| Specialties | industry qualification |

---

## 8 · LinkedIn → Sales Nav [NEW — verify the path on company #1]

**Best case: you never do this more than once per company.** Store the Sales Nav account URL at
bind time and reuse it forever.

**To get it the first time, in preference order:**

**① The in-UI Sales Navigator affordance on the LinkedIn company page**, if present. Cleanest —
LinkedIn resolved the identity for you.

**② Read the numeric organization ID out of the loaded page, then navigate to
`linkedin.com/sales/company/{id}`.** This is acceptable: **reading a page you legitimately loaded
is not an internal endpoint call, and typing a Sales Nav URL is ordinary navigation.**

**③ Sales Nav account search by name — last resort, and it is a twin risk.** If you use it, §8's
identity bar applies before you bind.

**Whichever path works on company #1, use that same path for all 80** — and write down which one.
I cannot verify LinkedIn's current UI from here.

> **After navigating, verify: the Sales Nav page must show the same company name AND the same
> website.** If either differs, you are on a twin. Stop.

---

## 9 · Sales Nav — what you count [RECOVERED + the open question]

**A people search, filtered to the company and the geography. The count is in the results header.**
One search, one exact number.

**The two filters, by their UI section names** (confirmed from the captured filter panel):

| section | value |
|---|---|
| **Current company** | the company |
| **Person geography** | **← the open question below** |

**Note: `Person geography` and `Company headquarters location` are different filter sections.**
You want **Person geography** — where the humans are, not where the company is registered.

### 🔴 The geography value — settle this on company #1

```
the ruling says      New York City Metropolitan Area
JD's saved searches  New York, New York, United States
```

**Run both on company #1. Compare the counts.**

- **Same number** → they are the same entity. Record which label you used and move on.
- **Different** → **stop.** You have found that the board's 41 existing measurements and your next
  79 are on different rulers, and that is a bigger finding than the batch.

**This is also the mandated opening test, which exists independently:** session 1 opens by
**re-measuring 3–5 of the already-known 41 through the UI path.** Reproduce → the existing
measurements stay valid and you proceed. Diverge → **stop, before spending the other 49.**

**Report the pairs, not a verdict.**

### What you write down

| | |
|---|---|
| **NYC Employees** | the header count from that search |
| **Total employees** | the **About page size band from §7** — not a second search |

### "No matches" — do NOT write a zero reflexively

**A UI-read zero is `Partial`, never `Verified`.** And there is a specific trap:

> **A company that plausibly has NYC presence — NYC HQ, or NYC job postings you already found —
> showing "No matches" is internally contradictory.** Office presence is a claim a zero
> contradicts.

| situation | write |
|---|---|
| No matches, **and** no NYC HQ, no NYC roles | **`0`, marked Partial** — a plausible measured zero |
| No matches, **but** NYC HQ or NYC roles exist | **Unknown + "needs a real read."** Do not write 0 |
| Structure loaded, filters applied, result implausibly empty | **back off. Do NOT write. Do NOT re-bind.** |

---

## 10 · Which Sales Nav URL you save [NEW — and this is a real distinction]

> **Save `linkedin.com/sales/company/{id}` as the identity link. NEVER the people-search URL.**

**The people-search URL encodes the filter state.** It is a **measurement**, not an **identity**.

**Two ways it burns you:** LinkedIn's geography vocabulary changes and the saved search silently
returns a different population; and anyone re-opening it later thinks they are looking at the
company when they are looking at *one query about* the company.

**The account URL is stable and means one thing.**

**If you want the search URL, store it in a separate field as measurement provenance** — never in
the identity slot.

---

## 11 · Careers [RECOVERED]

**Yes — use the bind runbook exactly:** search the ATS domains first, then footer, then view
source, then sitemap, then token guess. `reference/careers-url-discovery-runbook.md`.

### You do NOT count the roles. The script does.

**You produce a binding — `careers_url` + `ats_provider` + `board_token`. That is the whole job.**

**Once bound, the API returns every role with its location type, posting date, seniority and role
type attached.** You cannot read those reliably by eye, and **all four are what the score actually
uses** — `Desk Jobs` is `in-office + 0.8 × hybrid`, and remote counts zero.

**Hand-counting is slower and produces a worse number.**

**The one exception:** a Notion-hosted or otherwise API-less board has no endpoint. **Flag it** —
it needs the DOM reader forever, and its zeros are capped at Partial.

---

## 12 · The website, besides the careers hunt [NEW]

| take | note |
|---|---|
| **The canonical domain after redirects** | see §18 |
| **HQ city** | cross-check against Crunchbase and LinkedIn |
| **One-line summary** | what they actually do — used for the twin check |
| **Founders** | from an About or Team page if it is one click away |

**Do NOT take headcount from the homepage.** *"We're a team of 50"* is marketing copy, not an
instrument, and it is not on the same ruler as anything else on the board.

---

## 13 · The done checklist [NEW]

**A company is done when every line is either filled or carries a dated looked-and-none note.**

```
IDENTITY
  [ ] canonical domain (post-redirect)
  [ ] linkedin /company/ URL
  [ ] sales nav /sales/company/{id}          ← the ACCOUNT url
  [ ] crunchbase URL

CAREERS  (the binding — not a count)
  [ ] careers_url
  [ ] ats_provider
  [ ] board_token
  [ ] why you believe it is this company     ← one line

MEASUREMENT
  [ ] NYC Employees        + the geography label used
  [ ] total employees      (About size band)

FUNDING
  [ ] latest round name / amount / DATE
  [ ] total raised, round count
  [ ] lead + all investors
  [ ] ROUND HISTORY: name + announced date pairs   ← the high-value one

CONTEXT
  [ ] HQ city    [ ] founded year
  [ ] industries [ ] one-line summary
```

---

## 14 · A missing field: 0, blank, or a note? [RECOVERED — this is the system's core rule]

> **Never 0. Blank, plus a dated looked-and-none note.**

**Blank alone is ambiguous** — it cannot distinguish *nobody looked* from *someone looked and
there was nothing*. **The note is what turns a blank into a fact.**

```
no careers page found · 2026-08-13 · tried: /careers /jobs /join sitemap source-scan ashby+gh tokens
```

**Three parts, all required: what, the date, what you tried.**

**Why never 0:** a missing value that scores as zero is a company penalized for your not looking.
**Unmeasured and measured-zero are different facts** and the score treats them differently — a
blank does not penalize, a zero does.

**And the note expires.** It suppresses the re-ask for ~30 days, then re-asks — because a company
with no board today opens one when it raises.

---

## 15 · Where results are written [RECOVERED]

> **SQLite first. Notion is a projection of it. One write per company, at the end of the company.**

**Not live-to-Notion field by field.** A half-enriched company written to the board gets a status
on partial evidence — and then a different status three minutes later when the rest lands.
**Status flapping is the trust failure the whole barrier design exists to prevent.**

**JD editing the board directly is a supported, different path** — reconcile *adopts* his edits
with `jd-manual` provenance and never overwrites them. **That is for corrections, not for bulk
enrichment.**

**Practical shape:** collect into a scratch record per company → write the complete company to the
store → `reconcile_sweep --apply` pushes to Notion in one pass at the end of the session.

---

## 16 · Timing [NEW]

| step | target |
|---|---|
| Website + careers bind | **90 s** (3 min hard cap) |
| Crunchbase | **60 s** |
| LinkedIn About | **30 s** |
| Sales Nav | **60 s** |
| **one company** | **~4 minutes** |

**Too slow is 8 minutes.** At 8 minutes, **stop and record what is blocking** — a missing careers
board, an ambiguous Crunchbase entry — and move on. **Grinding on one company is how a session
that should cover 35 covers 12.**

```
40 companies × 4 min ≈ 2h40m of work
80 companies        ≈ 5h20m AND at least two sessions, because of the 80-view/day cap
```

---

## 17 · Challenges, captchas, logged-out states [RECOVERED — memorize this table]

| what you see | what it is | what you do |
|---|---|---|
| **LinkedIn `/checkpoint/`, `/challenge/`, an authwall, a 401** | **an identity challenge** | **HALT THE WHOLE LANE. Do not retry. Do not refresh. Do not "try once more."** Close it, stop the session, tell JD. **Retrying into a challenge is how accounts get locked** |
| Cloudflare page, 403/503 with a challenge body | **infrastructure, not identity** | back off with jitter, resume later. **Do not wake JD** |
| Page loads logged-in, layout is different, selectors miss | **the site moved** | re-find it. **Do not back off — the site is fine** |
| **Logged in, filters applied, result implausibly empty** | **soft block — a hollow page** | **back off. DO NOT WRITE. DO NOT RE-BIND.** ← the dangerous one |
| **Crunchbase logged out / paywalled** | a limit, not a challenge | **record funding Unknown and move on.** Do **not** log in with another account, do **not** retry-loop |

> **In an attended browser lane, the operator IS the control.** Nothing in code can block a browser
> request. Everything in the system is instrumentation for your judgment — **the judgment is the
> mechanism.**

---

## 18 · Redirects and rebrands [RECOVERED — a real recorded case]

> **The redirect TARGET is the real site. Record BOTH as identity keys.**

**The recorded case:** `deeptune.ai` redirects to `deeptune.com`; `deeptune.com` links an Ashby
board **that was already in the store under a different key.** It was bound on both keys and both
were recorded.

**So before you create anything after a redirect:**

**Check whether the target domain is already bound to another row. You may be about to create a
duplicate, not discover a company.**

**And use Crunchbase for exactly this** — resolving the canonical domain after a rebrand is the one
thing Crunchbase is better at than the site itself. **Do not use its careers or contact links;
they are stale and second-hand.**

---

## 19 · A real walkthrough [HONEST ANSWER]

**There is no click-level log of a per-company enrichment run, because no such run was ever
automated.** I will not invent one.

**What IS a real recorded computer-use run on JD's Mac — the Sales Nav filter capture:**

```
opened   linkedin.com/sales/  (already logged in, existing session)
         → Saved searches
         → opened "NYC - New Target Roles - 90 days"
captured the live URL, the result count (93), and every filter section by name
         Current job title · Seniority · Years in current position
         Person geography = "New York, New York, United States"
         Company headcount = 11-50, 51-200, 201-500
         Industry (applied to PERSON, not company)
         + 27 sections recorded as present-but-empty
cost     8 page loads.  interstitials encountered: none.
wrote    reference/captures/salesnav-workplace-poc-2026-08-09.json
```

**Two things to copy from it.** It recorded **what was empty**, not only what was set — *"present
but empty"* for 27 sections is what makes the capture reproducible instead of a summary. And it
recorded **its own cost** (8 page loads) and **that nothing interstitial happened**, which is what
makes the account-risk budget real rather than estimated.

**And a real enriched company, reconstructed from its stored output** — Remark, exactly as its
page body reads today:

```
Employees 6/34  (2 NYC metro)
Jobs      0/26  (0 NYC roles, location-type unknown, 0% of team)
Growth    2/10  (Slow est.)
Stage     0/8   (2 vs ~18 expected at series-a)
HQ        6/6   (NYC-based)
Industry  5/5
Funding   4/8   ($26.3M)
Investors 1/3
                                            Fit Score 24
```

**Read what that line admits.** `2 NYC metro` — the Sales Nav count. `location-type unknown` — the
careers board was read but the in-office/hybrid/remote split was not resolved, **so `Desk Jobs`
cannot be computed and it is honestly blank rather than 0.** `Slow est.` — velocity was
**estimated, not measured**, and the `(est.)` suffix says so on the board.

> **That is what a correctly enriched company looks like: every number carries what produced it,
> and the gaps are labelled rather than filled.**

---

## 20 · What the new agents must NEVER do

**Your five, confirmed, with the reason each one is on the list:**

**① Never name-search when a stored URL exists.** 1 in 6 domains misbound on name matching, in a
measured vendor eval. **A twin produces confident numbers about a stranger and nothing downstream
can detect it.**

**② Never save the people-search URL as the Sales Nav link.** It encodes filter state. It is a
measurement, not an identity, and it rots silently when LinkedIn's vocabulary changes.

**③ Never treat a `/careers` 404 as "no jobs."** ~50% of boards are embed-only. **A false zero
suppresses 26 of 100 scoring points** and a scheduled re-check does not heal it — **it confirms
it.**

**④ Never invent a 0.** Blank plus a dated note. **Unmeasured and measured-zero are different
facts.**

**⑤ Never batch all Crunchbase then all LinkedIn.** It defeats the per-company barrier **and** it
produces exactly the uniform block of LinkedIn traffic that is the real detection risk.

**And five more, each of which has a defect behind it:**

**⑥ Never retry into a LinkedIn challenge.** Not once. Not after a refresh. **Halt.**

**⑦ Never touch voyager, an internal endpoint, or intercepted XHR.** A value only reachable that
way is **not reachable**. Record it unavailable.

**⑧ Never construct an email address.** No `first.last@domain`. **Declared or nothing** — a wrong
score is fixed on the next pass, a wrong address is sent to a stranger.

**⑨ Never take a number from marketing text.** *"Coming soon," "no open roles," "we're a team of
50"* are **claims**. Structure is the fact.

**⑩ Never bind a board or a company on the name alone.** Domain match, or two independent
non-name signals. **And write down which one you used.**

---

# THE CARD

```
ORDER (per company, never batched by site)
  website → crunchbase → linkedin → SALES NAV LAST
  ~4 min/company · stop at 8 · 30-40 companies/session · 80 views/day cap

DRIVE
  UI only. no voyager, no XHR, no CDP capture.
  4-20s between loads, VARIED. uniform pace = a slower robot.
  3 tabs, reused. Sales Nav tab pinned, never reloaded.

SALES NAV
  filters: "Current company" + "Person geography"   (NOT "Company HQ location")
  geography value: SETTLE ON COMPANY #1 — ruling says NYC Metro Area,
                   saved searches say "New York, New York, United States"
  open the session by re-measuring 3-5 known companies. diverge → STOP.
  save /sales/company/{id}  — NEVER the search URL
  "No matches" + NYC HQ or NYC roles = Unknown, NOT 0

CAREERS
  you produce: careers_url + ats_provider + board_token + why
  you do NOT count roles. the API does.

MISSING
  never 0. blank + "looked, none · DATE · what you tried"

WRITE
  SQLite first, one write per company at the end. not live to Notion.

HALT
  /checkpoint/ /challenge/ authwall 401 → STOP EVERYTHING. no retry. tell JD.
  logged-in + filters set + implausibly empty → back off, DO NOT WRITE.
```
