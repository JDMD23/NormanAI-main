# Study: orca

- **Repo:** https://github.com/DimiMikadze/orca
- **Studied:** 2026-08-06 at commit `36d9eda`
- **What it is:** An AI agent for deep LinkedIn profile analysis. You define the
  insights you want (pain points, expertise, communication style…); it collects
  baseline data, then reasons over it and *autonomously calls scraping tools*
  when an insight needs more evidence. Core logic is a standalone ~780-line
  library (`orca-ai/`); a Next.js app is the demo. LangChain, MIT.
- **Why it was worth studying:** A distinct genre — the **bounded autonomous
  investigation agent** — done with real discipline, and the source of one crisp
  pattern the brain hadn't captured: the fixed-baseline + budgeted-drill-down
  split, with cost as a designed-in constraint.

## Architecture at a glance

```
orchestrator.ts   analyzeProfile(): baseline collection → analysis agent → stats
services/         collect-linkedin-data (deterministic, no LLM, ~11 credits) +
                  per-endpoint scrapers (comments, reactions, activity)
analysis-agent.ts LangChain agent: gets baseline as context, 3 scraping tools,
                  bounded tool-call budget, structured (zod) insight output
config.ts         insight preset packs (general/sales/recruiting/investing),
                  model, budgets, page defaults
utils/            credit tracker, data formatter
```

## The headline: fixed baseline + bounded autonomous drill-down

The orchestration split is the transferable idea, and it's the mature answer to
"how much autonomy does an analysis agent get":

1. **Deterministic baseline collection first** — profile, posts, comments,
   reactions, top-post engagement — *no LLM involved*, a known ~11-credit cost.
   The cheap, predictable, reproducible pass runs unconditionally.
2. **The agent reasons over that baseline** and only *then* reaches for tools —
   "Only use them if you need specific data to answer an insight and that data is
   not in the context. **Do not fetch data out of curiosity.** Max N tool calls."
3. **Every drill-down is budgeted and priced.** `DEFAULT_MAX_TOOL_CALLS = 3`;
   each tool's description states its cost ("1 credit per page"); `maxToolCalls:
   0` degrades cleanly to pure analysis-over-context.

This is the graphify/deterministic-first economics (studies/graphify.md) and
autoresearch's frozen-budget discipline (studies/autoresearch.md) fused into an
agentic loop: do the cheap deterministic work eagerly and completely, gate the
expensive autonomous work behind an explicit budget and a stated no-speculation
rule. The general principle, now in the brain: **an investigation agent should
run a fixed cheap baseline unconditionally and treat further tool use as a
budgeted, justified exception — not the default mode.**

## What else it does well

1. **Cost is a first-class design citizen, end to end.** Tool descriptions carry
   per-call credit costs *so the model can weigh them*; a `trackCredits` util
   reads RapidAPI's `x-ratelimit-credits-remaining` headers after every fetch;
   stats surface `toolCallCount`. The agent is given the price list and told not
   to overspend — cost-awareness pushed into the reasoning surface, not bolted on
   as an afterthought. (Most agent apps discover their bill in the dashboard;
   this one budgets in the prompt.)

2. **Grounding enforced structurally.** System prompt: "Never speculate, every
   claim must be grounded in specific evidence." Output rules mandate `[post](url)`
   citations with "the exact URL from the data. Never fabricate URLs." Zod output
   schema forces one entry per insight category. This is provenance
   (graphify's extracted/inferred) and anti-hallucination discipline enforced by
   *format contract*, not hope — the closest an LLM-reasoning agent gets to the
   epistemic-honesty bar the deterministic tools set.

3. **A read-through cache that makes the budget honest.** Baseline-collected
   top-post comments/reactions are pre-loaded into a cache keyed by post URN; if
   the agent "drills into" a post already collected, it's a cache hit that
   *doesn't consume the tool budget* and logs as such. The agent can't
   accidentally re-buy data it already has — the budget only spends on genuinely
   new fetches (brain/04 derived-data + brain/09 index-before-fetch).

4. **Library-first, demo-second.** "The core logic lives in `orca-ai/` as a
   standalone library… plug it into any Node.js project." The valuable part is
   framework-independent and separately consumable; the Next.js app is a thin
   harness over it (brain/02 dependency direction — the domain core doesn't
   import the web framework).

5. **Insight definitions as configuration, not code.** Insights are data
   (`{name, description}` packs for sales/recruiting/investing), user-overridable
   — the agent is a *reusable reasoning engine* parameterized by what to look
   for, not a hardcoded analyzer (brain/05 general-purpose interface, right-sized).

## Questionable calls and tradeoffs

- **Same LinkedIn ToS ceiling**, at one further remove: orca scrapes via a
  third-party RapidAPI provider ("Fresh LinkedIn Profile Data") rather than
  directly, outsourcing the collection (and its ToS exposure) to a vendor. That
  cleans up orca's own code and legal surface but doesn't change the underlying
  legitimacy question (studies/ats-scrapers.md); it relocates it.
- **The output is profiling of individuals.** Sales/recruiting/investing use
  cases mean inferring a named person's "values," "pain points," and "how their
  interests change" from their activity. The grounding rules are a genuine
  mitigation (claims must cite evidence), but the deliverable is still an
  automated dossier on a real person — a use the brain flags for the caution it
  warrants, independent of code quality.
- **Single-shot agent, no verification pass.** Insights are produced once; there
  is no adversarial check that citations actually support claims (the
  reviewer-mechanization pattern from studies/understand-anything.md would fit —
  a pass validating that each `[post](url)` exists in the data and supports its
  sentence).
- **~780 lines is small and clean now** — the risk is the analysis-agent file
  accreting tools; the current 3-tool surface is well within coherent range.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Investigation agents: run a fixed cheap deterministic baseline unconditionally; gate further tool use behind an explicit budget + a no-speculation rule ("don't fetch out of curiosity") | orchestrator + agent prompt | Research/analysis agents; the baseline must cover the common case |
| Put the price list in the tool descriptions so the model weighs cost while reasoning; track spend from provider headers | credit costs in tool descs + trackCredits | Any metered-tool agent |
| Enforce grounding by format contract: mandatory evidence citations with real URLs, schema-forced structure | system prompt + zod schema | LLM analysis over data; reduces (not eliminates) fabrication |
| Pre-load already-collected data into a cache the tools read through, so the budget only spends on new fetches | URN-keyed comment/reaction cache | Agentic loops with a fetch budget |
| Ship the reasoning engine as a framework-independent library; the app is a harness | orca-ai/ vs app/ | Any agent worth reusing beyond its demo |

## Brain updates made

- `brain/09-agentic-engineering.md`: added the **bounded-investigation pattern**
  — deterministic baseline eager + completely, autonomous tool use as a budgeted
  justified exception with the price list in the tool descriptions and grounding
  enforced by output contract.
