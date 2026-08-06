# Phase 1 lane design decisions (enrichment lanes)

Engineering rulings on the 7 dress-rehearsal hurdles, grounded in the studied
repos (scrapling · ats-scrapers · linkedin-mcp-server · gstack · linkedin_scraper ·
dlt · resilience4j · splink). These are the design contract for the browser
daemon, adapter registry, and self-healing lanes.

## Q1 — Browser identity: dedicated managed profile, NOT the daily driver

**Ruling: a dedicated, persistent, stealth-hardened browser profile, logged in
once (session-as-artifact), kept warm by the daemon, running on the user's
network. Do NOT attach to the daily-driver Chrome. Do NOT use vanilla Playwright
Chromium.**

Why the sandbox tripped and the daily driver sailed: Cloudflare trusted the daily
driver because it has a **real, aged session** (cookies, localStorage, history) —
coherence — and it distrusted the sandbox because it was (a) a fresh browser with
no session AND (b) almost certainly a vanilla automated Chromium whose automation
fingerprint is detectable. The lesson (linkedin-mcp-server, *coherence not
invisibility*): a browser that tells a consistent *true* story is trusted; a fresh
or contradictory one isn't. You get the daily driver's advantage without its
problems:

- **Dedicated persistent `user-data-dir`** (its own profile) that you log into
  Crunchbase and LinkedIn *once*, supervised (session-as-artifact — linkedin_scraper).
  It then accrues a real, aging session — coherent, not synthetic. "Synthetic" comes
  from *no history*, not from *being dedicated*.
- **Stealth runtime, not vanilla Playwright.** Use patchright (what
  linkedin-mcp-server uses) or real Chrome driven over CDP with a dedicated
  profile. Vanilla Playwright Chromium is the thing Cloudflare/LinkedIn flag.
- **Never inject a fingerprint/UA override** (linkedin-mcp): let the real browser
  tell the truth; an override that changes the UA but not the client hints is a
  *contradiction* and worse than nothing. Verify identity by measurement.
- **Warm and supervised** (gstack daemon): long-lived so the session persists
  across runs; election/lock/lease/liveness/health so one browser is shared safely.
- **On the user's machine/network** so the residential IP matches the human's real
  location (coherence). Moving to a hosted box changes the IP and breaks coherence —
  that's the availability tradeoff (W6), decide it explicitly.

The daily driver is disqualified for an unattended system regardless: contention
(the human closes a tab mid-scrape, cookies change under you) and — the real
killer — if the bot trips a challenge, it burns the human's *daily* session and
account. Isolate.

## Q2 — Careers: prefer the ATS public JSON API; DOM+self-healing only for custom

**Ruling: detect the ATS, hit its public JSON endpoint; fall back to DOM +
self-healing selectors only for genuinely custom pages. Adapters are per-ATS-type
in a registry (ats-scrapers), capability-declared — NOT per-company.**

This is deterministic-first (graphify) + the capability ladder (scrapling) +
provider-adapter registry (ats-scrapers). The ATS APIs are public, structured,
stable, auth-free, give exact location facets, and sit on firm legitimacy ground
(vs logged-in scraping):
- Greenhouse: `https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true`
- Ashby: the public posting API (`jobs.ashbyhq.com` / posting-api board endpoint)
- Lever: `https://api.lever.co/v0/postings/{company}?mode=json`
- Workday: the tenant's JSON POST endpoint (messier; adapter handles it)

**Adapter shape (ats-scrapers):** an ABC `CareersAdapter` + a registry; each
adapter declares (as data) how it *detects itself* (URL signature: `greenhouse.io`,
`ashbyhq.com`, `lever.co`, `myworkdayjobs.com`, embedded board markers) and how it
*fetches* (its endpoint). Detection routes the company to the right adapter. A
per-company override field is an escape hatch for pathological cases only — the
default is per-type detection, so a new company on a known ATS needs zero new code.
Custom/unknown pages → the DOM adapter with self-healing selectors (scrapling) and
**confidence surfaced on re-bind** (a silent partial match is a phantom fact).

**Contradiction flagged:** DOM-scraping an ATS-hosted board (your case b,
Greenhouse-in-a-custom-site) when its JSON API exists contradicts
graphify/ats-scrapers. Detect the embedded ATS and use the API even when the board
is wrapped in a custom site. Your case (d) — rebranded company, zero roles — the
API returns a clean `0`: that's a **real measured 0**, store it (Unknown≠0 does
not apply; it's genuinely zero).

## Q3 — LinkedIn NYC count: Sales Navigator geo-filtered search count

**Ruling: use Sales Navigator's geo-filtered people-search *count* as the primary
NYC-metro instrument. The public People-page top-5 "where they live" chart is a
fallback/corroboration only.**

