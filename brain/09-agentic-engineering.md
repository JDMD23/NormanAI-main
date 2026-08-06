# 09 — Agentic engineering: discipline for AI-agent-driven development

Founded by the superpowers study (`studies/superpowers.md`). This domain has its own
physics: the "runtime" executing your process documentation is an LLM — capable,
fast, and prone to specific, *predictable* failure modes (rationalization under
pressure, context loss, optimistic self-reports). Elite agentic engineering is
ordinary engineering discipline re-aimed at that runtime.

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

## Calibrate autonomy by reversibility

Same principle as brain/07 (decide fast when reversible), operationalized:
- **Hard human gates** at irreversible or direction-setting points: design approval
  before code, merge/ship decisions, anything destructive.
- **Continuous execution** between gates — "should I continue?" check-ins on planned,
  reversible work waste the human's attention and the agent's momentum.
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
