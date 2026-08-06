# Study: superpowers

- **Repo:** https://github.com/obra/superpowers
- **Studied:** 2026-08-06 at commit `44c9b2d`
- **What it is:** A complete software development methodology packaged as ~14 composable
  agent skills (brainstorm → plan → subagent-driven execution → review → verify → ship),
  auto-triggered via a session-start bootstrap, portable across ~10 coding-agent harnesses.
  By Jesse Vincent (obra) / Prime Radiant.
- **Why it was worth studying:** The user's goal is optimizing their workflows with
  Claude; this is the most mature public example of "methodology as code" for agents.

## Architecture at a glance

```
hooks/session-start          # injects using-superpowers skill into every session (per-harness JSON)
skills/using-superpowers     # the bootstrap: "if a skill might apply, you MUST invoke it"
skills/<workflow skills>     # brainstorming → using-git-worktrees → writing-plans →
                             #   subagent-driven-development | executing-plans →
                             #   test-driven-development → requesting/receiving-code-review →
                             #   verification-before-completion → finishing-a-development-branch
skills/writing-skills        # the meta-skill: TDD applied to writing skills themselves
.claude-plugin/ .codex-plugin/ .cursor-plugin/ ...   # thin per-harness adapters, one skills source
tests/                       # shell tests for plugin infrastructure (hooks, scripts, sync)
evals/ (external repo)       # behavioral evals: drives real agent sessions, LLM-judged compliance
```

The load-bearing insight: **the skills are the product; everything else is a delivery
mechanism.** One canonical skills directory, per-harness shims, and a bootstrap whose
only job is making skill invocation mandatory rather than optional.

## What this codebase does exceptionally well

1. **Process documentation is treated as code — with TDD.** `skills/writing-skills/SKILL.md`
   maps RED-GREEN-REFACTOR onto doc-writing: run a pressure scenario *without* the skill
   and record how the agent fails (RED), write the skill targeting those exact failures
   (GREEN), then close new rationalization loopholes (REFACTOR). Behavioral changes to
   skills require before/after eval evidence (drill harness driving real tmux sessions,
   LLM verifier). "Skills are not prose — they are code that shapes agent behavior."

2. **They discovered and fixed an interface-leak failure mode specific to prompts.**
   If a skill's frontmatter description *summarizes its workflow*, agents follow the
   summary and never read the body (documented in the SDO section: a description
   mentioning "code review between tasks" caused one review instead of the mandated
   two). Fix: descriptions state **only triggering conditions**, never process. This is
   Hyrum's Law operating on documentation — any observable surface becomes the contract.

3. **Rationalization tables: defensive design against the runtime's known failure modes.**
   TDD, systematic-debugging, and verification skills each contain an "Excuse → Reality"
   table pre-refuting the *specific* excuses agents produce under pressure ("too simple
   to test", "I'll test after", "emergency, no time for process"). These were harvested
   from observed baseline failures, not imagined. There's even a research-cited
   `persuasion-principles.md` explaining which compliance techniques work on LLMs and
   when each is appropriate.

4. **Durable external state beats conversational memory.** `subagent-driven-development`
   mandates a git-ignored ledger file per plan because "conversation memory does not
   survive compaction" — and names the observed failure (controllers re-dispatching
   entire completed task sequences, "the single most expensive failure observed").
   Recovery rule: trust the ledger and `git log` over your own recollection.
   Write-ahead-log thinking applied to agent orchestration.

5. **Constructed context per subtask, never inherited context.** Each task gets a fresh
   subagent with precisely-crafted instructions ("they should never inherit your
   session's context or history"). Plus explicit model-tiering (cheap models for
   mechanical tasks, capable ones for architecture/final review), an escalation ladder
   (fix rounds 4–5 get a fresh implementer on a stronger model), and a circuit breaker
   (5 rounds max, then adjudicate findings or report BLOCKED to the human).

6. **Evidence-before-claims as a hard gate.** `verification-before-completion`: no
   success claim without running the proving command *in the current message*; agent
   self-reports are explicitly untrusted ("Agent said success → verify via VCS diff").
   Regression tests must be verified red-green by reverting the fix.

