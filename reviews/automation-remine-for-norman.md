# Re-mining the 28 studies for Norman — the automation lens

The original studies extracted *general* principles. This pass re-reads all 28
knowing what Norman actually is: a **scheduled, browser-driven, unattended
decision-support automation** (funding watcher 5×/day; Core sessions at
07:00/07:30/12:00/15:00/17:30; guarded windows, locks, leases, receipts,
exactly-once). The question here is narrower and more useful: *which specific
ideas keep this automation running correctly, unattended, for a year?*

Each item says: **the pattern → the repo that proved it → the exact Norman
subsystem it applies to → whether it's NEW (not yet in the plan/brain) or a
sharpening of something already flagged.**

Norman already has the seeds: `browser_coordination.py`, `fcntl` locks, leases,
`crm_runtime_dispatch.py`, `crm_signal_watcher.py`, `causal_outbox.py`, receipts.
Most of the below is the *mature form* of things you started, not a new graft.

---

## Tier 1 — automation-critical: what keeps unattended scraping alive

### A. Persistent, supervised browser daemon  → **gstack + linkedin-mcp-server** → `browser_coordination.py`, the browser lanes  → **NEW (biggest single find)**

Norman cold-starts browser work per session across three sources. gstack's
architecture: a **long-lived Chromium daemon** the lanes talk to over localhost —
first call ~3s, every call after ~100–200ms, with persistent cookies/tabs across
commands. linkedin-mcp-server adds the coordination Norman half-built: **daemon
election, lock, lease, liveness/health-check, and version auto-restart** so one
browser is shared safely across concurrent lanes and stale binaries can't linger.
For a system doing dozens of company checks × 5 sessions/day, warm sessions and
persistent logins turn a fragile per-call login dance into one supervised
resource. This unifies `browser_coordination` + `browser_readiness` + your locks
into the proven shape. **Adopt this as the browser substrate of the rebuild.**

### B. Self-healing selectors  → **Scrapling** → Careers/Crunchbase/LinkedIn parsers → **NEW (the durability keystone)**

