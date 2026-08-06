# 09 — Agentic engineering: discipline for AI-agent-driven development

Founded by the superpowers study (`studies/superpowers.md`), extended by the ECC
study (`studies/ecc.md`). This domain has its own physics: the "runtime" executing
your process documentation is an LLM — capable, fast, and prone to specific,
*predictable* failure modes (rationalization under pressure, context loss,
optimistic self-reports). Elite agentic engineering is ordinary engineering
discipline re-aimed at that runtime.

## The economics update: write-cost collapsed, carry-cost didn't

AI-assisted coding changed one term in every build-vs-skip tradeoff, and only one
(gstack's "Boil the Ocean" ethos, honestly resolved). **Write-cost collapsed**:
decisions that hinged on effort-to-produce — skipping tests, deferring error
paths, shipping the 90% version of the task at hand — should flip toward
completeness, because the delta now costs minutes. "That would take too long" is
a stale reflex when applied to the current task's edge cases. **Carry-cost did
not collapse**: every line still must be read, reviewed, operated, secured, and
evolved — by humans and by agents with finite context — so speculative
abstractions, extra dependencies, and unrequested features cost what they always
cost. The rule: *be complete on the task at hand; keep the old discipline on
scope and abstraction.* YAGNI survives because it was never about typing effort
(brain/00, /01, /07 stand unmodified). Note also which work compresses least —
architecture and design (~5x vs ~100x for boilerplate) — judgment remains the
bottleneck, which is this brain's founding premise.

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

The hierarchy also applies *inside* a single agent role (Understand-Anything's
graph-reviewer): a QA agent reviewing structured artifacts should first **write
and run a deterministic checker** for everything mechanical (schema, enums, ID
conventions), then spend judgment only on the residue — with exit codes meaning
"the script ran," never "the content is valid." Don't ask an LLM to eyeball
3,000 nodes for conformance.

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

Memory splits into two systems with different physics (ECC = procedural,
claude-mem = episodic; design them separately, a complete agent needs both):
- **Procedural** — learned behaviors ("how do I usually do X here?"): atomic,
  confidence-scored, project-scoped, as above.
- **Episodic** — what happened ("what did we do about X in March?"): compress at
  *write time* (raw transcripts are for recovery, not retrieval), index by time
  as a first-class axis, and retrieve via **index-then-fetch**: a search returns
  compact IDs (~10x cheaper), full records are fetched only for hits that survive
  filtering. That retrieval rule generalizes to every agent-facing search tool —
  memory, docs, tickets, logs. And a hook-fed capture daemon is a distributed
  system: supervise it (health checks, graceful shutdown, atomic restart) or it
  silently stops remembering.

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

## Skills are knowledge deltas, packaged with progressive disclosure

What belongs *in* an agent-facing doc (anthropics/skills, from their production
document skills): not what the model already knows (wasted tokens), not generic
best practice (noise), but the **delta between model belief and ground truth** —
footguns, each harvested from an observed failure and compressed to a rule ("the
model knows the API; these are the footguns"). Superpowers' rationalization tables
are the same principle for behavior; this is it for technical knowledge. The third
delta species is the **output prior** (taste-skill): name the model's
collapsed-mode defaults explicitly — the AI-purple gradient, the three equal
feature cards, the boilerplate test shape — and forbid them. Slop is mode
collapse, and escaping a default requires naming it.

Two corollaries (obsidian-skills): **the format/API owner should ship the
skill** — a skill is to an agent what an SDK is to a developer; the canonical
source beats community reverse-engineering, and stating the delta scope in one
sentence ("covers only X-specific extensions; standard Y is assumed") keeps it
honest. And **place footgun warnings inside the workflow step where they fire**
(the validate step lists the likely validation errors), not in a separate
gotchas appendix the agent may never reach.

Package the capability in three loading tiers: metadata (always in context, ~100
words) → body (loaded on trigger, <500 lines) → bundled resources (unlimited —
references read as needed, and *scripts execute without ever entering context*).
That last tier is the underused move: deterministic capability shipped as code is
context-free, so the division of labor is **prose for judgment, references for
rare depth, scripts for anything deterministic** — the skill file is a thin
interface over real software (brain/01, with tokens as interface cost).

Artifacts now have **two readers** — humans and models — with opposite needs
(hierarchy and highlighting vs one flat, delimited, indexed stream). Design
outputs for both: render the machine view beside the human view from the same
pass (rendergit's Human/LLM toggle is the reference). Every export, report,
and dashboard has this dual-reader question; most answer only half.

When the curated knowledge itself exceeds any context budget (hundreds of styles,
rules, API entries), retrieval becomes the deterministic part: ship the corpus as
**structured, schema-validated data plus a boring local search tool** (BM25/regex,
zero dependencies — portability beats recall for installed tooling), and make the
loaded tier a *priority-ordered triage index* over it; the agent pulls 3 ranked
rows per query, never the corpus (ui-ux-pro-max). Validate the data, not just the
format — where data is the product, it gets schemas, lint, and tests.

Corollary for anything that routes on the environment (stack, framework, platform):
**detect from artifacts, ask when unknown, never default silently** — a hardcoded
default misroutes every downstream recommendation without ever erroring.

The *generated* sibling of the curated corpus is the project map derived from
source (graphify): extract **deterministically wherever a parser exists**
(tree-sitter ASTs are free, local, reproducible — spend LLM only on genuine
semantics), and label every derived fact by **provenance** — extracted (explicit
in source) / inferred (deduced) / ambiguous (route to a human). Derived knowledge
that can't say which of those it is will eventually be trusted wrongly.

When benchmarking an agent system, the fair-comparison standard (graphify's):
competitors run inside *your* harness under identical model/budget/grader, a
blind second judge with agreement stats published (kappa), cost as a first-class
axis beside accuracy, and losses reported as plainly as wins.

## Interfaces leak harder with LLM consumers

Hyrum's Law (brain/05) applies with more force, not less: an agent will treat any
observable text as the contract. The documented failure: a skill description that
*summarized its workflow* caused agents to execute the summary and skip the full
process. Rules that follow:
- Triggers/descriptions state **when to invoke**, never what the process is.
  The description is a *routing surface*: put all when-to-use information there —
  deliberately generous with trigger phrases, since under-triggering is the
  observed failure mode (Anthropic's own guidance) — and zero workflow summary.
  The highest-value trigger for a vendor skill is the *failure of the platform's
  native tool* ("use when web_fetch fails" — Scrapling): the fallback slot is
  where the agent is actively looking for an alternative.
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
- **Community catalogs need mechanized governance** (agency-agents). Format lint is
  not enough: the observed failure mode is the well-formed near-duplicate — a
  find-replace "re-skin" that merges cleanly and bloats the library. Defenses that
  work: a *semantic* originality gate (entity-neutralized shingle overlap against
  the whole corpus) with thresholds **calibrated against the existing corpus and
  documented in the tool**; and where one source of truth can't feed every consumer,
  duplicated facts guarded by a CI check that fails when any copy disagrees —
  drift that can't merge is drift that doesn't happen.

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
  The data-plane corollary (Understand-Anything): in multi-agent pipelines,
  **context carries coordination; disk carries data** — workers write large
  intermediates to files (cleaned up after assembly) rather than returning them
  into the orchestrator's window.

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

## Compose skills like modules

A skill library is a codebase; brain/01 applies directly (mattpocock/skills is the
proof). The working structure:
- **Primitives** — one well-designed process (an interrogation algorithm) reused by
  several entry points.
- **Vocabulary layers** — skills that define a shared language other skills "speak"
  (domain terms, design terms), each term with an explicit avoid-list of near-synonyms.
- **Compositions** — entry points that are one-line combinations of primitives and
  vocabularies. If a skill can't be expressed as a short composition, its primitives
  are missing.
- **Explicit invocation policy** — mark each skill user-invoked (a human-chosen entry
  point) or model-invoked (a helper the agent may pull in). This encodes the autonomy
  contract per skill instead of leaving triggering to chance.
- **Lifecycle buckets with membership invariants** — promoted / public-beta /
  deprecated, where "shipped set = promoted set" is an enforced rule. This prevents
  both catalog decay (ECC) and frozen catalogs (superpowers' closed policy).
  When guidance goes stale, **tombstone it** (JustHireMe): replace the body with
  an explicit "deprecated — do not let this constrain you; read the current
  code/docs instead." Stale guidance misleads with authority; deletion leaves
  dangling references; the self-disclaiming stub beats both.
- **Declarative context assembly** (gstack) — a skill's frontmatter can declare
  *queries* for the context it needs (globs over past artifacts, memory filters,
  sort/limit, rendered under a heading), assembled at invocation. Context
  construction as versioned, reviewable data beats imperative "first go read X"
  prose.
- **Model overlays** (gstack) — keep skill bodies model-neutral; put per-model
  quirk correction (verbosity, todo discipline) in separate overlay files with
  inheritance. Two concerns, two files; no forked skills.
- **Per-skill tool allowlists** — least privilege applied to skills: a plan
  review gets read/search tools, not edit. Scope what each skill *can* do, not
  just what it should.

## Shared language is context compression

DDD's ubiquitous language solves an agent problem: a project glossary (CONTEXT.md)
turns two sentences of circumlocution into one canonical term — paying off in fewer
thinking tokens, consistent naming, and cheaper navigation, session after session.
Discipline that keeps it working: the glossary stays *pure* (terms only, no
implementation details), conflicts with the glossary get challenged the moment they
appear, and ambiguities are flagged with their resolutions rather than papered over.

For eliciting the language and the design: **frontier interrogation** beats
one-question-at-a-time. Model the design as a tree of decisions; each round, ask the
whole frontier (every question whose prerequisites are settled), numbered, each with
a recommended answer. Split strictly: *facts* are the agent's job (dispatch lookups,
don't block unrelated questions on them); *decisions* are the human's. Terminate when
the frontier is empty — nothing left silently assumed.

For single-shot generation, the lightweight sibling is the **declared
interpretation** (taste-skill): state a one-line reading of the brief — audience,
register, direction — *before* acting, and ask at most one clarifying question,
only on genuine divergence. The user can redirect at the cost of one line;
grilling stays for work too big to hold in one shot.

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

## Autonomous experiment loops

The design for agent-driven hill climbing (karpathy/autoresearch is the
reference; studies/autoresearch.md):
- **Freeze the judge.** The evaluation code, metric, and dependencies live
  outside the agent's editable surface, by hard rule. Without this boundary any
  self-improving loop eventually optimizes the metric's implementation instead
  of the target — reward hacking excluded by construction, not by trust.
- **Normalize by budget, not configuration.** A fixed wall-clock/cost budget per
  experiment makes every attempt comparable regardless of what changed, prices
  the loop predictably, and supplies the kill criterion (over budget → discard).
- **Choose an invariant metric** — one that stays meaningful under every move
  the agent is allowed to make. And remember the frozen judge is still a chosen
  judge: Goodhart applies to what the scalar can't see.
- **Price complexity into the accept rule.** Keep-if-better loops accrete cruft
  monotonically unless the acceptance test charges for it: tiny win + hacky code
  → discard; equal result + simpler code → keep.
- **Git is the ledger; negatives are the record.** Branch per run, commit per
  attempt, advance on improvement, reset on regression — and log every attempt
  (kept, discarded, crashed, with descriptions), because the discards are the
  research record.
- **Bounded crash policy + boredom protocol.** Trivial failure → fix and rerun;
  broken idea → log and move on; a few failed fixes → give up. And specify what
  to do when out of ideas (re-read sources, combine near-misses, escalate
  radicalism) — autonomous loops fail on stopping and on idea exhaustion, so
  script both.
- **Two-level programming.** The human's surface is the org code — the loop
  instructions, roster, and accept rules — one level above the work. Iterating
  there is the actual meta-game.

## Calibrate autonomy by reversibility

There is also a *system-level* autonomy choice, prior to any single gate: who owns
the process. Mandatory auto-triggering methodologies (superpowers) buy uniform
discipline with rigidity; human-invoked composable toolkits (mattpocock/skills) buy
adaptability with reliance on user judgment. Pick per team: uniform discipline for
mixed-experience teams, composable control for experts — and either way, build the
library compositionally (above), which is superior at any point on that spectrum.

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