7. **Human gates only at irreversibility and genuine ambiguity.** Design approval is a
   hard gate; between tasks, execution is explicitly continuous ("'Should I continue?'
   prompts waste their time"). Conflicts found in a plan are batched into one question,
   not one interrupt per discovery.

8. **Docs as contributor access control.** The repo's CLAUDE.md is written *to agents*
   ("Stop. Read this section before doing anything"), citing a 94% PR rejection rate,
   requiring provenance disclosure (model, harness, plugins) and proof a human reviewed
   the diff. A novel genre: maintainer defense against AI-slop PRs, enforced at the
   layer where the slop is generated.

## Questionable calls and tradeoffs

- **Deliberate dogmatism.** "If there is even a 1% chance a skill applies, you MUST
  invoke it"; "delete code written before tests — no exceptions"; brainstorming gates
  *every* change, "a config change" included, behind design approval. By my brain's
  standards (00: judgment beats rules) this is over-rigid — but it's a *reasoned*
  tradeoff: the runtime (an LLM under pressure) reliably rationalizes its way out of
  soft rules, and their evals showed absolutist framing is what holds. They explicitly
  diverge from Anthropic's published skill guidance and demand eval evidence to change
  tuned wording. Rules-over-judgment is correct when the executor's judgment is the
  documented failure mode. The cost is real, though: heavyweight ceremony on genuinely
  trivial tasks, and "delete and re-implement" burns work that tests-after could salvage.
- **Plans contain the implementation.** writing-plans requires complete code in every
  step, sized for "an enthusiastic junior engineer with poor taste, no judgement, and
  an aversion to testing." Planning is ~doing the work up front; the payoff is cheap
  parallel/mechanical execution and reviewability. Right for autonomous multi-hour runs;
  overkill for interactive pairing.
- **Graphviz dot as control flow in prose docs** — machine-precise flowcharts agents
  can't misread as loosely as prose. Unusual, apparently effective, but unreadable-ish
  for humans skimming.
- **Telemetry via logo fetch** in the brainstorming visual companion — disclosed and
  opt-out, but piggybacking telemetry on an asset load is the kind of cleverness that
  erodes trust; a plain opt-in ping would cost little.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Agent-facing docs are code: baseline the failure, write, verify, regression-test | writing-skills TDD mapping; drill evals | Any CLAUDE.md, skill, or system prompt you rely on; overkill for one-off prompts |
| Never summarize a process in its trigger/description — agents will execute the summary | SDO section, two-reviews bug | Skill frontmatter, tool descriptions, runbook titles |
| Pre-refute the executor's specific rationalizations, harvested from real failures | Excuse/Reality tables | Discipline-enforcing docs (TDD, verification); noise if invented rather than observed |
| Long-running agent work needs a write-ahead ledger outside the context window | SDD ledger + "trust git log over recollection" | Any multi-hour agent workflow; unnecessary for single-turn tasks |
| Construct subagent context; never let it inherit; tier models; cap retry loops with escalation + circuit breaker | SDD model-selection and fix-round rules | Multi-agent orchestration of every kind |
| No success claims without fresh proving-command output; distrust agent self-reports | verification-before-completion | Universal — this is brain/00 "report outcomes faithfully" made mechanical |
| Put human gates at irreversible decisions only; batch questions; otherwise run continuously | brainstorming HARD-GATE vs. SDD continuous execution | Calibrates autonomy for any agent workflow |
| Absolutist rules outperform judgment-framing *when the executor's judgment is the failure mode* | Their eval-tested divergence from official guidance | Agent instructions; do NOT import into human-facing engineering docs |

## Brain updates made

- `brain/09-agentic-engineering.md`: **new doc** — engineering discipline for
  AI-agent-driven development workflows. This study is its founding evidence; the
  domain (prompts-as-code, context/state management for agents, autonomy calibration,
  verification gates) wasn't covered by 00–08.
- `brain/05-apis-and-boundaries.md`: no edit — the description-leak finding is recorded
  in 09 as the prompt-layer instance of Hyrum's Law already stated in 05.