The top-5 chart is a *fragile, incomplete* instrument — when NYC isn't top-5
(Alta), it's unreadable, and parsing a chart is exactly the brittle
displayed-value dependency linkedin-mcp warns against. The user owns Sales Nav; a
Sales Nav people search (company = X, geography = "New York City Metropolitan
Area") returns an **exact count in the header**, at any company size, for the price
of one search — the deterministic signal. It's also what the warm_path context
already uses, so **share the one Sales Nav session/profile** across both (one
login, one browser, coherent).

**Instrument consistency matters (the Q you didn't ask — see below):** pin NYC
count to Sales Nav *always*, so a re-check's delta is a real change, not an
artifact of switching instruments (chart last time, Sales Nav this time). Cache to
the freshness cadence; budget Sales Nav searches (shared with warm_path) against
the subscription's view limits.

## Q4 — Identity auto-bind bar: domain match, or two independent non-name signals

**Ruling: auto-bind a discovered profile to an entity only on (a) a website-domain
match, OR (b) two independent corroborating signals beyond the name. Otherwise →
human review.**

This is splink/Fellegi-Sunter thinking + refuse-uncertain-writes. Seven same-name
companies proves name is worthless alone; name + one weak signal (industry — every
company is "AI") is still too weak.
- **Domain match is the near-unique key** (low u-probability): if the LinkedIn page
  lists a website whose domain matches the entity's known domain, that alone binds.
- **No domain → require two independent signals:** industry + investor-overlap, or
  founder-name match + industry, or HQ-city + founder. Weight by rarity
  (term-frequency, splink): a rare founder name or a specific investor is strong; a
  common industry is weak.
- Implement as a small additive match score (domain=strong, investor-overlap or
  founder-name=medium, industry or HQ-city=weak); auto-bind above threshold, review
  below.
- **Record the bind with its evidence** (why we bound this URL) — auditable and
  reversible.

## Q5 — Multi-location job counting: keep "NYC-eligible", but split from "NYC-exact"

**Ruling: keep "counts toward NYC if NYC is any listed option," but store two
numbers — `nyc_jobs_exact` (NYC-only/primary) and `nyc_jobs_eligible` (NYC is one
of several) — exclude pure-remote, and store per-role location evidence.**

Defensibility > cleverness (your words), so make it auditable:
- NYC listed explicitly → eligible. "NYC only" / "NYC, NY" → also exact.
- Pure "Remote (US)" with no NYC → **not** NYC demand (the "Remote only — Not a
  Fit" case). "NYC OR Remote" → eligible, flagged.
- The Fit component uses `nyc_jobs_eligible` (or a blend) with a note; storing both
  lets you defend either interpretation and change your mind without re-scraping.
- **Store the location string of every counted role in the receipt** (evidence-as-
  claims, graphify provenance): "counted these 9 roles as NYC-eligible, here are
  their location strings." If JD disputes a count, the evidence is right there.

## Q6 — Rebrands & conflicts: surrogate ID + append-only alias table; contested attributes stay claims

**Ruling: model identity as a stable surrogate entity ID + an append-only
alias/identity-keys table. A rebrand is an *event* that adds the new keys as
current and keeps the old as aliases — gated on human confirm. Contested
attributes (HQ) are stored per-source as claims; the conflict is surfaced, the
derived value is Unknown, and reconcile never writes a false winner.**

- **Surrogate key forever** (brain/04: IDs opaque and stable). Identity signals
  (name, domain, LinkedIn URL, HQ) are *versioned attributes with validity*, not
  overwritten.
- **Rebrand (Anecdote→Clarity, anecdoteai.com→onclarity.com, NY→London):** not a
  new entity, not a silent rename — a `rebrand` event. Add the new keys as current;
  **retain the old keys in the alias table** so a future re-discovery via the old
  name/domain still resolves to the *same* entity (no duplicate). Because a domain
  change is high-signal-but-ambiguous, **gate the "same company?" confirmation on
  human review** before the new keys become canonical. Only treat as a *new* entity
  if continuity genuinely can't be established.
- **Contested attribute (Alta: NY on Crunchbase, Tel Aviv on LinkedIn):** HQ is not
  a single value — store **HQ-per-source as claims** with timestamps (evidence-as-
  claims, brain/10 #4). The reconcile loop does **not** pick a winner: it surfaces
  Review Required (conflicting-evidence), leaves the Fit-relevant derived field
  (is-NYC?) as **Unknown/contested** (refuse-uncertain-writes — never guess a value
  that feeds Fit), and shows Notion "HQ: conflicted (NY / Tel Aviv) — review," not a
  false single value. When JD resolves it, the winning claim becomes current.

## Q7 — Pacing budgets: LinkedIn is the riskiest; cap it hardest; breaker on first challenge

**Ruling (resilience4j rate-limiter + bulkhead + circuit-breaker, per source):**

| Source | Risk | Daily cap | Pace (per action) | Concurrency | Notes |
|---|---|---|---|---|---|
| **LinkedIn / Sales Nav** | **HIGHEST** | ~15–25 | 1 per 90–180s + jitter | **strictly 1** | working-hours only; breaker halts on first checkpoint |
| Crunchbase | medium | ~30–50 | 1 per 30–60s + jitter | 1–2 | coherence (Q1) matters more than the cap |
| Careers/ATS APIs | lowest | 100s | 1 per few s | several | public APIs — move most volume here (Q2) |

- **LinkedIn is the riskiest, unambiguously** — the downside isn't a failed check,
  it's a *restricted/banned account* that is the user's real professional identity
  and paid Sales Nav. Most conservative caps, **strict serialization** (never
  parallel), **working-hours-in-user's-TZ only** (activity at 3am is a flag), and an
  **aggressive circuit breaker**: the moment you see a LinkedIn checkpoint/challenge,
  *halt that lane immediately* and surface to the operator — do not keep hammering
  (that escalates the block and endangers the account).
- **Jitter everything:** ±40–60% on delays, **randomize company order** (never
  alphabetical/by-ID — that's a pattern), spread across the day, no bursts.
- **Daily budget = a hard cap** (autoresearch frozen-budget); exhausted → stop and
  reschedule. Cadence (7/14/30d) × budget spreads the 250-company load.
- **Bulkhead per source** so a slow/dead source can't consume the whole session.
- **Circuit breaker per source** (not just retry): retry handles a blip; the
  breaker handles a *block* — and for LinkedIn the breaker is the account-safety
  mechanism, not just a resilience nicety.

**Contradiction flagged:** if the current design is retry-only with no per-source
circuit breaker, that contradicts resilience4j and is *dangerous* specifically for
LinkedIn — retrying into a checkpoint is how accounts get restricted. Add the
breaker before scaling.

## Contradictions with the studied repos — summary
1. **DOM-scraping ATS boards** where a JSON API exists → use the API (graphify /
   ats-scrapers). [Q2]
2. **Parsing the top-5 location chart** as the NYC count → use Sales Nav's exact
   count (robust-signal, linkedin-mcp). [Q3]
3. **Attaching to the daily-driver Chrome and/or vanilla Playwright** → dedicated
   stealth profile with a real aged session (gstack daemon + linkedin-mcp
   coherence + linkedin_scraper session-as-artifact). [Q1]
4. **Auto-binding identity on name+industry** → domain or two independent signals
   (splink + refuse-uncertain-writes). [Q4]
5. **Retry-only resilience** → add per-source circuit breaker + bulkhead; mandatory
   for LinkedIn (resilience4j). [Q7]
6. **Per-company careers adapters** → per-ATS-type registry, capability-declared
   (ats-scrapers). [Q2]

## The questions you should have asked (but didn't)

**A. Instrument consistency — "am I measuring the same thing the same way every
time?"** The histories (NYC Employee/Job History) are only meaningful if the *delta
between checks is a real change, not an artifact of switching instruments*. If you
measured NYC via the top-5 chart last cycle and Sales Nav this cycle, the "change"
is noise. **Pin one instrument per metric** (Sales Nav for NYC count, the ATS API
for jobs) and record which instrument produced each value, so change-detection is
trustworthy. This is subtle and it feeds Fit — get it wrong and the board reports
phantom growth/decline.

**B. Enrichment *correctness*, not just write correctness.** You verify the *write*
(read-back) beautifully — but a wrong NYC count written verified-ly is still wrong.
Nothing yet verifies the *value*. Add the trust-boundary layer (guardrails/evidence-
clamp + evidently): (i) **capture the raw evidence** every number came from (the
count string, the screenshot/DOM snippet), so any value is auditable; (ii)
**cross-check across sources** where possible (jobs from the ATS API vs the page);
(iii) **drift-flag** implausible jumps — an NYC count that goes 15→150 between
checks should route to review, not silently overwrite. Verified-write guarantees
you wrote what you meant; it does not guarantee what you meant is true.

**C. The "what do I check today?" selector is a priority queue, not a loop.** When
the backlog of due-for-recheck companies exceeds the daily budget (inevitable at
250 companies × 7/14/30-day cadences), *who gets checked first?* Answer: a priority
queue — Prospects/Top Pursuits get their recheck budget before Watchlist (tiered
cadence, brain/10 #9). Design the daily selection as "highest-value due work within
budget," not FIFO, or your hottest companies go stale while the budget is spent on
cold ones.

**D. The strategic one — the legitimacy/account-risk decision is now due.** You're
about to scale the enrichment on logged-in LinkedIn/Crunchbase scraping, and Q7
establishes LinkedIn as the lane that can *burn the user's real account*. The ATS-
API move (Q2) de-risks careers, but LinkedIn/Crunchbase remain exposed. This is the
compliant-data hard problem (ats-scrapers legitimacy ceiling), and enrichment is
exactly where it bites. The question to put to JD *before* scaling the riskiest
lane: **do we move NYC-headcount to a compliant data source (a LinkedIn-data
provider, or an API) rather than logged-in Sales Nav scraping, given the account is
his real professional identity?** It's a business call, but it's due now, not later.
