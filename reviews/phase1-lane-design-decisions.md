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

---

# Follow-up rulings (round 3)

Field-tested against batch-2 (20 companies × 3 sources, 55 checks, hand-driven, zero
challenges, all writes verified). These are refinements the real data forced, plus
two genuinely new states. The priority-queue and per-company-interleave behaviors
*emerged* under the existing rulings — good evidence the rulings are load-bearing.

## G1 — The ATS roster is open by design; client-side rendering *means* there's an endpoint

**Ruling: the adapter count is not 4 — it's open-ended, and that is the whole point
of the provider registry (ats-scrapers, A5).** Encountering Gem and Dover outside the
Greenhouse/Ashby/Lever/Workday set is not a gap in the ruling; it's the registry
doing its job — each new ATS is one more registered adapter behind the same
interface. Don't hardcode a roster; hardcode the *interface* and let the roster grow.

On "no obvious public JSON API": **a client-side-rendered board is proof a JSON
endpoint exists — the browser is calling one via XHR to paint the page.** Gem
renders client-side, so `jobs.gem.com/casap` is fetching JSON from some
`api.gem.com/...`-shaped URL; Dover's iframe `src` is a page that itself calls an
API. The discovery move is: open the board once in the browser daemon, watch the
network tab, and capture the XHR the app fires. Prefer that captured endpoint (it's
the same data the page renders, structured, and it's stable within a provider). Only
if there is genuinely no callable endpoint does the adapter fall back to a **DOM
adapter behind the same registry interface** — the caller never knows the difference.
So: **probe for the XHR endpoint first (always present for a CSR board), DOM adapter
as the documented fallback**, both registered as `provider=gem` / `provider=dover`
with a `bound_via` note recording which path won. This is scrapling's "find the
resilient handle" applied to APIs, not just selectors.

**Board-pending is a real third state — add it.** Brandlight (office cities listed,
zero postings, "coming soon" board) is *not* a measured-0 and *not* Unknown. It is
**evidence of hiring intent without measurable volume** — they stood up a board and
declared office locations, which is a weak *positive* signal, the opposite of a true
zero. Three distinct states, never collapsed (Unknown≠0 extended):
- `measured-0` — board found, readable, genuinely zero open roles (a real, scored
  data point: they're not hiring right now).
- `board-pending` — board found but unpopulated / "coming soon" (intent present,
  volume unmeasurable; score as a weak-positive/Unknown-volume, **not** 0; set a
  **short recheck cadence** because a coming-soon board flips to populated fast).
- `Unknown` — no board found or unreadable (no evidence either way).
Collapsing board-pending into measured-0 would score an *about-to-hire* company as a
*not-hiring* one — a false negative on exactly the signal Norman exists to catch.

## G2 — Confirm the two-phase careers lane: browser discovers once, API counts forever

**Ruling: confirmed, and the ~30% static hit-rate is the proof.** The careers link
and ATS embed live in the JS-rendered DOM on ~70% of homepages, so **discovery is a
rendered-browser problem**; but once you've bound the company to `(provider, board
token/endpoint)`, **counting is a cheap deterministic API call** that never needs the
browser again. The lane is explicitly two-phase:
- **Bind (expensive, rare):** browser daemon renders the homepage → finds the careers
  link → identifies the ATS → captures the endpoint/token. Runs **once per company**,
  re-runs *only* on a self-heal trigger (careers URL 404s, ATS changes, endpoint
  shape breaks). Store the binding with `bound_at` + `bound_via` provenance.
- **Count (cheap, recurring):** hit the cached endpoint on cadence. No browser, no
  account-risk surface, no selector fragility.

This is the highest-leverage shape in the whole careers lane: it moves the *recurring*
cost and the *fragility* into a once-per-company step, so the daily budget spends API
calls, not browser sessions. It's the same split as F2 (discovery carries the browser
cost; the recurring path is deterministic) and scrapling's bind-then-reuse. A binding
that fails to count re-enters *bind*, not *count* — a 404 on the cached endpoint is a
re-discovery trigger, not a measured-0 (don't confuse "my cached handle broke" with
"they have no jobs" — that's the G1/F3 structure-present-vs-absent check again).

## G3 — Velocity: collapse same-disclosure-window rounds; the pattern is its own signal

**Ruling: the ≤7-day merge rule is sound — adopt it, with three refinements.**
Announcement date ≠ event date, and out-of-stealth companies disclose multiple rounds
on one day (Artemis: Seed $15M + Series A $55M, same date → seed→A = 0.0 months =
"Fast," which is semantically noise). The metric requires **two independently dated
events separated by a real interval**; when the interval is a disclosure artifact,
suppress the velocity computation. Refinements:
1. **Make the window a tunable constant, not a literal.** `SAME_DISCLOSURE_WINDOW =
   7d` as config, validated at boot (config-schema invariant). I'd lean 7–14 days —
   a stealth reveal sometimes spreads across two press hits a week apart — but pin it
   as one number and let it move with evidence, don't hardcode `7` in the scorer.
2. **Don't discard the event — re-label it.** Rounds inside the window collapse to one
   *disclosure event* tagged `announced-together (out-of-stealth)`. That pattern is
   **itself a signal** (simultaneous seed+A + stealth exit often means well-capitalized
   and hot) — so it's not "no signal," it's "not a *velocity* signal; it's a
   stealth-reveal signal." Preserve it as evidence; just don't let it drive velocity.
3. **Fall back to the founded-anchor estimate, marked provisional** (→ G4). Overall
   velocity for a collapsed-round company is founded→first-real-round, flagged
   provisional, never presented as a measured seed→A interval.

## G4 — Provisional velocity must be visually AND sortably distinct (the leaderboard consumes it)

**Ruling: yes — and this is the most important round-3 fix, because a ranking is
consuming the field.** A founded-anchor / single-dated-round estimate that renders as
the same `Fast`/`Slow` select as a two-dated-rounds measurement is **inferred data
masquerading as measured** (graphify extracted/inferred/ambiguous, brain/10 #2 / D2) —
and when the leaderboard *sorts* on it, a guess can outrank a measurement. That's the
failure mode the evidence-confidence discipline exists to prevent, surfaced in the UI.

Don't over-correct by hiding the estimate (it carries real information); make the
*confidence* legible and keep it out of the measured tier:
- **Display distinctly:** `Fast (est.)` / a `(prov)` variant / muted styling —
  never identical to a measured tag. The operator must tell "measured Fast" from
  "estimated Fast" **at a glance** (operator-clarity mandate).
- **Sort in a separate tier:** the leaderboard ranks *measured* velocities first;
  provisional ones sort into a clearly-separated lower/greyed tier, or are excluded
  from the primary sort. A provisional value may **never rank above a measured value
  as if equally trustworthy.**
- **Promote on evidence:** the moment a second independently-dated round lands, the
  tag graduates from provisional to measured and re-enters the primary sort. Store
  `velocity_basis ∈ {measured, founded-anchor, collapsed-rounds}` so the display and
  the sort both read from provenance, not a boolean.

## G5 — LinkedIn geo-chart is a ~20%-lossy fallback instrument; tag every value with instrument + granularity

**Ruling: confirmed, and now quantified — the top-5 geo chart failed on 3/15 (20%),
which is precisely why the Sales Nav pinned-instrument lane (F1) is necessary, not
optional.** Two failure shapes, both recorded, neither silently coerced:
- **NYC not in top-5** (Astelia, Bolto): the instrument literally cannot read the
  value → record `Unknown (instrument: geo-chart-top5, NYC-not-shown)`, **not 0**.
- **City-granularity only** (Bold Security: "New York, New York: 3", metro not shown):
  city is *narrower* than metro (metro includes NJ/CT/Westchester/LI), so a city count
  is a **floor**, not the metro figure. Record `3 (instrument: geo-chart-city,
  granularity: city, is-floor: true)`.
The rule from F1 holds and is reinforced: **store the instrument and granularity with
every value; never compare across instruments.** The scorer treats `geo-chart-top5`,
`geo-chart-city`, and (future) `sales-nav-filter` as different measurement devices —
comparable within a device, not across. When the Sales Nav lane lands, **the ~20% the
geo-chart couldn't read are the highest-value backfill re-checks** (they're currently
Unknown on the very field that drives Fit).

## G6 — Capture redirect-observed aliases opportunistically — but only same-entity renames

**Ruling: yes, record aliases opportunistically on any check — this is identity
reconciliation for free, with one guard.** When a canonical URL 301/302-redirects
during a check (Bolto's Crunchbase slug `onnix`; LinkedIn `aryaworks→aryahealth`,
`numeric-id→join-blossom-health`), the redirect *is* evidence of a slug rename, and
you already followed it — capturing it costs nothing and prevents a future
duplicate-entity (identity-before-write invariant, brain/04). Record `(observed_alias
→ canonical, source, observed_at)` **idempotently** (skip if the alias already
exists). This is level-triggered identity reconciliation (controller-runtime): the
world drifted, the check observed it, the alias table converges — no separate crawl.

**The one guard — distinguish a rename from an acquisition.** A slug redirect that
still resolves to the *same* canonical entity (same domain root / same Crunchbase org
id) is a **rename → auto-capture**. A redirect that lands on a *different* company
(acquired-into, merged) is **not an alias** — auto-merging two distinct entities is a
high-bar, human-owned decision (the identity auto-bind bar from the earlier rulings).
So: **auto-capture same-entity slug aliases; route cross-entity redirects to review,
never auto-merge.** The discriminator is "does the redirect target share the entity's
existing identity keys?" — if yes, converge; if no, flag.

## G7 — Interleave-by-company is the recommended execution order — because it paces the risky lane for free

**Ruling: yes, interleave-by-company, not batch-by-source — and the pace data proves
why.** Batching all LinkedIn checks back-to-back clusters the account-risk requests
into a dense burst, the exact pattern that trips challenges. Interleaving sources
*within* a company means every LinkedIn hit is separated by a Crunchbase + a careers
check — which spaced LinkedIn to ~2–3 min effective cadence **with no artificial
sleep**: the gap is filled with real work, not an idle timer. That's a rate-limiter/
bulkhead behavior *emerging from execution order* (resilience4j), and it's why 55
checks ran clean in 75 minutes.

Two things to encode so it doesn't rely on luck:
- **Per-company is also the atomicity unit.** All-or-nothing per company, one receipt
  per company, one company fully enriched before the next — interleave-by-company
  aligns the execution order with the transactional boundary (all-or-nothing lanes).
  This is a second, independent reason to prefer it.
- **The rate-limiter is the floor; interleaving is the cheap spacer — keep both.**
  Interleaving spaces LinkedIn *for free when a company has other sources to check*,
  but a company with **only** a LinkedIn check has nothing to interleave against. So
  the LinkedIn lane still carries a hard `min-interval` rate-limiter set to the
  observed-safe spacing (~2–3 min); interleaving is the default order that usually
  satisfies it at zero idle cost, the rate-limiter guarantees it when interleaving
  can't. Don't rely on interleaving *alone* — it degrades exactly when a company is
  LinkedIn-only, which is the case you least want unpaced.

---

# Follow-up rulings (round 4)

Requested before batch 3, after a big interactive stretch that locked most of the
operator surface (Fit scorer v1 harness-first, 18→14 status vocabulary, operator-
surface redesign; 25 live/scored/routed, 135 invariants passing). Two things to
affirm before the rulings, because they're evidence the discipline is holding:
**the scorer was pulled forward from Phase 2 but stayed harness-first** (eval before
scorer, brain/09 / justhireme) — jumping the phase *number* is fine because the
*invariant* held; and **H2 (readback caught "Fintech" silently binding to legacy
"FinTech") is the verified-writes invariant paying out on live data** — that's the
failure it exists to catch, caught. Keep both.

The through-line of this whole round: **hysteresis is not a score feature, it's a
router property**, and **a display merge is only safe if the machine keeps the finer
reason in a structured field.** Most of Q1–Q5 are those two ideas applied.

## J1 — Evidence-hysteresis: entering a band needs full evidence; holding tolerates one absence

**Ruling: yes — mirror score-hysteresis with evidence-hysteresis, and the
asymmetry is the point.** Promotion and demotion already have different *score* bars
(60 to enter Prospect, 57 to hold). Give them different *evidence* bars too:
- **ENTER a band requires full NYC evidence** (both components measured). You never
  promote a company into Prospect — a high-consequence write that lands on JD's
  action queue — on incomplete evidence. Entering at exactly 60 with `heads=Unknown`
  does **not** enter.
- **HOLD a band tolerates one *absent* component** (evidence-hysteresis). Demoting a
  company you already believe in because a measurement is merely *missing* is the
  false-negative the whole system is built to avoid. Astelia holding Prospect at 60
  with `jobs=0 measured` + `heads=Unknown` → **holds** (one real signal present, one
  absent).

The load-bearing distinction is **absent vs contradicting.** A *measured* low/zero is
evidence and can route a company *down* (the Low-NYC exit); an *Unknown* is absence
and may **block a promotion but must never cause a demotion.** So: both NYC
components *measured-low* → route down (real evidence); one *measured*, one *Unknown*
→ hold; both *Unknown* → not a hold, route to pending/review (you're flying blind, so
say so rather than silently holding). "Missing evidence never demotes; it only blocks
promotion and, when total, forces a review" — that's the rule.

## J2 — Sequencing: reconcile BEFORE batch 3

**Ruling: build the reconcile loop next, before batch 3.** Batch 3's *load* is
safe in isolation (creating 20 fresh pages clobbers nothing) — but that's not the
real question. H6 shows the input surface is now live *in JD's head*: he's asking
"if I paste a careers link, how does the system know?", which means he will start
editing the board now. The moment he edits an existing page and any full-projection
write fires, the machine **silently reverts an operator edit** — and for an
operator-*trust* product, silently undoing the operator's action is the single most
destructive failure there is (worse than any delay). Reasons reconcile wins the next
slice:
1. The clobber risk is **no longer hypothetical** (H6), and loading 20 more pages
   just *widens* the surface where it can happen.
2. The **change-log table just landed** — the substrate reconcile needs is already
   there. Reconcile is the natural next slice; batch 3 adds volume but no new
   *capability*.
3. Reconcile is a **prerequisite for J4** (honoring JD's Tracking placements) — the
   router can't respect a JD edit it never read.

**Escape hatch (pragmatic honesty):** if batch 3 must run first for some reason, it
is acceptable **only if** the loader is *proven append-only* (creates fresh pages,
zero writes to any existing page) **and** the recurring full-projection writer stays
disabled until reconcile lands. Append-only creation is safe; re-writing live pages
is not, until read-board-first + adopt-JD-edits exists. Default: reconcile first.

## J3 — Exit-shelf flapping: hysteresis is the damper, cadence is not

**Ruling: give the exit shelf a threshold *gap*, not a single boundary — cold
cadence alone does not damp, it just slows the oscillation.** A company sitting at
the `heads=5/6` boundary rechecked monthly will flap *monthly*; cadence changes how
*often* it flaps, never *whether*. Damping requires either a threshold gap
(hysteresis) or a dwell requirement. Prefer hysteresis — it's stateless and it's the
tool you already use for score:
- **Exit to Low NYC at `heads ≤ 4`; return to Tracking at `heads ≥ 7`** (numbers
  illustrative); `5–6` is a **hold zone** where the current state persists. Same shape
  as the 57/60 score band.
- **Reserve dwell time (N confirming checks) for high-consequence exits only** — e.g.
  routing to Do Not Pursue — where a single confirming check isn't enough to justify
  the cost of being wrong. Don't spend the extra state (a pending-transition counter)
  on routine boundary shelving; a threshold gap covers that for free.

Generalize it: **every band boundary a recurring recheck crosses needs asymmetric
thresholds**, because single boundary + repeated measurement = guaranteed flap. Make
hysteresis a *property of the router*, not a special case bolted onto the score.

## J4 — Tracking handover: no new router rule; the guard is in reconcile, and it's "never silently revert"

**Ruling: a JD hand-placement into Tracking is a *JD placement* and already wins by
the router's existing precedence (`JD placement > score bands`) — the missing piece
is not a router rule, it's reconcile.** Today the router overwrites JD's Tracking
placement on rescore only because, without reconcile reading the board, **it doesn't
know JD placed it** — it sees a machine-owned band and re-derives. So:
- Reconcile reads the board, detects the JD edit, and **tags it JD-sourced with
  provenance.** Now the router sees a *placement*, not a machine state, and honors it.
- On a later rescore that disagrees, the machine **never silently overwrites** — it
  pins to JD's placement and **surfaces the disagreement** in the Changes column
  ("machine scores this Prospect; you have it in Tracking"), or routes a light review.
  JD resolves once; the machine annotates, it doesn't revert.

This is the same invariant as J2 (never silently revert an operator action) and it's
why J4 *depends on* J2's reconcile. No heavy pinning system — just: read the edit,
tag it, honor it, show the delta.

## J5 — The merges are good at the status layer, but each needs a structured reason enum

**Ruling: collapsing 18→14 is right for the operator (fewer statuses = a clearer
board), but a merge is only safe if the machine keeps the finer distinction in a
*structured, queryable* field — not free-text notes.** The operator sees the merged
business state; the machine keeps the operational reason (brain/10 #7: operational
vocabulary is separate from business state). Test each merge by "is there an
automation that would branch on the lost distinction?" — and two of them fail it:
- **Bad Data vs Needs Review** have **different owners and next-actions** (Bad Data =
  machine retries when the source recovers; Needs Review = JD decides) — which by
  JD's own merge rule ("same owner + same cadence + same next-action") argues they
  shouldn't fully merge. Keep the *status* merged, but **`review_reason` must be a
  structured enum** (`source-failed`, `ambiguous-evidence`, `conflicting-source`…) so
  the machine can auto-retry the source-failed ones and hold the human-needed ones.
  If that reason is currently free-text, structure it **before batch 3**.
- **Big Tech vs Do Not Pursue** differ on **write-authority**: Big Tech is a
  *machine* evidence-exit (re-derivable every check — the machine may lift it if the
  company shrinks below the bar); "repped already / CBRE conflict" is a *human/
  relationship* exit (the machine must **never** auto-clear it). Merge the status, but
  store `exclusion_reason` structured **and typed by owner** (machine-exit vs
  human-exit), so the reconciler knows which exclusions it may re-evaluate and which
  are sacred.

Net: keep the merges; promote every merged status's reason from prose to a structured
enum tagged with its owner. That preserves operator clarity *and* the machine's
ability to take the right next action.

## J6 — Industry taxonomy: split it — ordering to config, regexes to code

**Ruling: it's not one thing, it's two, and they have different homes.** (1) The
**priority ORDER** (which vertical wins when several match — the exact thing H3's bugs
were about: Web3/HR > Fintech) is *domain judgment JD holds and an engineer doesn't*
→ move it to **validated config**, a boot-checked ordered list JD can reorder without
an engineer. (2) The **regex matchers** (does this company read as Fintech at all)
are code, and H3 proved they need **adversarial ordering tests from real data** →
keep them in code with those tests. Config holds the *ordering and vocabulary*; code
holds the *matching and the test suite* — exactly mirroring the Fit formula (config =
tunable bands/weights, code = the pure function). The taxonomy being the lone tunable
living in code is a small consistency smell; splitting it removes the smell *and*
gives JD the one knob he'll actually want. The adversarial tests are the real safety
mechanism and travel with the regexes regardless of where the ordering lives.

## J7 — Most likely latent bug: (a) partial-evidence routing. Cheapest catch: a pure-scorer replay audit

**Ruling: rank them (a) > (b) > (c) by *latency*, and fix-readiness inverts it.**
- **(b) clobbering JD edits** is the highest *consequence* but it is **not latent** —
  it's *named* (H6) and time-gated (bites only on JD-edit + projection-write), and
  J2 closes it by sequencing. Dangerous, but on the radar and scheduled.
- **(c) select-option drift** is real (H1/H2) but **already defended** — verified
  readback is the detector, and it *worked*. Least latent.
- **(a) partial-evidence routing is the true latent bug**: it's **live, silent, and
  in the routing core** right now. Astelia-at-60-with-`heads=Unknown` is *already*
  holding Prospect on partial evidence; if J1's line is even slightly off, companies
  are mis-routed today and the 60 "looks valid," so nobody sees it.

**Cheapest catch — a pure-scorer replay audit** (you can do this today because the
scorer is a pure function over stored evidence): list every live company whose
current band was entered or held with any NYC component `= Unknown`, and for each,
re-run the scorer three ways — (i) as-is, (ii) missing component forced to its
*worst plausible* value, (iii) forced to its *best plausible* value — and show where
the band *changes*. Any company whose band flips between (ii) and (iii) is routed on
evidence it doesn't have. That one query surfaces exactly Astelia/Cluely/Camp as a
reviewable list, costs nothing (no new instrumentation), and doubles as the
**validation of J1** against live data before you commit the rule. Run it before
batch 3.

## J8 — Operator surface vs the studied repos: aligned, with one correction and one obligation

**Ruling: the surface is well-aligned — the anti-default judgment is notably good —
with one real correction and one thing the select-heavy choice *obligates*.**
- **rendergit dual-reader (E4): aligned.** Selects/tags are both human-skimmable and
  machine-parseable; the change-log is a structured episodic record that also renders
  readable; detail-in-page-body is progressive disclosure. Skim the board, drill the
  page — that's dual-reader done right.
- **ui-ux anti-defaults (C6/E4): aligned, and good.** "Short over long," one-word
  selects, and especially **removing "Needs Sales Nav count" from JD's Action Needed
  because it was asking JD to do the machine's work** — that's textbook detect-then-
  ask / anti-default. Action Needed being *strictly Joe's queue* is the correct
  ownership boundary made visible.
- **brain/10 #11 score-vs-state legibility: one correction.** Pushing detail to the
  page body is right for *rich* detail (the review question + resolution options) but
  the **one-line triage reason must stay on the board.** rendergit's dual-reader is
  *skim THEN drill* — the skim layer has to carry enough to *triage without opening*.
  For a 250-row board, a "Needs Review" with no on-board reason forces a click per
  company, which breaks the "act without re-checking" mandate (the product is *ranked
  trust*). Keep the **reason** on the board (in Action Needed or a short tag); push the
  **options** to the body. The Changes split already gets this right (delta tags on
  the board = triage; full change-log = drill) — apply the same split to review.
- **The obligation:** a select/tag-heavy board *bakes in* the H1/H2 failure modes
  (recolor-requires-rebuild, case-collision-binds-silently). That's not a design
  contradiction — it's the operational cost of a sound choice — but it means the
  **scripted select-migration playbook (H1) and case-normalization-on-write (H2) are
  now load-bearing infrastructure, not nice-to-haves.** The design is fine; it
  *obligates* those two mechanizations. Build them as owned pieces of reconcile.

---

# Follow-up rulings (round 4, addendum 2)

Two operator-caught data misses (both fixed) plus an instrument decision, from JD
using the live board hard before batch 3. The finding that frames the whole
addendum: **JD has now out-measured the machine's conservatism twice the same way**
(Cluely and Alta — both "NYC not in the top-5 chart → machine recorded Unknown → JD
got the real count in one click"). That is not two anecdotes; it's a **calibration
result** — the geo-chart's failures systematically cost real signal, and the operator
keeps paying to patch it by hand. K3 is the structural fix for exactly that pattern.

## K1 — Render protocol: ratify, and strengthen along the structure-not-text line

**Ruling: ratify all three, and recognize this as the careers-lane version of the
breaker taxonomy's core rule (F3): classify on *structure*, never on displayed
text.** Brandlight failed three reinforcing ways — didn't scroll (missed lazy-loaded
listings), anchored on the first section match (took the hero, not the real board),
and read "Coming soon!" as evidence of zero (text-as-evidence). Each is a named
anti-pattern; strengthen the protocol so none can recur:
- **Scroll-triggered settle, not a timer.** Listings load *on scroll*, so
  network-idle-on-a-clock isn't enough: scroll to bottom, wait until new DOM nodes
  *stop appearing*, then extract. Time-based settle would repeat the miss.
- **Scan the whole document for role-structures; never anchor on the first heading.**
  First-match extraction is the same fragility family as H3's first-match-wins
  taxonomy bug. Count *all* role-structures across the full rendered page and take the
  union, not the first section.
- **"Coming soon" / "no open roles" are CLAIMS, not evidence.** A zero requires *zero
  role-structures across the entire settled page*, corroborated — never a string.
  Same discipline as F3: a page's words are localized/marketing; its structure is the
  fact.
- **Add the internal-contradiction check (the G-series plausibility layer).** A page
  that *lists office cities* ("NYC · London · TLV · Madrid") but extracts *zero roles*
  is internally contradictory — office cities are a claim of presence that a zero
  contradicts. That contradiction routes to "needs a real read," not to a confident
  zero. The hero asserting NYC while the extractor says 0-NYC *is* the drift signal.
- **Name the systemic trap:** a deterministic reader bug re-runs identically forever
  — "same reader, same bug." A scheduled recheck does **not** self-heal a false zero;
  only a fixed reader or an independent corroboration gate (K2) breaks the loop.

## K2 — Cap DOM-adapter zero/pending at Partial until *independently* corroborated

**Ruling: yes — and the asymmetry is the whole point. A DOM zero is Partial; a DOM
positive with role-level evidence is Verified.** Verified-write confirms you *wrote
what you meant*, not that *what you meant is true* (the F/G distinction) — and a
DOM-extracted zero, on a page with no ATS API, is exactly where "what you meant" is
most likely wrong (lazy-load traps, text-as-evidence, first-match). So:
- A **zero or board-pending** conclusion from a DOM adapter is capped at
  `Data Status = Partial`, never Verified, until an **independent** corroboration.
- A **positive count with role-level evidence** (Brandlight → 3 actual roles
  extracted) may be **Verified immediately** — presence of 3 named roles is
  self-corroborating in a way absence never is. Absence of evidence isn't evidence.
- **Independent, not merely repeated.** "Two consecutive checks agree" only counts if
  the second check is a *different instrument, cross-source, or a fixed reader* — two
  runs of the *same buggy reader* agreeing proves nothing (the scheduled recheck
  would have "confirmed" Brandlight's false zero). The corroboration must come from a
  different signal, or the cap doesn't lift.
This mechanizes Unknown≠0 at the Data-Status layer: the board visibly distinguishes
"measured, corroborated zero" from "one reader said zero, unconfirmed."

## K3 — Ratify: pin Sales Nav geo-search as THE NYC-headcount instrument for every company

**Ruling: confirmed — Sales Nav geo-search is the primary NYC-headcount ruler for
*every* company, with chart + people-page filter *demoted to tagged fallback/
corroboration*, not retired.** The consistency argument (F1) is decisive and JD's
"is it easier to just always use Sales Nav?" is correct: the scorer compares
companies against each other and deltas across time, so **one ruler beats a mix of
individually-fine instruments** — you cannot compare a geo-chart-top5 value against a
people-page-city value against a Sales Nav value; they're different measurement
devices (G5). Reinforcing reasons: the fallbacks are demonstrably unreliable exactly
where it matters (geo-chart ~20% lossy per G5; DOM careers zero trap-prone per K1);
Sales Nav people-search with `current-company + NYC-metro` is the *definitional*
instrument for F1's named metric (everything else is a proxy-for-the-proxy); and it
**shares the warm_path session**, amortizing session cost and account-risk surface
onto one instrument instead of two.

Three consequences to accept with eyes open:
1. **Budget is now the binding constraint on headcount cadence.** Every company
   consumes a Sales Nav search *per cycle*, not just edge cases. Size the recurring
   cadence so monthly search volume stays under Sales Nav's search/commercial-use
   limit; if the cap allows N searches/day, that caps how many companies you
   re-measure per day — which the **priority queue already allocates** (hot companies
   first). The budget doesn't block A3; it *sets the cadence*, and the queue handles it.
2. **The whole headcount signal now rides the single riskiest source.** F2 (supervised
   aging), F3 (breaker taxonomy), and G7 (interleave + rate-limiter) now protect the
   *core metric*, not an edge case — so their priority rises accordingly. And if Sales
   Nav is down/challenged you have *no* primary instrument — which is why the fallbacks
   are **demoted, not deleted** (degraded mode + corroboration).
3. **One-time instrument migration.** The live 25 were measured on chart/people-page;
   going forward they're Sales Nav. Per G5 you don't compare across instruments, so
   **re-measure the live set on Sales Nav** to put everyone on the same ruler before
   trusting cross-company or cross-time deltas.

## K4 — Ratify the operator-dispute flow, and treat the dispute as an instrument-drift signal

**Ruling: yes, formalize "JD supplies/edits a value" as a first-class event in the
reconcile slice — and it does *two* jobs, not one.** (1) **Adopt with provenance:**
the value lands with `jd-manual` provenance, which outranks machine-measured for that
field and is **never silently overwritten** by a later machine measurement (a
disagreeing measurement surfaces as a delta, same never-revert invariant as J4). (2)
**Treat the dispute as a drift signal on the instrument:** JD supplying a value the
machine recorded as Unknown/wrong is *evidence the instrument underperformed* — log
it so a *pattern* of the same miss (Cluely + Alta, both geo-chart-fails) becomes
**countable**, not anecdotal. That's how "the geo-chart is unreliable" gets learned
from data (feeding K3) rather than noticed by luck. Mechanics: on a dispute event,
adopt `jd-manual`, **force a recheck of that field on the best instrument** (now Sales
Nav) to corroborate onto the common ruler, and record whether JD's manual value and
the instrument agreed — that agreement/disagreement *is* your instrument-calibration
metric. Provenance order: `jd-manual > machine-verified > machine-partial`.

## K5 — Entity-confirmation guard: resolve-then-echo the canonical entity, don't just repeat the string

**Ruling: ratify the echo-back, but make it an *identity-resolution + disambiguated*
echo-back — this is identity-before-write applied to the manual/voice intake path,
the one write path that has no entity binding.** A board edit already targets a
specific page (bound); a voice/chat value ("Cluely") is unbound, which is exactly the
gap that let "Clarity" receive Cluely's 4 heads. Close it by routing manual entry
through the **same identity resolver every other write uses** (rapidfuzz/splink):
- Resolve the spoken name against the canonical entity table, then **echo back the
  canonical identity *with keys*, not just the name** — "applying heads=4 to Cluely,
  cluely.com, Prospect — confirm?" Near-names rarely share a domain: "Cluely" and
  "Clarity" sound identical but `cluely.com ≠ clarity.com`, so **the domain is the
  disambiguator the ear can't hear but the eye can.** Echo the domain/slug.
- **Ambiguous match (Adaptive ×7, Complyance ×2) → force a pick.** Present candidates
  with distinguishing keys; never auto-select under ambiguity (the identity auto-bind
  bar — a low-confidence match is never auto-bound).
- **No match → confirm "new entity" before creating**, so voice entry can't silently
  spawn a near-duplicate.
The append-only log handling the Cluely/Clarity error cleanly (nothing erased, error
+ correction both on record) is the right *recovery*; the guard is the *prevention* —
blocking the wrong write beats a clean revert of it.

## K6 — Sequencing: reconcile before batch 3, now reinforced

**Ruling: unchanged and strengthened.** J2 already put reconcile before batch 3; this
addendum makes the case tighter. K4 (dispute intake) and K5 (manual-entry guard) are
*part of the reconcile slice* — they're how JD's manual measurements and corrections
get a **systematic home** instead of taking effect only when the machine happens to
re-read the board. JD is *actively out-measuring the machine* (K3's calibration
finding); every one of those corrections needs the reconcile intake path to persist
with provenance and to trigger the instrument audit. Loading 20 more companies before
that path exists widens the board JD is hand-correcting **faster than the machine can
systematically absorb the corrections** — the exact opposite of what you want while
the operator is the most reliable sensor on the board. Reconcile first.

---

# Follow-up rulings (round 5)

Same-day implementation of the J and K rulings, a live validation event, and **two
JD directives that revise prior rulings**. Two things to affirm first, because
they're the whole mechanized-invariant loop closing end to end within hours:
**J7 predicted all five partial-evidence flippers and four flipped on measurement**
— Astelia's Prospect seat "at exactly 60 riding the unknown" collapsing to Low NYC
on 2 heads is the textbook case J1 was written for; the evidence-hysteresis rule and
the replay audit *together* caught and corrected a real mis-route the same day. And
**JD's standing autonomy order** ("LinkedIn identity-verified + NYC headcount blank →
go measure it, no queuing, no asking") is JD encoding the operator-respect principle
himself: the machine's work queue must never leak onto the human's.

## Directive effects on prior rulings (record before the new questions)

- **Directive #1 (Sales Nav is the ruler) confirms K3 — no revision.** The
  discovered people-page geo param (`?facetGeoRegion=90000070`, exact metro count in
  one load) is precisely the *tagged interim fallback* K3 named; Sales Nav proper
  stays the pinned instrument. Migration debt now includes re-measuring tonight's
  geo-param values **and** the two earlier JD-manual values onto Sales Nav so every
  count and delta shares one ruler (K3 consequence #3).
- **Directive #2 (budgets waived during build) is a *scoped suspension*, not a
  deletion, of the cap rulings.** The F2 tiered-budget ramp, G7's deferred-checks,
  and any daily-cap language are **suspended for attended build-phase**, replaced by
  pace-only rules. They are **scheduled for reinstatement at unattended cutover**
  (L2). The *pacing* non-negotiables are untouched: human pace + jitter, working
  hours, strict LinkedIn serialization, breaker halts instantly on any challenge.
  Note the harmony, not tension: waiving the daily *quota* actually **strengthens the
  all-or-nothing-per-company invariant** (G7 atomicity) — "work moves through
  COMPLETELY, not piecemeal" is the same instinct as "no partial evidence, no
  stranded half-enrichment waiting for tomorrow's budget." The quota was in mild
  tension with atomicity; removing it (while attended) resolves that.
- **The standing autonomy grant has design weight and is affirmed:** "Action Needed
  must never show machine work as pending when the machine could just do it" is the
  detect-then-**do** line (vs detect-then-ask), the operator-respect principle at its
  conclusion. One guard: "could just do it" acts **within** the pacing envelope —
  autonomy to *act* is never autonomy to act *fast* or *into a challenge*. The grant
  operates inside the non-negotiables, not around them.

## L1 — The budget waiver, eyes open: the danger isn't daily volume, it's inhuman *regularity* — and the waiver only holds if monitoring replaces the quota

**Ruling: defensible while attended and at human pace — because 30–60 touches/day at
human pace is inside a legitimate heavy Sales-Nav-user envelope (a busy recruiter's
day), and the directive preserves exactly the signatures that *do* trigger detection
(superhuman speed, inhuman regularity) as non-negotiable.** The volume itself isn't
the threat. Three real residual risks the pace-only model doesn't fully cover:
1. **Sustained regularity is itself a signature.** A human has *day-level* variance —
   heavy days, light days, weekends, gaps. A machine doing 30–60 *every* working day
   on a fixed cadence, indefinitely, creates a longitudinal pattern even if each day
   is individually human-plausible. **Add day-level variance** (occasional light/
   skipped days, respect weekends), not just intra-day jitter.
2. **Sales Nav's commercial-use limit (CUL)** throttles heavy searchers monthly —
   *throttle, not ban*, but at 300 companies × cadence you'll approach it, and a CUL
   cap can *masquerade as an F3 soft-block (category d)*. The breaker taxonomy must
   grow a case: "monthly search limit reached" ≠ soft-block ≠ selector break.
3. **The waiver removes the blast-radius limiter quotas provided.** A cap also bounds
   how much a bug/runaway can burn before a human notices. Without it, the **breaker
   is the only volume ceiling left** — fine while attended (JD notices in minutes),
   which is exactly why L2's attended/unattended split is the crux.

**The line where I'd insist on coming back to JD with data is signal-triggered, not a
magic company count.** Don't pick "300." Come back on the *first sign the envelope is
tightening*: (a) **challenge frequency > a one-off** — the breaker halts on the first
challenge, but the observe layer must *count challenges over a rolling window*,
because a *second* challenge is the trend that matters; (b) **soft-block rate** (F3
category d) rising above a low baseline; (c) **CUL-throttle detection** on Sales Nav.
Any one → stop and bring data, don't push through. **These three are the tripwires
the observe layer must watch, and they must be live *before* scaling** — because the
waiver converts a *static* safety (quota) into a *dynamic* one (monitoring), and a
dynamic safety only protects you if it's actually watched. **The condition on the
waiver: no live tripwires = the safety was removed, not replaced.**

## L2 — Unattended cutover flips the safety model: mechanize the caps back, and make "unattended without caps" an impossible state

**Ruling: confirmed and sharpened — the waiver is *mode-scoped*.** Attended/build =
JD's judgment + the breaker are sufficient, quotas are just friction. Unattended =
the human sensor of last resort is *gone*, so the only protection is what's
mechanized. In unattended mode:
- **Reinstate a volume cap as a blast-radius limiter** (not as anti-detection —
  pacing handles that). Its unattended job is to bound what a bug, a runaway retry,
  or a slow drift into a challenge-storm can burn before the next human check-in. Set
  it to *the volume JD would be comfortable discovering the machine did while he
  wasn't looking* — smaller than the attended max.
- **Conservative-on-uncertainty becomes mandatory.** Attended, a soft-block can be a
  judgment call; unattended, the only safe default is halt-don't-write-alert-wait,
  because no judgment is available.
- **Make it an invariant, not a to-do.** `attended_mode` is a config flag the
  scheduler sets; the system **refuses to run unattended without its caps** the same
  way it refuses a malformed config (config-validated at boot). Don't leave
  "reinstate quotas when we go unattended" as something a human remembers — mechanize
  it so the unsafe state can't exist. That's the elite move: the safety model
  *inverts automatically* at cutover.

## L3 — Review auto-resolution: the machine may finish an *evidence* question under JD's own rule; it may never close a decision JD *reserved*

**Ruling: default is your lean — an opened review waits for the human (a review is a
promise) — with one typed exception, and Bolto is NOT in it.** The discriminator is
*what the review was waiting on*:
- **Evidence-gated review** (opened only because a measurement was missing/ambiguous):
  once new evidence resolves it **under a rule JD already approved**, the machine is
  not making a new judgment — it's applying JD's own rule to now-complete evidence.
  This subclass **may auto-close**, with the resolution change-logged and surfaced
  ("review auto-resolved: evidence now decisive, routed per [rule]").
- **Judgment-gated review** (opened because the *decision* is JD's by ownership — a
  relationship call, a protected status, a reserved "should we pursue despite X"):
  **never auto-closes**, no matter how decisive the evidence.
This reuses J5's structured `review_reason` for free — the enum already carries
whether a review is evidence-gated or judgment-gated, so the machine knows which it
may close. **Bolto stays open:** by your own description "JD's open decision outranks
the router" — that's a *judgment gate*, not an evidence gate. So even though 0 heads
/ 0 jobs / Chicago hubs is now unambiguous, the *decision* is one JD reserved.
Surface "evidence now decisive → recommend Do Not Pursue" on the board so he closes
it in one glance; the machine does not close it. (If JD prefers maximum conservatism
— *all* reviews wait, even evidence-gated — that's a defensible simpler setting and
it's his queue to set; the typed exception is an offer, not a mandate.)

## L4 — J7 graduates from bug-hunt to standing regression harness — confirmed, plus a fourth job

**Ruling: confirmed — and add post-config-change regression as a fourth standing
use.** J1 now *prevents* partial-evidence *entry* structurally, so J7's role shifts
from catching that bug to four guardrails: (1) **held-position sensor** — J1 lets a
company hold on one absent component, so replay periodically re-checks "would this
held company survive a worst/best forcing of the missing value?"; (2) **pre-batch
sanity gate**; (3) **post-instrument-migration check** (after the Sales Nav
re-measure, confirm the new ruler doesn't silently flip anyone); and (4) **new:
post-config-change regression** — any edit to the scoring config or a router
threshold (J6 taxonomy order, hysteresis bounds, band cutoffs) gets a replay against
live data to see *what would move* before it ships. J7 is now the cheap "what does
this change do to the live board?" harness for the whole routing layer.

## L5 — Reconcile scope: the happy-path list is right; the edge/safety pieces are what make it safe against live JD edits

**Ruling: the ten-item list is complete on the happy path. Add seven edge/safety
items, fix one scoping error, pin one ordering rule, and scope cadence to mode.**

**One scoping fix — separate sweep-triggered from event/one-shot work.** The list
mixes three trigger types; build them together but don't run them on the same clock:
- *Sweep-triggered* (every sweep): board diff, JD-edit adoption, drift-heal, the
  non-Verified⇒Action assertion.
- *Event-triggered*: resolve-then-echo (fires on manual entry, often interactive),
  dispute-as-drift logging, the select-migration playbook (fires on **schema
  change**, not every tick).
- *One-shot*: **the Sales Nav re-measure migration is a one-time job, not a recurring
  reconcile duty** — gated by the L4 replay audit. Baking "re-measure every headcount"
  into each sweep would re-measure the whole board every cycle. Run it once, verify,
  retire it.

**One ordering rule that prevents re-introducing the clobber:** within a sweep,
**adopt JD edits BEFORE healing drift.** Sequence: (1) read board → (2) adopt JD
edits with provenance (their fields are now truth) → (3) heal drift on the *remaining
machine-owned* columns against the datastore → (4) assert invariants → (5) write
back. Heal-before-adopt would overwrite a JD edit before it was adopted — the exact
failure J2/J4/K4 guard against.

**Seven missing edge/safety pieces:**
1. **Heal scope = machine-owned fields ONLY, stated as an invariant.** Reconcile
   *reads* human-owned fields (to adopt) but **never writes** them (relationship
   notes, protected statuses, jd-manual values). This is *the* reconcile invariant;
   without it a drift-heal can clobber a JD edit.
2. **Idempotency (the controller-runtime property).** Every reconcile action must be
   idempotent and correct from any starting point, so a sweep run twice — or run
   mid-enrichment — can't double-apply. This is what makes level-triggered safe.
3. **Per-company failure isolation (bulkhead, G7).** A breaker halt on one company's
   triggered recheck records the halt and **moves on** — one company's challenge
   never stops the whole sweep. A half-finished sweep is safe because the next sweep
   re-converges.
4. **Reconcile writes its own actions to the change-log.** A drift-heal or an
   adoption is itself an append-only entry ("reconcile healed X to datastore truth"),
   so "why did this change?" is always answerable — reconcile never acts invisibly.
5. **Stale-jd-manual surfacing.** jd-manual outranks machine and is never silently
   overwritten — but a *materially newer* machine measurement (JD's heads=4 from a
   month ago vs Sales Nav's 6 today) **surfaces as a Changes delta for JD to
   accept/refresh**, so a stale manual value can't ossify forever. Never-overwrite
   holds; add never-let-it-silently-rot.
6. **Cross-field invariant re-assertion, not just the Action one.** While sweeping,
   re-assert the whole invariant set on each row (Unknown≠0, band-entry evidence
   completeness, single-write-path) — the sweep is the natural place to catch any row
   that drifted out of spec, not only the non-Verified⇒Action rule.
7. **A dry-run/diff mode for the sweep.** Before the first live reconcile against
   JD's real edits, run it in report-only mode (show what it *would* adopt/heal/flag)
   so you validate the adopt-before-heal ordering on real data before it writes. Cheap
   insurance for the highest-clobber-risk slice.

**Minimal correct sweep cadence while attended-only: cadence follows mode.** You do
**not** need a background timer while the system runs only in working sessions — a
timer is unattended-mode machinery. Level-triggered means "converge when it matters,"
so the minimal correct cadence is **event/session-triggered**:
- **Mandatory: a full sweep at the *start* of every working session, before the
  machine does anything else** — this is what adopts whatever JD edited while the
  machine was off (the H6 scenario: "I pasted a careers link, how does it know?").
  That single rule closes the H6 gap.
- **On-demand after a burst of board edits** within a session.
- **At session end**, to flush/verify.
Build the periodic level-triggered timer (with tiered requeue — hot objects sooner,
brain/02) **only at unattended cutover**, alongside L2's caps. Don't build the timer
now; build the session-start sweep now.

---

# Follow-up rulings (round 6)

From batch 3 (20 companies, 45/45 converged, 150 tests green). One anomaly that is a
**real correctness bug** (M6, the Camp Network re-ask) plus five hurdles. Two of the
five (M3 entity-leak, M4 US-wide postings) are not parsing fixes — they touch
*evidence attribution* and the *demotion* logic, and both resolve to principles the
brain already holds (identity-before-write; J1 absent-never-demotes). M1/M2/M6 feed
directly into the **v2 cleanup prompt** as fixes-with-tests.

## M1 — Velocity merge: don't widen the flat window, make the wide window *evidence-gated*

**Ruling: two windows, not one bigger one.** Fig Security's 21-day seed→A with the
*same lead investors* is clearly one raise in two announcements — but the fix is not
"cap the window at 30 days flat," because a flat 30-day window would wrongly collapse
two *genuinely distinct* rounds that happen 25 days apart (a fast-but-real seed→A,
which is real signal you must not erase). The signal that two rounds are *one event*
is not the gap alone — it's **corroborating same-raise evidence.** So:
- **Short flat window (≤ ~14d): collapse on time alone** — handles the out-of-stealth
  same-week disclosure (G3's original case).
- **Wide window (≤ ~45d): collapse ONLY when corroborated** by a same-raise signal —
  canonically **shared lead investor(s)**, also explicit tranche labels or a
  seed/seed-extension pairing. Fig (21d + same leads) → collapses. A hypothetical 21d
  gap with *different* leads and a valuation step-up → stays two rounds.
Both windows are tunable config, boot-validated (J6). Tag the collapsed event
`announced-in-tranches (same lead)` — per G3 the pattern is itself evidence, not
nothing. **Dependency:** this needs clean, comparable lead-investor data (ties to M3);
if lead investors can't be parsed reliably, fall back to the short flat window and
flag rather than guess.

## M2 — Funding totals: trust the headline aggregate; dedupe rows for *structure*; cross-check the two

**Ruling: yes, "trust the headline total, dedupe the rows" is the standing rule — with
a mandatory cross-check.** The headline **Total Funding is Crunchbase's own reconciled
aggregate and is the authoritative total** — *never reconstruct the total by summing
rows*, because rows are duplicate- and tranche-prone (Daytona's pre-seed and seed each
appearing twice). Separately, **dedupe rows to distinct `(round_type, announced_on)`
tuples** for round-structure and velocity purposes — and note the store's
`UNIQUE (entity_id, round_type, announced_on)` constraint already enforces the exact
case at the DB layer. The non-negotiable addition (Unknown≠0 / verified discipline):
**cross-check the deduped-row sum against the headline; if they materially diverge,
drift-flag to review** rather than silently trusting either. A discrepancy is a known
data-quality signal to surface, not a number to smooth over.

## M3 — Financial-row attribution: the discriminator is DIRECTION (recipient vs investor), not a name-substring

**Ruling: right instinct, wrong handle — fix the phrasing before it creates false
negatives.** "Only rows whose name contains the company's own name" would exclude the
*leaks* (correct) but also exclude most *legitimate* raises, which are named by round
type ("Series A", "Seed") and do **not** contain the company name. The real
distinction is **direction: is the company the *recipient* of the round, or the
*investor/grantor*?** Etherealize's "Ethereum Institutional" seed and Daytona's
"BeatAI" grant are rows where the company is the *funder* and a **different named
entity** is the recipient. So:
- **Count** rows that are the company's own funding rounds (round-type-named, capital
  flowing *in*).
- **Exclude** rows attributed to a *different named entity* (grants/investments the
  company *made*) — prefer Crunchbase's structural signal (the Investments section /
  investor role) over string matching where available.
- **Ambiguous row → exclude from the total AND flag** (Unknown≠0: an unclassifiable
  row is not silently counted).
This is **identity-before-write applied to funding evidence** (brain/04; brain/10 D2):
evidence must be attributed to the *correct entity* before it counts. JD's name-match
catches the cases he saw because the leaks carry another entity's name — but encode it
as "exclude rows about a *different* entity," never "require the company's *own* name."

## M4 — A verified NYC office turns a "US-wide/remote, no explicit NYC" reading from a measured-0 into an *ambiguous* signal — which may not drive the Low-NYC exit

**Ruling: yes, soften it — because this isn't softening, it's correctly classifying
the evidence.** This is J1's absent-vs-contradicting distinction, and the standing
"NYC must be listed" rule was too blunt: it's correct for *counting explicit NYC
roles* but wrong to let that count *drive a demotion* when the 0 is an artifact of how
the company posts, not confirmed absence. The discriminator is the **shape of the
non-NYC roles**:
- **NYC-excluding** (roles explicitly in *other* cities — Echo's Tel Aviv/SF — and no
  NYC office): a real **measured-low**. The Low-NYC exit **stands**.
- **NYC-ambiguous** (roles posted "United States" / "Remote, U.S." *with a verified
  NYC office* — Fig's 488 Madison): the NYC-eligible count is **not 0, it's Unknown** —
  we cannot measure how many of those remote roles are NYC. Per J1, **absent/ambiguous
  evidence may never demote**, so this **does not trigger the hard Low-NYC exit.**
Mechanism, precise so it doesn't over-correct: a verified-NYC-office + US-wide/remote
reading sets `nyc_jobs = Unknown` (evidence note: "roles posted US-wide/remote; NYC
office verified at [address]; NYC-eligibility unmeasurable"), **not** `0` and **not** a
fabricated positive. That Unknown holds the company in review/watch (and, with the
office as a weak-positive presence signal, off the Low-NYC shelf) while the data-blind
cap keeps it from claiming a Prospect seat it hasn't earned. **The office blocks the
demotion without manufacturing a promotion.** Gate strictly on a *verified* office
(stale/unverified address doesn't count). Fig holds instead of shelving — correct.

## M5 — Embedded ATS boards are now the majority path: elevate G2+K1 from "protocol" to "the standard careers lane"

**Ruling: confirmed — 5 of 12 Ashby boards being embed-only makes the two-phase lane
the DEFAULT, not a fallback.** The discovery/bind phase must **always** parse embed
scripts / the rendered DOM for ATS handles; "static scan found nothing" is **never**
"no board" (that's the K1 false-zero trap that produced Brandlight). Standard careers
path, restated as the norm: **browser + embed-parse to BIND (extract the Ashby board
token), then the Ashby API to COUNT** on cadence (G2 — cheap, no re-discovery). One
addition for the observe layer: **track the static-discovery hit-rate as a metric** —
it's now ~50% embed-only, and if it drops further the browser-bind becomes even more
load-bearing, which is a cost/account-surface signal worth watching (more binds = more
browser sessions on the risky source).

## M6 — The Camp Network re-ask is a real bug: the negative-finding intake must persist a *durable suppressing state*, not just fire an event

**Ruling: this is a correctness bug and a trust bug, and it goes in the v2 cleanup
prompt with a locking test.** "Joe says: no careers page" is defined (round-5 Part 5)
to be *recorded with jd-manual provenance + date, stop re-asking, and switch the
company to the LinkedIn-jobs fallback with monthly re-discovery.* It came back after
JD acked it because the intake is being **adopted as an event but the resulting
durable state isn't persisted** — so the next projection re-derives "Joe: paste
careers link" and re-sets the ask. The fix:
- Acking "no careers page" transitions the company to a **durable state**
  (`careers_status = no-page-per-jd`, jd-manual provenance + date) that **suppresses
  the board ask** and **switches enrichment to the LinkedIn-jobs fallback.**
- The careers **re-discovery is scheduled to +1 month, not immediate** — the intake's
  forced recheck must not re-run discovery seconds after JD acked and re-emit the ask.
- **Locking test (for the v2 prompt):** ack "no careers page" → run a reconcile sweep
  → assert the "paste careers link" ask does **not** return and `careers_status`
  persists. A batch-3 miss that isn't turned into a test recurs in batch 4 (the K1
  "same reader, same bug" lesson). Note: DataLane's "Joe: paste careers link" rides
  the *same* mechanism — fixing M6 makes that intake trustworthy too.
