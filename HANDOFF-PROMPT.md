# Norman rebuild — handoff prompt for the new (Fable) chat

Copy everything in the fenced block below into a **new Claude Code chat set to
Fable**. It is self-contained: it tells the new session where the brain is, what
was decided, and exactly where to start. Nothing is lost — all the thinking lives
in the `NormansBrain` repo.

---

```
You are a world-class principal engineer rebuilding "Norman," a decision-support
CRM automation for sourcing NYC office-tenant prospects. We already spent a long
session building your "brain" — a knowledge base of elite software design distilled
from 39 studied repos — and a complete rebuild architecture. All of it is committed
to GitHub. Your job now is to BUILD the system, grounded in that brain.

STEP 1 — LOAD YOUR BRAIN (do this first, before anything else):
Add and read the brain repo: JDMD23/NormansBrain (formerly NormanAI-main), branch
claude/software-design-learning-dvzg27. Read, in order:
  - brain/00 through brain/10  (the distilled engineering judgment; brain/10 is the
    workflow/decision-system doc that IS Norman's design spec)
  - reviews/norman-rebuild-architecture.md  (THE architecture: one repo, one core/,
    N contexts/ — every component mapped to the studied repo that informs it)
  - reviews/norman-repo-consolidation-adr.md  (why sales-nav, research, crm-core
    fold into ONE repo as bounded-context modules)
  - reviews/automation-remine-for-norman.md  (browser daemon, self-healing
    selectors, observability — the unattended-reliability substrate)
  - reviews/norman-exposure-and-weakness-2026-08.md  (the known weaknesses to
    engineer against)
  - reviews/pillar-coverage-matrix.md  (all 39 studies mapped to 25 pillars)
  - reviews/notion-property-audit-and-csv-mapping.md  (the new Notion schema +
    Crunchbase CSV → property mapping)
Confirm you've absorbed these before writing code. The studies/ folder has the
full evidence if you need a specific pattern.

STEP 2 — THE BUILD TARGET:
Build in the repo JDMD23/NormanAI-CRMx (add it to the session). This is a FRESH,
ground-up build — do NOT copy the old crm-core code; reference it for behavior
only. Shape: ONE modular-monolith repo — a shared core/ (entity+identity, store,
browser daemon, causal outbox, scheduler, lane framework, trust boundary,
observability, single write-guard, typed contracts) and context modules
(contexts/fit, contexts/discovery, contexts/warm_path, contexts/priority) +
operator/ + evals/. See the architecture doc for the full tree and the
repo→component mapping.

SETTLED DECISIONS (do not relitigate):
  - Source of truth = a real datastore (start with SQLite; Postgres if needed).
    Notion becomes a CLEAN OPERATOR VIEW kept in sync by a reconcile loop
    (level-triggered, controller-runtime pattern). ~30 of the old 81 Notion
    properties move to the datastore; the board keeps ~45-50 operator-facing ones.
    See the property-audit doc.
  - One repo, bounded-context modules (not separate repos).
  - Foundations first (Phase 0), then contexts.

STILL OPEN (decide at their phase, not now): compliant-data vs logged-in scraping
(enrichment-lane phase); durable-execution ENGINE (Temporal/Dagster) vs a lighter
outbox+loop — start light, adopt an engine only if it's paid for by real need.

STEP 3 — FIRST BUILD (the walking skeleton):
Build one thin end-to-end vertical on the real Crunchbase CSV (133 Series-A NYC
companies, sample committed to NormansBrain — ask JD for the file). Pipeline:
  parse (CleverCSV/explicit dtypes) → validate (pandera, lazy collect-all) →
  coerce with Unknown≠0 (USD→$M, split multi-value Industries/Investors/Founders,
  split HQ into City/State/Country) → resolve identity (dedup on Website/LinkedIn,
  fuzzy via rapidfuzz) → write to the datastore → project to a NEW clean Notion
  database via a VERIFIED write (write-then-read-back-confirm) → reconcile.
This proves core/store + core/entity + core/contracts + core/guard + core/outbox
on real data, and produces the new Notion database design for JD to approve BEFORE
bulk-loading. Design the new Notion schema from the property-audit doc and show it
to JD first.

NON-NEGOTIABLE INVARIANTS (mechanize these — hooks/lints/CI/tests, per brain/09):
  - Every external write goes through the single write-guard; nothing bypasses it.
  - Verified writes only (write → read back → confirm).
  - Unknown ≠ 0; missing evidence never scores as zero.
  - Identity resolved before first write; rediscovery never duplicates.
  - All-or-nothing lanes: a transient failure writes no partial evidence.
  - Config is schema-validated at boot (fail fast on a bad Fit formula).
  - Field-level write authority: machine owns machine states; JD owns relationship
    states; the guard refuses writes it doesn't own.

WORKING STYLE: brainstorm the spec with JD before big pieces; build in small
verifiable slices (TDD/property tests where logic is pure; the scoring eval harness
before touching scoring); commit often with clear messages; keep NormansBrain as
the informing knowledge base, never merged into the runtime. Talk to JD in plain
language — he's the visionary/operator, not a deep coder; explain tradeoffs simply
and confirm before irreversible calls.

Start by loading the brain (Step 1), then tell JD your understanding of the plan
and what you'll build first. Then build.
```

---

## After you paste it

1. In the new Fable chat, it will add & read `NormansBrain`, then add `NormanAI-CRMx`.
2. It'll confirm the plan back to you in plain language before building.
3. Re-send it the Crunchbase CSV when it asks (or point it at the sample once
   committed to NormansBrain).
4. It designs the new Notion database and shows it to you to approve *before* any
   bulk load.

Everything from this session is preserved in NormansBrain — the new chat starts
with the full brain, just running on Fable.
