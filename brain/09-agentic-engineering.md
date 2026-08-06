# 09 — Agentic engineering: discipline for AI-agent-driven development

Founded by the superpowers study (`studies/superpowers.md`), extended by the ECC
study (`studies/ecc.md`). This domain has its own physics: the "runtime" executing
your process documentation is an LLM — capable, fast, and prone to specific,
*predictable* failure modes (rationalization under pressure, context loss,
optimistic self-reports). Elite agentic engineering is ordinary engineering
discipline re-aimed at that runtime.

## Enforce mechanically; persuade only where judgment lives

Prose instructions are probabilistic — observed compliance for skill-style guidance
runs ~50–80%; a harness hook fires 100% of the time (ECC's measured rationale for
moving from skill-based to hook-based observation). That yields a hierarchy for any
rule you want an agent to follow:

1. **Hook / hard block** — if the rule is mechanically checkable, enforce it in the
   harness: block `--no-verify`, block edits to linter configs (and *point at the
   right fix*: "fix the code, not the config"), gate dangerous commands. This is the
   agent-layer twin of brain/04's "constraints in the database, not the app."
2. **Eval-tested prose** — for rules requiring judgment, use behaviorally tested
   wording (superpowers' TDD-for-docs), including pre-refuted rationalizations.
3. **Plain prose** — acceptable only for low-stakes preferences.

Putting a discipline-critical rule one level lower than it could live is a design
defect: every "MUST" in a doc that a regex could enforce is compliance left to chance.

## Agent memory that learns must be scoped and evidence-weighted

The working design (ECC's instinct system) for "the agent learns my preferences":
- **Atomic units** — one trigger, one action; never essay-sized "lessons."
- **Confidence scores** that rise with repeated observation and *fall on user
  correction or disuse* — memory without decay accumulates stale beliefs.
- **Observation via deterministic capture** (hooks logging real behavior), analyzed
  by a cheap background model — not self-reported "what I learned" summaries.
- **Project-scoped by default.** Global-by-default memory cross-contaminates
  (React habits leaking into Python repos). Promote to global only on evidence:
  the same pattern independently observed in multiple projects at high confidence.
The general principle: learned state is derived data (brain/04) — it needs
provenance, a recompute path, and an invalidation story, or it becomes corruption.

## Prompts and process docs are code

Anything that shapes agent behavior — CLAUDE.md, skills, system prompts, subagent
briefs — is code and earns code's lifecycle: version control, review, and **tests**.
The TDD loop transfers directly:
1. **RED:** run the scenario *without* the doc; record exactly how the agent fails
   and the excuses it generates.
2. **GREEN:** write the doc targeting those observed failures — not imagined ones.
3. **REFACTOR:** when the agent finds a new loophole, plug it and re-verify.
Behavioral wording that has been tuned this way is load-bearing; don't "clean it up"
without evidence, the same way you don't reformat a regex you don't understand.

## Interfaces leak harder with LLM consumers

Hyrum's Law (brain/05) applies with more force, not less: an agent will treat any
observable text as the contract. The documented failure: a skill description that
*summarized its workflow* caused agents to execute the summary and skip the full
process. Rules that follow:
- Triggers/descriptions state **when to invoke**, never what the process is.
- Anything you don't want executed as instructions shouldn't look like instructions.
- The doc the agent actually loads is the API; everything else is dead weight —
  token cost is interface cost, so compress what loads every session.
- **A skill/prompt catalog is itself an API surface.** The agent selects from it by
  reading descriptions, so every entry taxes the selection of every other entry.
  Unbounded, uncurated growth (281 mixed-quality skills — ECC) degrades the whole
  catalog; curation with a quality gate (14 eval-tested skills, domain content
  refused — superpowers) is the "when in doubt, leave it out" rule from brain/05
  applied to prompts. Catalog facts (counts, indexes) must be generated from source:
  ECC states three different catalog sizes in three hand-maintained docs.

## Design against the runtime's failure modes

- **Rationalization under pressure.** Soft rules ("prefer", "consider") reliably lose
  to time pressure and sunk cost. For discipline-critical steps, absolutist framing
  plus a pre-refutation table of the *observed* excuses ("too simple to test" →
  reality) measurably holds where judgment-framing folds. Inversion of brain/00's
  "judgment beats rules," and correctly so: rules beat judgment **when the executor's
  judgment is the documented failure mode**. Keep the absolutism in agent-facing docs;
  don't let it leak into human engineering culture.
- **Optimistic self-reports.** No success claim without fresh proving-command output;
  a subagent's "done, all tests pass" is verified against the VCS diff and a real test
  run, never trusted. Regression tests get red-green verified (revert fix → must fail).
- **Context loss.** Conversation memory does not survive compaction. Long-running
  work keeps a **write-ahead ledger** in the filesystem (progress file + git history);
  on recovery, the ledger and `git log` outrank the agent's recollection. The failure
  this prevents — re-executing hours of completed work — is the expensive one.

## Context is a scarce, constructed resource

- **Construct, don't inherit.** Subagents get precisely the context their task needs,
  never the session's accumulated history. Inherited context pollutes focus and burns
  the orchestrator's own window. This is information hiding (brain/01) applied to
  context windows: the task brief is the interface; the session history is the
  implementation detail it hides.
- **Fresh agent per task** beats one long-lived agent accumulating drift; the
  orchestrator holds the plan, workers hold one task each.
- **Tier models by task:** cheap/fast for mechanical well-specified work, capable for
  architecture, review, and judgment. Explicit tier choice per dispatch — defaults
  silently pick the most expensive.
- **Escalate, then break.** Retry loops get a ladder (fresh worker, stronger model
  after N failures) and a circuit breaker (hard round cap → adjudicate or report
  BLOCKED to the human). Unbounded fix loops are the agentic version of
  retry-without-backoff (brain/02).

## Diff discipline: agents are guests in the codebase

The agent default for edits is **surgical** (karpathy-skills' formulation): every
changed line traces directly to the request; match existing style even when you'd
choose differently; don't "improve" adjacent code, comments, or formatting; mention
pre-existing dead code, don't delete it; remove only the orphans *your* change
created. This deliberately inverts brain/03's boy-scout rule, and the resolution is
ownership: boy-scouting is for owners whose cleanups are cheap to review and trusted;
an agent's unrequested improvements inflate the diff a human must review and spend
trust the task didn't earn. An agent granted standing maintenance duties by its
human is an owner for that scope; otherwise, guest rules apply.

## Calibrate autonomy by reversibility

Same principle as brain/07 (decide fast when reversible), operationalized:
- **Hard human gates** at irreversible or direction-setting points: design approval
  before code, merge/ship decisions, anything destructive.
- **Continuous execution** between gates — "should I continue?" check-ins on planned,
  reversible work waste the human's attention and the agent's momentum.
- **Autonomy is downstream of verifiability.** Transform imperative tasks into
  verifiable goals before starting ("add validation" → "write tests for invalid
  inputs, then make them pass"); with a strong success criterion the agent can loop
  independently, while "make it work" guarantees clarification round-trips.
- **Batch questions.** Conflicts and ambiguities found during a scan are presented as
  one consolidated question, not a stream of interrupts.

## Plans for agent execution are a different genre

A plan a capable human executes can sketch; a plan for autonomous agent execution is
written for "a skilled developer with zero project context and poor taste": exact file
paths, complete code, exact commands with expected output, explicit
consumes/produces interfaces between tasks, no placeholders ("add error handling" is
a plan failure). The cost is that planning approaches doing the work; the payoff is
mechanical, parallelizable, reviewable execution and multi-hour autonomy. Use this
genre when execution is delegated and unattended; don't impose it on interactive work.

## The workflow skeleton that works

Distilled shape of a production-grade agent dev loop:
clarify intent → **approved design** (gate) → isolated workspace (worktree/branch) →
fine-grained plan → per-task: fresh worker + review (spec compliance, then quality) →
verification with evidence → whole-branch review → **human ship decision** (gate).
Adopt pieces proportionally to stakes and task size (brain/00: scope honesty) — the
full ceremony for autonomous feature builds, a fraction of it for a one-file fix.