The #1 silent killer of scheduled scraping is a **site redesign breaking a
selector** — the lane runs, finds nothing, writes nothing, and the board quietly
goes stale. Scrapling stores an element *fingerprint* at bind time and, when the
selector fails, **re-derives the element by similarity** against the new DOM — no
code change, no LLM. For Norman this is what lets the lanes survive Crunchbase and
LinkedIn UI churn unattended. Pair with the **capability ladder** (plain HTTP →
real browser → stealth): fetch cheaply first, escalate to the daemon browser only
when a source demands it, so you spend the expensive path only where required.
One caveat from the study: **surface confidence when a selector re-binds** — a
silent partial match is a phantom fact (brain/10 #8).

### C. Silent-failure detection via real observability  → **OpenTelemetry (+ claude-mem)** → the whole scheduled surface → **NEW (the operational blind spot)**

Norman has *receipts* (forensics after the fact) but no *alerting* (notice in
real time). Scheduled automation's worst failure mode is going quiet. OTel's
model closes it: a **correlation ID per company per session**, traces across
lanes, and alerts on the **four golden signals** — so "did the 12:00 LinkedIn
closeout actually run, and did enrichment throughput drop?" is answerable in
seconds, not discovered weeks later as a stale board. claude-mem's lesson is the
same in one line: **a capture daemon is a distributed system — supervise it or it
silently stops remembering.** This is the runtime half of the `evidently` gap
(the other half being score/input *drift*). **Instrument the substrate from day
one; retrofitting telemetry is misery.**

### D. Autonomous-loop discipline for the Core session  → **autoresearch** → `crm_maintenance_run.py`, dispatch → **SHARPENS (you built the loop; adopt the rigor)**

Norman's daily maintenance *is* an autonomous loop, and autoresearch is the
reference design for one. Map it directly:
- **Frozen judge** — the agent/loop must not be able to edit the scoring config or
  the eval. (You already do this: scoring is config-as-formula, not agent-authored.
  Keep it structurally impossible to violate.)
- **Fixed-budget normalization** — the 15-min execution window + lane allowance is
  exactly autoresearch's fixed-budget-per-experiment; make it the hard kill
  criterion.
- **Bounded crash policy** — trivial failure → retry; broken → log and move on; N
  failures → stop and surface. (Your Blocked/Manual outcomes are this — formalize
  the ladder.)
- **Git-as-ledger / negatives are the record** — your receipts are the ledger;
  make sure *discards and crashes* are logged as first-class, not just successes.

---

## Tier 2 — sharpen scoring, identity, and cost

### E. RapidFuzz as the actual entity-resolution engine  → **RapidFuzz** → identity resolution, `crm_dedup_scan.py`, identity-conflict reason code → **NEW (a concrete tool, not just a pattern)**

brain/10 #6 makes identity resolution load-bearing. RapidFuzz is a *library* you
can use directly: fast fuzzy company-name matching for dedup, rediscovery
idempotency, and detecting the "identity conflict" Review-Required case. It pairs
with (not replaces) the deeper Splink study — RapidFuzz for the string-similarity
layer, Splink for probabilistic multi-field linkage.

### F. Bounded-investigation shape for Second Pass  → **orca** → `crm_second_pass_agent.py` → **SHARPENS**

Norman already splits deterministic (Fit Score) from LLM (Second Pass) — orca is
the disciplined version of exactly that: **cheap deterministic baseline runs
unconditionally; LLM drill-down is a budgeted, justified exception** ("don't fetch
out of curiosity, max N calls"), with **the per-call cost in the tool
description** so the model weighs it, and a **read-through cache** so the budget
never re-buys data you have. Apply verbatim to Second Pass.

### G. Provenance labels + deterministic-first extraction  → **graphify** → evidence/claims layer, source parsing → **SHARPENS (brain/10 #4)**

Sharpen Norman's evidence from "has a source" to graphify's
**extracted / inferred / ambiguous** labels, routing *ambiguous* to your
Review-Required queue automatically. And **extract deterministically wherever a
parser exists** (parse Crunchbase's structured data for free; reserve the LLM for
genuine interpretation) — cutting both cost and the hallucination surface that
threatens the system of record.

### H. Contract tests per source  → **ats-scrapers + MiroFish** → the three lanes → **SHARPENS (F5)**

Pair a **contract test with each source adapter** (expected HTML/JSON shape,
fields, pagination) so an upstream Crunchbase/LinkedIn change **fails your CI as a
red test instead of silently corrupting enrichment**. MiroFish did this for a SaaS
dependency; ats-scrapers does it per provider across 50 sources.

### I. Session-as-artifact auth  → **linkedin_scraper** → the logged-in lanes → **NEW (small, correct boundary)**

Push login *out* of the lane code: a setup step mints a reusable `session.json`;
lanes load it. Credentials touch one path, sessions survive across the 5 daily
runs, and the scraping code never handles passwords. (Composes with the daemon in
A and the credential-security exposure I flagged.)

---

## Tier 3 — operator surface and governance (lower automation weight)

- **rendergit dual-reader** → give the daily review an **LLM view** beside the
  human cards, so an agent can consume board state cheaply (brain/09).
- **mattpocock CONTEXT.md** → Norman has heavy domain vocabulary (Status meanings,
  Need-\* markers, reason codes) — a single **ubiquitous-language glossary** keeps
  every doc, agent prompt, and property name consistent.
- **agency-agents CI-checked duplication** → the config-consistency check for the
  Fit weights / job-map / views (the F3 authority-map generator).
- **ui-ux-pro-max / taste-skill** → the operator card is a UI; anti-default
  discipline and design-knowledge retrieval improve the operator experience if you
  ever move cards beyond Notion.
- **JustHireMe eval harness, Hypothesis property tests, OTel rationale.md** →
  already in the plan (F1, F2, F7).

---

## Honest bottom line

The re-mine surfaced **four automation-critical ideas I had not connected to
Norman** — the persistent supervised **browser daemon** (A), **self-healing
selectors** (B), real **silent-failure observability** (C), and **RapidFuzz** as a
concrete identity engine (E) — plus several sharpenings (D, F, G, H, I). A, B, and
C are the three that most determine whether Norman runs unattended for a year
without a human noticing it quietly died. They should be **foundational substrate
in the rebuild**, not features added later. None of this changes the design in
brain/10 — it's the machinery that makes that design survive contact with real,
churning, logged-in websites on a schedule.
