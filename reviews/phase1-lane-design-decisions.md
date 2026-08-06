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

---

# Follow-up rulings (round 2)

Four sharper questions on the enrichment lanes. These refine — not replace — the
rulings above.

## F1 — Sales Nav count fidelity: name the proxy, don't chase the truth

**Ruling: apply exactly two filters and pin them forever — `current company =
target` + `geography = NYC metro`. Filter nothing else.** Do not try to exclude
contractors, advisors, or stale profiles: LinkedIn gives you no reliable, locale-
independent facet for "employee vs contractor," and any heuristic you invent will be
applied inconsistently across 250 companies — which destroys comparability, the one
property the number exists to provide.

The deeper move is to **stop pretending the metric is "true NYC employees."** It
isn't, and it can't be. What you are actually measuring is *"LinkedIn members in the
NYC metro who list this company as their current employer."* Name the field that
honestly — `LinkedIn NYC Metro Count`, not `NYC Employees` — and store the exact
filter definition alongside the value as provenance (brain/10 #6: a number without
its definition is a lie waiting to happen). Then **calibrate Fit against the proxy,
not against ground truth.** The scorer never needed the true headcount; it needed a
*consistent, comparable* signal of NYC presence and growth. A consistent proxy beats
an inconsistent truth every time.

On the gap between the LinkedIn count and true employment: annotate the field as a
**lagging, upward-biased** proxy. Upward-biased because departed employees leave
stale "current company" entries for months (people update LinkedIn late); lagging
because it reflects the workforce of weeks-to-months ago, not today. Two consequences
you exploit rather than fight: (i) a *sudden drop* in the count is a high-confidence
signal — people rarely remove a current employer unless something real happened
(layoff, shutdown, mass departure), so a drop is worth routing to review; (ii) the
upward bias means the count is a **ceiling, not a floor** — treat "count is high" as
weak evidence and "count dropped" as strong evidence. Store the count history
(brain/10 #8, change surface) so the *delta* is available to the scorer, because the
delta is more trustworthy than the level.

## F2 — Aging the dedicated profile: inherit trust, prove it behaviorally

**Ruling: the dedicated profile inherits its trust from JD's real, aged account —
it is not aged from zero.** If the dedicated automation runs on a *separate* new
account, you have the worst of both worlds: a cold account (instantly suspicious to
LinkedIn) that is *also* linked by behavior to JD's real one. So the warm-up protocol
is really a *trust-transfer and ramp* protocol, not a "grow a new identity" protocol.

The ramp, keyed to **clean-day tiers, not a fixed clock:**
- **Day 0 — supervised manual login, zero automation.** JD logs in by hand, on the
  same device/session that will run the automation, and browses normally for 20–30
  minutes (session-as-artifact, linkedin_scraper). No scripted action touches the
  account this day. You are establishing a warm, human-origin session the automation
  will later borrow.
- **Days 1–3 — ~25–33% of target budget** (LinkedIn ≈ 5–8 profile/count views per
  day), human-paced (jitter, business hours only), circuit breaker armed to halt on
  the *first* challenge.
- **Days 4–7 — ~50–66% budget**, *only if* the prior tier ran with zero friction
  (no checkpoints, no interstitials, no empty-result anomalies).
- **Day 7+ — full budget**, again only on a clean record.

"Aged enough" is **behavioral, not temporal.** The gate to each next tier is "N
consecutive clean days at the current tier," where *clean* is defined by the breaker
never tripping and the enrichment-plausibility layer never flagging. A profile that
hits a checkpoint on day 5 does not advance on day 8 — it resets to the prior tier.
The circuit breaker (F3) is the sensor that decides "clean"; there is no separate
"aged" flag to invent. And login stays **supervised forever** — you never script the
credential entry or the challenge response; the automation borrows an
already-authenticated human session, it does not authenticate. That single rule is
what keeps this on the right side of the account-safety line.

## F3 — Breaker trigger taxonomy: classify on structure, never on displayed text

**Ruling: the breaker classifies on machine-observable signals — HTTP status,
response headers, final URL, and DOM *structure presence* — and NEVER on the
human-readable text of the page.** Text is localized, A/B-tested, and reworded
constantly; a taxonomy built on strings like "unusual activity" breaks the first time
LinkedIn ships a new locale or copy test. The decision tree:

| # | Signature (machine-observable) | Meaning | Action |
|---|---|---|---|
| a | Final URL contains `/checkpoint/` or `/challenge/`, or an authwall redirect, or `401` | **LinkedIn identity challenge** — the account is being asked to prove itself | **HALT-AND-ALERT.** Stop the lane immediately, do not retry, page JD. Retrying *into* a challenge is exactly how accounts get locked. |
| b | `cf-ray` / `cf-mitigated` response header present, or `403`/`503` with a challenge body structure | **Cloudflare / edge interstitial** — infrastructure, not identity | **HALT-AND-BACKOFF.** Exponential backoff with jitter; resume later. Not an account signal, so no page — but no hammering either. |
| c | `200` + authenticated shell present (nav/header DOM confirms you're logged in) + the *expected result structure is MISSING* | **Selector break / layout change** — you're in, the page just moved | **SELF-HEAL RE-BIND** (scrapling pattern): attempt the resilient re-selection; if it fails, flag for human selector review. Do NOT back off — the site is fine. |
| d | `200` + authenticated shell present + expected structure *PRESENT* + result is implausibly empty (e.g. a company that had 40 shows 0) | **Soft-block or throttle** — they're serving you a hollow page | **BACK OFF, DO NOT WRITE, DO NOT RE-BIND.** This is the dangerous one. |

The two discriminations that matter most:
- **(c) vs (d): "is the expected structure present?"** If the results container/
  selector exists but is empty, it is *not* a selector break — re-binding does
  nothing and wastes a rebind budget. If the container is *gone*, it's a layout
  change. This single check ("structure present but empty" vs "structure absent")
  is what stops you from misclassifying a soft-block as a selector break and
  "keep hammering" — the exact failure you named.
- **(d) vs a real zero:** a genuinely empty result (a tiny company really does have
  0 NYC members) is indistinguishable *at the page level* from a soft-block. You
  resolve it *above* the breaker, in the enrichment-plausibility layer (ruling B
  above): cross-source corroboration + historical continuity. A `0` that contradicts
  a prior non-zero count, or that a second source contradicts, is treated as a
  soft-block (back off, don't write); a `0` consistent with history and corroborated
  is a real zero. The breaker never writes on (d); the plausibility layer decides
  whether a clean `0` is trustworthy.

## F4 — The news lane instrument: citation-by-construction, LLM as interpreter only

**Ruling: the pinned instrument is a set of deterministic feeds where every item
*arrives with* its source URL — not an LLM that you ask "what's the news?"** The
evidence discipline (brain/10 #2, research evidence-clamp) is non-negotiable here:
every claim Norman writes must carry a source URL, and the only way to *guarantee*
that is to make the URL a structural property of the input, not something the model
is asked to remember to include.

The instrument, in order of trust:
- **Crunchbase** for funding / M&A / round events — you already have it, it's
  structured, each event carries its own record. This is the spine of the news lane.
- **Google News RSS** (`https://news.google.com/rss/search?q="Company+Name"`) or a
  news API for everything else. RSS is deterministic, free, and every `<item>`
  carries a `<link>` — citation by construction. Pin the feed set so the *instrument*
  is consistent run to run (you compare companies on the same news surface, same
  reasoning as F1's pinned filters).

The LLM (Perplexity, Grok, whatever) is an **interpretation layer over cited inputs,
never a fact source.** It takes the feed items (each with a URL) and answers "does
any of this indicate an office move / expansion / leadership change?" — and its
output is **clamped to cite one of the input URLs per claim** (guardrails output
guard; no URL → the claim is dropped, not written). Perplexity is acceptable *as an
additional discovery feed* only if you enforce and store its citations the same way;
its native citations are inputs to be verified, not trusted outputs. Never let the
model assert a fact it can't tie to a fed URL — an uncited "they're expanding" is
exactly the fabricated-evidence failure the trust boundary exists to prevent.

Three mechanical rules that make the lane safe: **recency filter** every feed to the
cadence window (you don't want a 2019 article scored as a fresh signal); **dedup on
seen URLs** so the same story across three feeds is one piece of evidence, not three;
and **no URL, no angle** — an interpretation with no citable input is discarded at
the guard, never written to the board.
