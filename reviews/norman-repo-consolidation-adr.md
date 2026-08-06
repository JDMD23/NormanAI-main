# ADR: Norman repo consolidation — one system, one repo, bounded-context modules

**Status:** Proposed (governs the ground-up rebuild)
**Decision owner:** JD
**Context gathered:** crm-core (the Fit/scoring system) + NormanAI-sales-nav (the
warm-path/relationship engine), with more sibling repos expected.

## Decision

**Fold the sibling systems into one repository** with a **shared core** and one
**bounded-context module per concern** — do *not* keep them as separate repos.
Sales Nav is the first test case and the verdict is unambiguous: it is a
**fourth lane family of Norman, not a separate system.**

## Why (evidence, not preference)

### Sales Nav and crm-core are already one system wired through the worst possible seam

- **Cross-repo path import.** `sn_notion.py` does
  `CRM = ~/Projects/NormanAI-crm-core` and loads crm-core's `notion_client.py`
  *by absolute filesystem path*. This is a hidden, physical, unversioned
  dependency between two repos (brain/01 hidden coupling at its most severe): if
  crm-core moves, renames, or refactors that file, Sales Nav breaks silently, and
  nothing — no import graph, no package manager, no CI — can see the link.
- **Shared datastore as contract.** Sales Nav reads crm-core's shelves
  (`Status ∈ {Top Pursuit, Prospect}`, joins on Notion page ID) and writes back to
  the *same Notion company pages*. Two components sharing a database schema as
  their contract is the tightest coupling in software (brain/04) — and here they
  share it with **no shared schema module**, so a renamed Notion property breaks
  the writeback with no red test.
- **Duplicated invariant machinery.** Sales Nav reimplements crm-core's
  discipline — never-writes-Status, Unknown≠0, human pace ("crm-core shape"),
  success/retry/park lane outcomes, the `Need-*` checkbox work queue, AppleScript
  Chrome ("crm-core LinkedIn-lane style") — in its own `lib/chrome.py`,
  `lib/pace.py`, `lib/state.py`. The same invariants enforced twice will diverge
  (brain/10; the ats-scrapers registry finding says this must be one BaseLane).
- **A field-ownership conflict is already flagged in Sales Nav's own spec**
  (Phase 3 Growth Insights: "crm-core's LinkedIn lane owns headcount fields. Do
  not double-own fields."). That is brain/10 #3 (conditional write-authority) —
  trivial to enforce with one write-guard in one codebase, a cross-repo hazard
  as two systems reaching into the same Notion pages.

### Keeping them separate is the distributed-monolith anti-pattern

Two repos that share a datastore, import each other by path, and duplicate each
other's machinery have **all the costs of separation** (schema drift, duplicated
code, cross-repo coordination, the path-import landmine) and **none of the
benefits** — they *cannot* deploy or evolve independently, because Sales Nav
literally cannot run without crm-core's data and code. That is precisely
brain/08 #1: the distributed monolith. Merging removes the costs and loses
nothing real.

### The three legitimate reasons to split — none apply

Split a component into its own repo only if it is (brain/02, brain/07): a
**reusable library with external consumers** (Sales Nav is JD-specific, no),
has a **different runtime or release cadence** (same Python + logged-in Chrome +
Notion; its re-scan cadence is just another scheduled lane, no), or is a
**shared dependency of multiple systems** (it is strictly downstream of crm-core,
no). Zero of three.

## But fold in as a bounded context, not a script merge

Sales Nav *is* a genuinely distinct **bounded context** (Evans/DDD): the
relationship/angle graph — personas, intro-node ranking, connection tiers, a
people graph in SQLite (v2: a promoted People entity) — is a different model from
Fit/scoring, and it owns *different fields*. So the rebuild is:

```
norman/                      one repo, one deployable (modular monolith)
  core/                      shared substrate — used by every lane family
    entity model + identity resolution (the join key, resolved before any write)
    browser daemon (persistent, supervised)          [automation-remine A]
    self-healing selectors                            [automation-remine B]
    causal outbox + receipts + observability          [automation-remine C]
    Notion write-guard (the ONE write path)           [brain/10 #3]
    lane framework (BaseLane: success/retry/park, Need-* queue, human pace)
    notion schema contract (the shared property map — imported, never re-typed)
  contexts/
    fit/          Crunchbase · Careers · LinkedIn lanes → Fit Score → Status
    warm_path/    Sales Nav lanes → personas · warm paths · intro nodes → warm-path fields
    (future siblings land here as new contexts)
```

**Write-authority is field-level and enforced in one guard** (brain/10 #3):
the Fit context owns Status / Fit / headcount; the Warm-Path context owns
Warm Path Summary / Connectivity / Workplace POC; the guard refuses any lane a
field it doesn't own. This *dissolves* the Phase-3 conflict instead of managing
it across repos.

**A per-context deployment/policy boundary is still available inside one repo.**
Sales Nav reads JD's personal network and is JD-triggered with explicit-approval
scheduling — a more sensitive autonomy posture. That is a *policy on the lane*
(schedule, approval gate, blast-radius), not a reason to split the code. One repo,
independent lane schedules.

## Timing makes this nearly free now

Sales Nav is a **scaffold** (parsers pending selector development, ~1,800 lines,
little accreted). Folding it in during the ground-up rebuild costs almost nothing;
letting it grow its own divergent browser/pace/state/outbox machinery makes it
expensive later. This is the moment to make the call — before the duplication
ossifies.

## Consequences

- One `notion-schema` contract module both contexts import → property renames are
  a one-line change with a red test, not a silent cross-repo break.
- One browser daemon, one outbox, one pace engine, one write-guard → the
  automation-remine substrate (A/B/C) is built once and every context inherits it.
- The cross-repo path import is deleted outright.
- New sibling repos are evaluated against this same test: **shared entity/datastore
  + inherited discipline ⇒ a context module here; genuinely independent
  runtime/consumers ⇒ its own repo.** Apply per repo as JD sends them.

## Open

Remaining sibling repos (JD is sending them one at a time) each get this same
evaluation appended here. Default expectation, given the pattern: they are
context modules of the one Norman system, not separate systems.
