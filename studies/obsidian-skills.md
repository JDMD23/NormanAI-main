# Study: obsidian-skills

- **Repo:** https://github.com/kepano/obsidian-skills
- **Studied:** 2026-08-06 at commit `a1dc48e`
- **What it is:** Five skills from Obsidian's CEO (Steph Ango / kepano) teaching
  agents Obsidian's file formats: Obsidian Flavored Markdown, Bases (`.base`),
  JSON Canvas (`.canvas`), the Obsidian CLI, and defuddle (clean web-page
  extraction). 14 files, ~1,800 lines total, Agent Skills spec-compliant, MIT.
- **Why it was worth studying:** The thirteenth study introduces the cleanest
  new genre yet — the **vendor format skill** — and executes the brain's
  skill-authoring principles with textbook discipline, from the format owner
  itself.

## Architecture at a glance

```
skills/obsidian-markdown/   SKILL.md (196 ln) + references/ (callouts, embeds, properties)
skills/obsidian-bases/      SKILL.md (499 ln) + references/FUNCTIONS_REFERENCE.md
skills/json-canvas/         SKILL.md (244 ln) + references/EXAMPLES.md
skills/obsidian-cli/        SKILL.md (106 ln)
skills/defuddle/            SKILL.md (41 ln)
```

## The headline: a skill is to an agent what an SDK is to a developer

The pattern this repo establishes: the **format owner ships the skill**. Obsidian
defines these file formats; kepano publishing the skills means every agent that
installs them produces valid Obsidian files, learned from the canonical source —
exactly the role SDKs and official client libraries play for human developers.
The strategic logic runs both ways: users get correctness, the vendor gets an
ecosystem where agents are first-class producers of its formats. Every product
with a file format, DSL, or API surface should be doing this, and almost none
are. (The claude-api skill in anthropics/skills is the same move for an API;
this is the purest format example.)

## What it does exceptionally well

1. **Knowledge-delta scoping, stated explicitly.** "This skill covers only
   Obsidian-specific extensions — standard Markdown (headings, bold, lists...)
   is assumed knowledge." The anthropic-skills delta principle (brain/09),
   written in the wild as a scoping sentence. No tokens teaching CommonMark.

2. **Textbook progressive disclosure.** Core syntax and workflow in SKILL.md;
   exhaustive enumerations (all callout types, all embed forms, all Bases
   functions, canvas examples) pushed to `references/` with clear pointers.
   The sizes are right: a 41-line skill where 41 lines suffice, references only
   where an enumeration earns one.

3. **Workflows end in verification, with failure modes pre-listed.** Both major
   skills close their workflow with "verify it renders in Obsidian," and Bases
   goes further: the validate step enumerates the *likely* errors at exactly
   that point — "unquoted strings containing special YAML characters, mismatched
   quotes in formulas, referencing `formula.X` without defining `X`." Footgun
   placement inside the workflow step where the gun goes off.

4. **Format knowledge agents genuinely lack.** Wikilink heading/block syntax,
   block-ID placement rules for lists vs paragraphs, `.base` filter recursion
   ("exactly ONE key: and, or, not"), YAML quoting rules — precisely the
   Obsidian-specific delta between model knowledge and reality.

5. **Standards citizenship.** Follows the Agent Skills spec, documents install
   for Claude Code/Codex/OpenCode including the OpenCode directory-structure
   gotcha, takes community PRs (HEAD is a merged external contribution).

## Questionable calls and tradeoffs

- **No validation harness.** The examples are presumably hand-verified against
  Obsidian; nothing in-repo lints the YAML samples or round-trips the canvas
  JSON against the spec. For format documentation, executable example checking
  would be cheap and high-value (the langchain-tests instinct, miniaturized).
- **No evals** — the ecosystem-wide gap, though at 1,800 lines of pure format
  reference the risk profile is lower than for behavioral skills.
- **defuddle depends on the author's own tool** — reasonable (it's good and
  token-motivated: "removing clutter to save tokens"), but it's the one skill
  that's a product plug rather than a format spec.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Format/API owners should ship official skills — a skill is to an agent what an SDK is to a developer | the whole repo | Any product with a format, DSL, or API; canonical source beats community reverse-engineering |
| State the knowledge-delta scope in one sentence ("covers only X-specific extensions; Y is assumed") | obsidian-markdown intro | Every reference skill; saves tokens and sharpens focus |
| Put footgun warnings inside the workflow step where they fire, not in a separate gotchas section | Bases validate step | Workflow-shaped skills |
| References earn their existence via enumerations; workflows and core syntax stay in the body | skill/references split | The progressive-disclosure boundary decision |

## Brain updates made

- `brain/09-agentic-engineering.md`: one addition to the knowledge-delta
  section — the vendor-skill pattern (format/API owners ship the skill; SDK
  analogy) and footguns placed inside the workflow step where they fire.
