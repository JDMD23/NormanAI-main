# Study: linkedin-mcp-server

- **Repo:** https://github.com/stickerdaniel/linkedin-mcp-server
- **Studied:** 2026-08-06 at commit `ba0562d` ("Refuse a profile root nobody
  claimed")
- **What it is:** An MCP server exposing LinkedIn (via the user's own logged-in
  browser session, patchright/Chromium) as ~20 tools to AI assistants — profiles,
  companies, jobs, messaging, people search. 64 modules, Apache-2.0, mature
  (issue numbers in the 600s), with a striking amount of daemon/session
  infrastructure.
- **Why it was worth studying:** The first **MCP server** studied — the
  *tool-provider* side of the agent boundary, where every prior skill study sat
  on the consumer side. It is the single best specimen of tool-interface design,
  agent-facing failure semantics, and safety-by-provable-ownership in the whole
  collection, and its CLAUDE.md is a masterclass.

## Architecture at a glance

```
tools/          person, company, job, messaging, post, feed — the MCP surface
scraping/       fields.py (section registry), extractor, per-section parsers
drivers/ browser_launch.py   patchright Chromium, coherent-identity launch config
daemon_*.py (12 files)       singleton browser daemon: election, lock, liveness,
                             lease, owner, proxy — one browser shared across calls
session_state.py profile_claim.py profile_lease.py   provable profile ownership
core/ config/ utils/         auth, errors, diagnostics
```

## The four things it does better than anything else studied

### 1. Tool design as a first-class interface (the MCP surface)

Every tool is engineered as an API for an agent consumer:
- **MCP annotations carry semantics the model needs:** `readOnlyHint: True`,
  `openWorldHint: True`, tags, titles — the tool tells the agent what *kind* of
  operation it is. Mutating tools (`send_message`, `connect_with_person`)
  "require confirmation" — write operations gated, reads not (brain/05's
  safe-by-default, at the tool layer).
- **Explicit section selection over fetch-everything:** `get_person_profile`
  takes a `sections` argument (experience, education, posts…) so the agent pulls
  only what it needs — the index-then-fetch / progressive-disclosure economics
  (brain/09) built into the tool signature, saving both navigation and tokens.
- **`exclude_args=["extractor"]`** hides an internal dependency-injection
  parameter from the agent-visible schema — the tool's public interface is
  curated separately from its implementation signature (brain/01 information
  hiding, at the tool boundary).
- **Bounded inputs** (`max_scrolls: Field(ge=1, le=50)`) validated at the
  boundary (brain/04 parse-don't-validate).

### 2. Structured, partial-failure return format

Every scraping tool returns `{url, sections: {name: raw_text}}` plus optional
`section_errors: {section: {error_type, error_message, issue_template_path,
runtime, …}}`, `unknown_sections`, and typed `references`. Two deep ideas:
- **Partial failure is first-class.** One broken section doesn't fail the call —
  it returns its data and reports the failure *in band*, so the agent gets the
  three sections that worked plus a typed error for the fourth. This is the
  brain/01 error-handling rule ("expected failures are values") shaped for an
  agent consumer that can act on partial results.
- **Errors carry an `issue_template_path`.** A failure hands back the path to a
  bug-report template — the tool is instrumented so its own breakages route
  toward a fix. Failure semantics designed as a feedback loop.

### 3. Anti-fingerprinting reframed as *coherence, not invisibility*

The Browser Identity Rules in CLAUDE.md are the most sophisticated stealth
philosophy in any studied repo, and they invert the usual approach:
- **"The browser must not contradict itself."** Everything it says about itself
  must survive cross-checking against another surface (user-agent vs `sec-ch-ua`,
  page vs its workers/iframes, screen vs window). "The goal is coherence, not
  invisibility — invisibility cannot be proven, while a contradiction is a fact."
- **"Never inject a fingerprint"** — no spoofed UA, no custom client hints — with
  the *measured reason*: a `user_agent=` override changes the string but not the
  client hints and never reaches service workers (upstream Chromium bug, linked).
  A browser telling the truth beats one caught lying.
- **"A proxy must contain every egress path, not just HTTP"** — WebRTC/UDP leaked
  around the proxy until explicitly closed; DNS and QUIC flagged as the same
  family. **"Verify identity changes by measurement"** against four named
  detectors, or it's a guess.

This is a general security lesson far beyond scraping: *coherence is provable and
falsifiable; invisibility is neither.* A system that presents a consistent true
story is more robust than one maintaining a lie across surfaces it doesn't
control — and every evasion claim must be measured, not assumed.

### 4. Safety by provable ownership

The most rigorous destructive-operation discipline studied. Because
`USER_DATA_DIR` accepts any path and rotations delete directories, the rules are
paranoid *with stated reasoning for each*:
- **"Nothing is moved or deleted under a root the server cannot prove it owns."**
  Every `rmtree`/`move`/`unlink`/`rename` on a user path routes through
  `_owned()`, backed by an explicit profile *claim* — capability-based
  authorization for filesystem operations, the brain/04 "provable ownership"
  idea made mechanical.
- **"Guard the source root, once, before any short-circuit"** — with the failure
  named: a check on a *derived* path "asks about a nested auth root the server
  deletes on purpose, while reading as protection." A check in the wrong place is
  worse than none because it looks like safety.
- **"The auth root is the blast radius, not the profile"** — the sidecars that a
  rotation takes live one level *above* the guarded dir, so the profile's
  emptiness proves nothing. Blast-radius reasoning, explicit.
- **"Expand and resolve together"** — or a symlink splits the profile from its
  sidecars.

The whole HEAD commit is this rule enforcing itself: "Refuse a profile root
nobody claimed."

## What else stands out

- **A CLAUDE.md that teaches invariants with their reasons**, not commands.
  Nearly every rule states the specific bug it exists to catch — the highest
  form of the agent-instruction genre (beyond gstack's decisions-with-scars: these
  are *invariants*-with-scars). It even scopes the tooling precisely: "use
  `uv run` not `uvx` so the process reflects your workspace."
- **Locale-independent detection.** Classification must key on URL patterns,
  attribute *presence* (`aria-label` exists), or structural counts — "never on
  text values like 'Connect'… the verb is locale-dependent; whether the
  attribute exists is not." The self-healing/robust-reference instinct
  (Scrapling, brain/04) applied to i18n brittleness.
- **Minimize DOM dependence by rule:** prefer innerText and URL navigation;
  when selectors are unavoidable use generic ones (`a[href*="/jobs/view/"]`),
  "never class names tied to LinkedIn's layout" — the brittle-reference hedge as
  a coding standard.
- **Serious singleton-daemon engineering** (election, lock, liveness, lease,
  owner) so one browser is shared safely across concurrent tool calls — the
  stateful-expensive-resource daemon (gstack's browser) with real distributed-
  systems care around ownership.

## Tradeoffs and the honest paragraph

- **Same ToS ceiling as linkedin_scraper** — authenticated session against a
  service whose terms forbid automation; the README's trademark/independence
  disclaimer is careful, and the design is scrupulously read-mostly with
  confirmation-gated writes, but the fundamental posture is ToS-adverse and the
  legitimacy ceiling (studies/ats-scrapers.md) applies. What's notable is how
  much *better* the engineering is here despite the same ceiling — the
  browser-coherence and ownership rigor are genuinely transferable regardless of
  the target.
- **12 daemon modules** is heavy; justified by safe browser sharing, but it's a
  lot of surface for a personal-use server (brain/06 right-sizing question —
  though the concurrency requirement is real).
- **Sponsor-funded, with a managed-cloud upsell** (Unipile) — disclosed, and the
  OSS server is fully functional standalone.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| MCP/tool interfaces are APIs for agents: annotate operation semantics (readonly/mutating), gate writes with confirmation, expose section-selection so the agent fetches only what it needs, hide internal args from the schema | tool annotations + `sections` + `exclude_args` | Any tool/MCP server design |
| Return partial failure in band: per-section results plus typed per-section errors that route toward a fix | `{sections, section_errors[issue_template_path]}` | Any multi-part agent tool |
| Stealth done right is coherence, not invisibility — a consistent true story is provable; a lie across surfaces is falsifiable; measure every evasion claim | Browser Identity Rules | Any anti-detection/anti-fingerprint work; security posture generally |
| Destructive operations need provable ownership (capability claim), guarded at the source root before any short-circuit, with blast radius reasoned explicitly | `_owned()` / profile claim | Anything that deletes/moves user-supplied paths |
| Write agent instructions as invariants-with-reasons: state the exact bug each rule catches | CLAUDE.md throughout | Every CLAUDE.md/AGENTS.md |
| Detect on locale-invariant signals (URL, attribute presence, structure), never on displayed text | Scraping Rules | i18n-robust automation and testing |

## Brain updates made

- `brain/05-apis-and-boundaries.md`: added a tool/MCP-interface subsection —
  annotate operation semantics, confirmation-gate mutations, section-selection
  for fetch-only-what's-needed, hide internal args, and return partial failure
  in band with typed per-part errors.
- `brain/09-agentic-engineering.md`: added "coherence, not invisibility"
  (provable-consistent-truth beats unprovable evasion; measure evasion claims)
  and "destructive ops need provable ownership guarded at the source root."
