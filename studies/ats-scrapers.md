# Study: ats-scrapers

- **Repo:** https://github.com/kalil0321/ats-scrapers
- **Studied:** 2026-08-06 at commit `40e49f0`
- **What it is:** An open dataset + Python toolkit for job data: 50+ scraper
  adapters for ATS platforms (Workday, Greenhouse, Lever, Ashby, SmartRecruiters,
  SuccessFactors…) normalizing into one typed schema, plus a free hosted dataset
  (4.2M+ jobs / 63k companies / 49 sources). 257 files, 86 source modules, 100
  test files, MIT.
- **Why it was worth studying:** The best-engineered scraper in the collection
  and a near-textbook **plugin/adapter architecture** — the right counterexample
  to linkedin_scraper on every axis, and the source of one crisp new principle.

## Architecture at a glance

```
scrapers/base.py     BaseScraper (ABC) + ScraperRegistry (decorator registry)
scrapers/<ats>.py    50+ adapters: one afetch() each, capability declared as
                     class attrs (fetch_engine, fetch_escalate, default_headers)
fetch.py             Fetcher: httpx → httpcloak (TLS impersonation) escalation ladder
models.py            Pydantic Job/Company/Salary; field names are a public contract
enrichment/          derived fields computed from the normalized core
resolve.py client.py hosted-dataset query layer (search over Parquet/CSV)
ats-companies/*.csv  per-ATS company slug lists (the input registry)
```

## What this codebase does exceptionally well

1. **A registry-based plugin system, done right.** `@ScraperRegistry.register(
   ATSType.GREENHOUSE)` on each adapter; "the registry is the only stable lookup
   mechanism — never import scraper classes by path from outside the package."
   New provider = one file implementing one method (`afetch`), self-registering.
   This is brain/05's extension-seam lesson (langchain's middleware, graphify's
   language-extractor recipe) in its cleanest small-scale form: the base class
   is the interface, the registry is the discovery mechanism, and 50 adapters
   prove the seam.

2. **Capability declared as data, escalation as a ladder.** Each adapter sets
   class attributes for what its ATS *needs*: `fetch_engine` ("httpx" for
   nearly everything, "cloak" = TLS+h2 impersonation for load balancers that
   block plain clients), `fetch_escalate` (retry a 403/406 through httpcloak
   once and stick with it), `default_headers`. Anti-bot handling is a
   *per-provider declaration consumed by a shared fetcher*, not bespoke code in
   each scraper — the capability-ladder pattern (Scrapling's fetcher tiers,
   JustHireMe's embeddings) expressed declaratively, with the cheap engine as
   the default and escalation opt-in per known-bad tenant.

3. **The normalized schema IS the product, and treats field names as a public
   contract.** models.py says it outright: "Backwards compatibility on field
   names is part of the public contract — renaming a field" breaks Parquet
   exports and every downstream query. Provider-specific overflow is preserved
   verbatim in a metadata field ("Greenhouse custom fields, Bundesagentur
   arbeitszeit/branche…") rather than dropped — the brain/04 lesson (model the
   domain, keep provider quirks without letting them leak into the core schema)
   and brain/05 (serialization formats are contracts) applied to a 49-source
   union. Adding a field is a documented three-step ritual (dataclass +
   normalizer default + parquet schema).

4. **Per-adapter docstrings document the provider's reality — the knowledge
   delta for scraping.** Greenhouse's header: the exact public endpoint,
   "the most permissive ATS API — no auth, no rate limits in practice,"
   `content=true` costs ~5x response size but saves per-job detail fetches
   across ~3,000 boards, employment-type is "NOT in the list response… only via
   the authenticated harvest API." This is the anthropic-skills knowledge-delta
   principle (studies/anthropic-skills.md) applied to *external APIs*: capture
   what you learned about the provider's quirks at the seam, next to the code
   that depends on it, so the next maintainer inherits the hard-won knowledge.

5. **Async-first with a non-crashing sync bridge.** `afetch` is the primitive;
   the sync `fetch()` wrapper "works both from plain scripts and from inside a
   running event loop (Jupyter, FastAPI), where it runs the coroutine on a
   private loop in a worker thread instead of crashing in `asyncio.run`." The
   sharp edge (calling sync-over-async inside a live loop) handled correctly
   rather than left as a footgun — the mark of a library that met its users.

6. **Contract tests per provider.** 100 test files including `test_adp.py` +
   `test_adp_contracts.py` pairs — the MiroFish consumer-side-contract-test
   lesson (studies/mirofish.md) applied at scale: each external API's assumed
   shape is pinned so provider drift fails CI, and there's an `e2e/` tier.

## The compliance contrast (vs linkedin_scraper)

The counterpoint to the previous study, and it's instructive. This library hits
**official, public, unauthenticated ATS endpoints** (Greenhouse's public board
API, etc.) — the ATS platforms *publish* these for career-site rendering. No
login session, no ToS-adverse authentication, employer-published job postings.
That's a categorically stronger footing than scraping authenticated LinkedIn
sessions, and it shows in the engineering: because the data source is
legitimate and stable, every other investment (typed schema, contract tests,
hosted dataset, 50 adapters) has a durable foundation to compound on. The
lesson the pair teaches together: *the legitimacy of the data source sets the
ceiling on everything you can responsibly build above it.*

## Questionable calls and tradeoffs

- **TLS impersonation is still an arms-race dependency.** The "cloak" engine
  exists because some tenants block plain clients — legitimate here (public
  data, impersonating a browser to read an employer's own posted jobs), but the
  escalation ladder means some providers are one policy change away from
  breaking, and httpcloak is an evasion dependency to maintain.
- **50 adapters is 50 maintenance surfaces.** Each is small and isolated (the
  architecture's whole point), but ATS APIs drift; the per-provider contract
  tests are the necessary hedge, and their existence is why this is sustainable
  where a monolithic scraper wouldn't be.
- **The hosted dataset is a separate trust boundary** — `storage.stapply.ai`,
  the maintainer's service; the OSS toolkit funnels to it (disclosed, MIT,
  base install works without it, but the open-core seam is present).

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Plugin systems: ABC interface + decorator registry as the only lookup; a new provider is one self-registering file with one method | BaseScraper + ScraperRegistry | Any N-provider integration (payments, storage, LLMs, ATSes) |
| Declare per-provider capability as class-attribute data consumed by a shared client; default cheap, escalate opt-in | fetch_engine/escalate ladder | Multi-backend clients with varying auth/anti-bot needs |
| A normalization schema's field names are a public contract; preserve provider-specific overflow verbatim in a metadata field | models.py contract note | Any system unioning many sources into one schema |
| Document the provider's quirks in a docstring beside the adapter — the knowledge delta for external APIs | Greenhouse docstring | Every integration; the next maintainer inherits the lesson or relearns it |
| Pair a contract test with each provider adapter so upstream drift fails CI | test_*_contracts.py | Multi-vendor integrations |
| The legitimacy of the data source is the ceiling on everything built above it | official ATS endpoints vs authed sessions | Any data-collection product |

## Brain updates made

- `brain/05-apis-and-boundaries.md`: added the provider-adapter pattern — ABC +
  decorator registry as sole lookup, per-provider capability declared as data
  consumed by a shared client, and per-adapter docstrings capturing the
  provider knowledge-delta at the seam.
