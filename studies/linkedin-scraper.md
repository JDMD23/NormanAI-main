# Study: linkedin_scraper

- **Repo:** https://github.com/joeyism/linkedin_scraper
- **Studied:** 2026-08-06 at commit `b1cdc1c` (v3.x)
- **What it is:** A long-lived (since ~2018) PyPI library for scraping LinkedIn
  profiles, companies, and jobs — freshly rewritten in v3 from sync Selenium to
  async Playwright with Pydantic models. 45 files, ~3,900 lines: `scrapers/`
  per entity, `models/`, `core/` (auth, browser, exceptions), samples, and a
  unit/integration-split test suite.
- **Why it was worth studying:** Little new theory — its value is as a
  **comparative specimen**: it demonstrates, in one small codebase, the exact
  diseases and dilemmas that three earlier studies provide the treatments for.

## Architecture at a glance

```
core/       BrowserManager (async context manager), session save/load, exceptions
models/     Pydantic: Person, Company, Job, Post (+ to_dict/to_json)
scrapers/   base + per-entity scrapers; person.py alone is 1,122 lines
samples/    runnable per-scenario scripts incl. create_session.py
tests/      unit (hermetic, ~5s) vs integration (marked, needs a session)
```

## Three instructive contrasts

### 1. Breaking rewrite under the same name — vs. langchain's rename-and-freeze

v3 is "NOT backwards compatible": Selenium→Playwright, sync→async, new imports,
new models, new signatures — shipped under the *same PyPI name*, mitigated by a
migration guide and "pin `linkedin-scraper==2.11.2`" advice. This is the exact
fork in the road where langchain (studies/langchain.md) chose rename-and-freeze
(`langchain-classic` beside a new package). Same-name breaking majors push the
cost onto every downstream `pip install -U` and every tutorial ever written;
the rename costs the maintainer a package registration. The migration guide
here is well done (before/after code, escape hatch stated) — it's the best
version of the worse strategy. For a hobby-scale library the choice is
defensible; the contrast is what's instructive.

### 2. Hardcoded selectors — the disease Scrapling treats

`person.py` is 1,122 lines dominated by DOM navigation against LinkedIn's
current markup. Every LinkedIn redesign breaks it; the repo's long issue
history *is* the maintenance treadmill of brittle references. Scrapling
(studies/scrapling.md) exists precisely to convert this class of breakage into
fingerprint-based re-derivation. Seen side by side: hardcoded selectors are
borrowing against every future redesign, and this repo has been paying that
interest for eight years. (brain/04's self-healing-reference rule, argued by
counterexample.)

### 3. The disclaimer-only compliance posture

LinkedIn's ToS prohibits scraping; this library authenticates with a saved
logged-in session, which forecloses the "public data only" argument that
carried hiQ-style litigation. The repo's entire posture is one line at the
bottom: "for educational purposes only… comply with LinkedIn's Terms of
Service… authors are not responsible." Compare Scrapling (ships robots.txt +
throttling machinery alongside its stealth) and JustHireMe (multi-source
adapters where per-source posture at least varies): the spectrum runs
machinery → variance → disclaimer, and this sits at the bare end. The
engineering lesson stands apart from the legal one: a library whose core value
is ToS-adverse has a ceiling on every other investment in it.

## What it does well

- **Session-as-artifact auth.** Login is pushed *out* of the library:
  `create_session.py` produces a `session.json` the user loads —
  the library never handles credentials in scraping code, sessions are
  reusable across runs, and the credential-handling surface is one sample
  script. Right boundary for auth in any browser-automation tool.
- **Hermetic-by-default tests.** Unit tests (models, browser context, session
  round-trip, navigation utils) run in ~5s with no network; tests needing a
  real LinkedIn session are pytest-marked `integration` and opt-in. The
  default developer loop stays fast and credential-free (brain/03's pyramid,
  executed at small scale).
- **Models separated from scraping.** Pydantic entities with serialization
  helpers, independent of the DOM-walking — the data contract would survive a
  scraper rewrite (and just did, v2→v3).
- **An honest, complete migration guide** — before/after code, what changed and
  why, and the pin-the-old-version escape hatch in the first screen of the
  README.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Same-name breaking majors are the costlier strategy; if you must, ship the before/after guide and the pin escape hatch prominently | v3 README | Library versioning; rename-and-freeze (brain/07) remains kinder |
| Push authentication out of the library: sessions as user-owned artifacts, credentials confined to one setup path | create_session.py / load_session | Browser automation, API clients |
| Mark credentialed/network tests and keep the default suite hermetic and fast | pytest markers | Any library with external-service tests |
| Hardcoded references into others' markup are unhedged debt — eight years of issue-tracker interest | person.py history | The brain/04 fingerprint rule, by counterexample |

## Brain updates made

- None — the brain already holds every principle this repo illustrates
  (brain/04 self-healing references, brain/05 compatibility, brain/07
  rename-and-freeze, brain/03 test structure). This study is recorded as
  *confirming evidence and counterexample*, which is what studies are for when
  a codebase teaches by contrast rather than by novelty.
