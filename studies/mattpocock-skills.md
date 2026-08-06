# Study: mattpocock/skills

- **Repo:** https://github.com/mattpocock/skills
- **Studied:** 2026-08-06 at commit `8b36d4f`
- **What it is:** Matt Pocock's personal agent-skills toolkit: ~35 skills totaling
  just 2,377 lines, organized in lifecycle buckets, shipped as a Claude Code plugin.
  Explicitly anti-framework: "small, easy to adapt, composable" vs. systems that
  "own the process and take away your control."
- **Why it was worth studying:** Fourth point on the spectrum — the *practitioner's
  composable toolkit* — and the strongest example yet of classical software design
  (Ousterhout, Evans, Feathers, Hunt/Thomas) applied *to* agent tooling, not just
  through it.

## Architecture at a glance

```
skills/
  engineering/ productivity/   # promoted: shipped in the plugin, documented
  in-progress/                 # public beta — feedback wanted, not shipped
  misc/  deprecated/           # retained but not promoted
CONTEXT.md                     # the repo's own glossary (dogfooded domain-modeling)
.agents/adr/                   # ADRs governing the repo itself
CLAUDE.md (= AGENTS.md symlink)# invariants, written as agent instructions
docs/                          # human-facing page per promoted skill
```

Structurally this is a **module system for skills**: primitives (`grilling`),
vocabulary layers other skills "speak" (`domain-modeling`, `codebase-design`),
compositions (`grill-with-docs` is six lines: "Run a /grilling session, using the
/domain-modeling skill"), and a router (`ask-matt`) mapping flows across them.

## What this codebase does exceptionally well

1. **Skills are deep modules that compose.** One interrogation primitive serves
   multiple entry points; shared-vocabulary skills sit underneath process skills;
   entry-point skills are one-line compositions. Average skill ~70 lines. This is
   brain/01 (deep modules, information hiding) applied to prompt engineering — and
   `codebase-design/SKILL.md` *is* the Ousterhout/Feathers vocabulary, packaged as a
   ubiquitous language ("use these terms exactly; consistent language is the whole
   point"), with each term carrying an explicit *avoid-list* of near-synonyms.

2. **The frontier interrogation algorithm** (`grilling`) is the best requirements-
   elicitation design I've seen for agents. Model the design as a **tree of
   decisions**; each round, ask the entire **frontier** — every question whose
   prerequisites are settled — numbered, each with a recommended answer; settled
   answers push the frontier outward. Two brilliant refinements: **facts vs
   decisions** ("finding facts is your job, never the user's" — dispatch subagents,
   don't block the rest of the frontier on them; decisions always go to the human)
   and a real termination condition (empty frontier = "nothing left silently
   assumed"). Compare superpowers' "ask questions one at a time": the frontier
   batches what's askable now without ever asking a question that depends on an
   unanswered one.

3. **Ubiquitous language as context compression.** The insight that DDD's shared
   language solves an *agent* problem: "There's a problem with the materialization
   cascade" replaces two sentences of circumlocution, session after session. Payoffs
   claimed: consistent naming, cheaper navigation, fewer thinking tokens. The
   discipline is real: `CONTEXT.md` is a glossary and *nothing else* ("totally
   devoid of implementation details"), terms conflicting with the glossary get
   challenged immediately, ambiguities get a "Flagged ambiguities" section with
   resolutions — and the repo dogfoods all of it on itself.

4. **ADR discipline at reference quality.** The gate is three conditions, all
   required: **hard to reverse** ∧ **surprising without context** ∧ **result of a
   real trade-off** — if any is missing, skip the ADR. And ADR-0002 (why a Claude
   plugin but not a Codex one) is a model of the genre: the forcing constraint
   (Codex manifests take one path string; symlinks are dropped by its install cache
   — *tested*, with the failure mode named), rejected alternatives with reasons,
   the invariants the decision creates, and dated verification updates against live
   systems.

5. **Lifecycle buckets with hard invariants.** Promoted skills *must* appear in
   README + plugin.json; non-promoted *must not*; `in-progress/` is deliberately
   public beta; `deprecated/` is retained, not deleted. The plugin ships exactly
   the promoted set. Curation (the superpowers lesson) plus a visible pipeline for
   growth (which superpowers' closed policy lacks) — catalog decay (ECC's failure)
   structurally prevented.

6. **Explicit invocation policy per skill.** Frontmatter separates user-invoked
   (`disable-model-invocation: true` — entry points the human chooses) from
   model-invoked (vocabulary and sub-processes the agent pulls in). Nobody else
   studied makes this distinction explicit; it's the control-philosophy made
   mechanical: the human triggers processes, the agent composes helpers.

7. **Context management as a first-class planning constraint.** The router names
   the "smart zone" (~150k tokens where reasoning stays sharp), mandates one
   unbroken window from grilling through ticket-splitting, then a fresh window per
   ticket ("the last one's context is disposable"), and gives a five-option
   decision guide for phase boundaries (continue / clear / handoff / subagent /
   compact) with a stated default. Wayfinder's framing for foggy efforts —
   "decisions, not deliverables" — turns a map of open questions into tracked,
   dependency-ordered decision tickets.

## Questionable calls and tradeoffs

- **No behavioral testing.** By the brain/09 hierarchy this is tier-3 prose:
  no evals, no baselines. Mitigated differently than superpowers: one expert
  author dogfooding daily plus a large audience as an informal feedback loop.
  That scales taste, not verification — forks inherit claims, not evidence.
- **Invariants enforced by agent instructions, not CI.** The CLAUDE.md invariants
  (promoted ⇔ README ⇔ plugin.json; router must not lie; docs re-sync triggers)
  rely on the *agent* reading and obeying them during maintenance sessions — a
  novel middle tier between prose and CI, but per their own philosophy these are
  mechanically checkable and would be cheap to script. (`claude plugin validate`
  covers only the manifest.)
- **Single-author voice as architecture.** `ask-matt`, "Matt's" flows — coherence
  comes from one person's taste (the source of its quality), which makes the repo
  hard to generalize to team authorship. Contrast ECC's many-voices sprawl: this is
  the opposite failure mode avoided, but the succession problem is real.
- Newsletter/marketing hooks in README — light, and honestly labeled.

## Where this sits on the spectrum

karpathy-skills (patch) → **mattpocock/skills (composable toolkit)** → superpowers
(methodology) → ECC (platform). Pocock vs superpowers is the interesting axis: not
size but **who owns the process**. Superpowers auto-triggers and mandates; Pocock
makes every entry point human-invoked and every skill forkable. Superpowers buys
reliability with rigidity; Pocock buys adaptability with reliance on user judgment.
For expert users, Pocock's bet looks right; for teams wanting uniform discipline,
superpowers'. The composability layer, though, is simply better engineering —
primitives + vocabularies + compositions beat monolithic skills at any point on
the control spectrum.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Build skill libraries as module systems: primitives, shared vocabulary layers, one-line compositions | grilling / domain-modeling / grill-with-docs | Any prompt/skill library; brain/01 depth applies verbatim |
| Elicit requirements by frontier: batch all currently-askable questions with recommended answers; agent fetches facts, human makes decisions; stop at empty frontier | grilling SKILL.md | Design conversations, spec reviews, any agent-led interview |
| Maintain a project glossary (CONTEXT.md): pure glossary, avoid-lists, challenge conflicts, flag ambiguities — shared language is context compression | CONTEXT.md + domain-modeling | Every repo an agent works in long-term; cheap to start, compounds |
| Gate ADRs on hard-to-reverse ∧ surprising ∧ real-tradeoff | domain-modeling | Sharper than "document non-obvious decisions" (brain/07) |
| Separate user-invoked entry points from model-invoked helpers explicitly | invocation frontmatter + policy file | Any skill system; encodes the autonomy contract per skill |
| Give catalogs a lifecycle: promoted/beta/deprecated buckets with membership invariants | bucket structure + CLAUDE.md rules | Prevents both catalog decay (ECC) and frozen catalogs (superpowers) |
| Name the context budget and plan phases around it; fresh window per self-contained ticket | smart zone, context hygiene rules | Long agent sessions; pairs with brain/09 ledger pattern |

## Brain updates made

- `brain/09-agentic-engineering.md`: added **"Compose skills like modules"** (primitives,
  vocabulary layers, compositions, invocation policy, lifecycle buckets) and
  **"Shared language is context compression"** (glossary discipline, frontier
  interrogation with the facts/decisions split); noted the control-spectrum framing
  under autonomy calibration.
- `brain/07-decision-frameworks.md`: tightened the ADR trigger to the three-condition
  gate (hard to reverse ∧ surprising without context ∧ real trade-off).
