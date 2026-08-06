# Study: Scrapling

- **Repo:** https://github.com/D4Vinci/Scrapling
- **Studied:** 2026-08-06 at commit `bc0cf7d`
- **What it is:** A mature adaptive web-scraping framework: fast lxml-based
  parser with **self-healing selectors**, a fetcher ladder (plain HTTP → real
  Chrome → stealth Chrome), a spider framework (scheduler, throttle, checkpoint
  pause/resume, robots.txt, proxy rotation), CLI, MCP server, and an official
  agent skill. 55 package modules, 57 test files, in-repo competitor benchmarks.
- **Why it was worth studying:** The nineteenth study brings the collection's
  best example of **self-healing references** — a general pattern implemented
  with deliberately boring machinery — plus the sharpest skill-trigger design
  seen so far.

## Architecture at a glance

```
scrapling/core/       storage (ABC → SQLite), similarity, custom types, shell
scrapling/parser.py   Selector: css/xpath + auto_save/adaptive relocation (1,381 ln)
scrapling/fetchers/   requests.py → chrome.py → stealth_chrome.py  (capability ladder)
scrapling/engines/    static + browser engines, toolbelt
scrapling/spiders/    engine, scheduler, throttle, checkpoint, robotstxt, cache
agent-skill/          official versioned SKILL.md + references + examples
benchmarks.py         timeit comparison vs 8 competitor parsers
```

## The headline: self-healing selectors with boring machinery

The signature feature (`auto_save=True` / `adaptive=True`) is a clean instance
of a general pattern:

1. **On first match, store a fingerprint** — the element serialized to a dict
   (tag, attributes, text, structural context) in SQLite, keyed by URL +
   identifier hash, behind a pluggable `StorageSystemMixin` ABC.
2. **When the page changes and the selector fails, re-derive** — score *every*
   element in the new DOM against the fingerprint with a multi-attribute
   similarity function (separate sub-scores for class/id/href to survive "full
   structural changes"), and return the highest scorers above a threshold.

No ML, no LLM, no network: deterministic, offline, cheap, explainable — where
the fashionable 2026 answer would be "ask a model to find it again."
The docstring even warns against threshold-twiddling ("don't play with this
number unless you must know what you are doing").

**The general form, now in the brain:** any reference into structure you don't
control (CSS selectors, API response paths, UI-test locators) is derived data
that *will* break. Store enough fingerprint at bind time to re-derive the
reference when the structure shifts — the reference is cache; the fingerprint
is source; relocation is the recompute path (brain/04's derived-data rule,
pointed at external volatility).

## What else it does well

1. **Trigger design: position the skill as the fallback for the platform's
   native tool.** The official skill's description includes "Use when…
   **web_fetch fails**; the site has anti-bot protections…" — triggering on the
   *failure of the built-in alternative* is the sharpest routing-surface move
   in nineteen studies. The skill is versioned ("0.4.12"), declares binary
   requirements in metadata, and states its authority: "the official skill for
   the scrapling library by the library author" (the obsidian vendor-skill
   pattern, executed with version + requirements discipline).

2. **A capability ladder priced by cost.** `Fetcher` (plain HTTP) →
   `DynamicFetcher` (real browser) → `StealthyFetcher` (hardened browser) —
   escalation is explicit and caller-chosen; you pay for headless Chrome only
   when the target requires it. Same shape as JustHireMe's embedding ladder and
   brain/09's model tiering: capability tiers with visible price tags.

3. **Responsibility machinery ships alongside the stealth.** The spider
   framework includes `robotstxt.py`, `throttle.py`, and `checkpoint.py` —
   robots compliance, rate limiting, and resumability are first-class modules,
   not afterthoughts. (See tradeoffs for the other half of this coin.)

4. **In-repo competitor benchmarks** — `benchmarks.py` runs Scrapling against
   eight parsing libraries (bs4, parsel, lxml, selectolax, pyquery…) under the
   same timeit harness. Lighter than graphify's standard (no blind judging —
   but parsing speed needs none), and the performance claims are reproducible
   with one command.

5. **Typed with care where it counts** — `@overload` signatures on `relocate`
   so `selector_type` flips the return type statically; a custom-types module;
   57 tests organized by subsystem (parser, fetchers, spiders, cli, ai,
   integrations).

## Tradeoffs and the honest paragraph

- **Dual-use surface.** "Bypass anti-bot systems like Cloudflare Turnstile out
  of the box" is a headline feature. The legitimate uses are real (scraping
  your own properties, authorized data collection, research, sites that
  over-block), and the same repo ships robots.txt support and throttling — but
  the framework leaves the authorization question entirely to the user, and
  its marketing leads with evasion rather than responsibility. An engineering
  study can note the craftsmanship while flagging that the ToS/CFAA posture is
  the user's burden and the README could own that framing more directly.
- **`parser.py` at 1,381 lines** holds the whole Selector API — coherent but
  approaching the mega-module line (brain/03).
- **Relocation is O(page × fingerprint checks)** — brute-force scoring of every
  DOM node; fine for scraping cadence, worth knowing before borrowing the
  pattern for hot paths.
- **Fingerprint staleness** — auto_save overwrites on success; a redesign that
  *partially* matches wrong elements above threshold will silently re-bind. The
  threshold docstring warns, but there's no confidence surfacing to the caller
  (graphify's extracted/inferred labeling would fit perfectly here).

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| References into volatile external structure are derived data: store a fingerprint at bind time, re-derive by similarity on failure | auto_save/adaptive + SQLite fingerprints | Selectors, UI-test locators, API-shape assumptions; O(n) rescan is the cost |
| Prefer boring, deterministic healing over LLM re-finding — offline, cheap, explainable | similarity scoring, no ML | Anywhere the fingerprint captures enough signal |
| Trigger official skills on the failure of the platform's native tool | "use when web_fetch fails" | Vendor skills; the fallback slot is the highest-value trigger |
| Ship capability ladders with visible price tags; never default to the expensive tier | Fetcher → Dynamic → Stealthy | HTTP clients, browser tools, model tiers |
| Version the skill, declare its runtime requirements in metadata | skill frontmatter | Any distributed skill |
| Dual-use tools should ship the responsibility half too — and lead with it | robotstxt/throttle vs stealth marketing | Scraping, automation, security tooling |

## Brain updates made

- `brain/04-data-and-state.md`: added the self-healing reference pattern to the
  derived-data guidance (fingerprint at bind time; similarity re-derivation on
  structural change; surface confidence when re-binding).
- `brain/09-agentic-engineering.md`: one line on the routing surface — the
  platform-native tool's failure mode is the highest-value trigger for a
  vendor skill.
