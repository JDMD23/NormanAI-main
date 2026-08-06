# Study: anthropics/skills

- **Repo:** https://github.com/anthropics/skills
- **Studied:** 2026-08-06 at commit `b29e7cf`
- **What it is:** Anthropic's official skills repo: 17 skills (creative, technical,
  enterprise), the production document skills (docx/pdf/pptx/xlsx — source-available,
  182 files of real software), the official `skill-creator` meta-skill, a 6-line
  template, and a pointer to the Agent Skills spec (now externalized to
  agentskills.io).
- **Why it was worth studying:** The canonical source, after five community
  interpretations. Two questions: what does the org that invented the format think
  a skill *is*, and what does a skill powering a production feature look like?

## Architecture at a glance

```
skills/<name>/SKILL.md      # interface: frontmatter (trigger) + instructions
skills/<name>/scripts/      # implementation: real software, runs without loading
skills/docx|pdf|pptx|xlsx/  # production document skills: Python packages, XSD
                            #   schema validation, LibreOffice automation
skills/skill-creator/       # official meta-skill, with eval tooling in-skill
template/SKILL.md           # the whole required shape, in 6 lines
```

## The two big findings

### 1. Skills are knowledge *deltas*, not tutorials

The docx skill states the principle in one line: **"The model knows the API; these
are the footguns."** The skill spends zero words teaching docx-js — it documents
only where reality diverges from what the model already believes: `ShadingType.SOLID`
renders black (use `CLEAR`); `WidthType.PERCENTAGE` breaks in Google Docs; TOCs
silently omit custom heading styles unless `outlineLevel` is set; Word fragments
visible phrases across `<w:r>` runs so grep can't find them (hence `merge_runs.py`).
Every entry is empirical — an observed failure, compressed to a rule.

This is the sharpest answer yet to "what should agent-facing docs contain": not
what the model knows (wasted tokens), not generic best practice (noise), but the
**delta between model belief and ground truth**, harvested from real failures. It
generalizes superpowers' rationalization tables (behavioral deltas) to technical
knowledge (API-reality deltas).

### 2. Progressive disclosure is the context economics of capability

The official three-tier loading model, from skill-creator:
1. **Metadata** (name + description) — always in context, ~100 words
2. **SKILL.md body** — loaded on trigger, <500 lines ideal
3. **Bundled resources** — unlimited; references loaded as needed, and **scripts
   execute without ever entering context**

Tier 3 is the move the community repos underuse: the docx skill wields a 182-file
software package — schema validation, tracked-changes acceptance, headless
rendering — at *zero* context cost, because capability lives in executable code
rather than prose. The design rule that falls out: **prose for judgment, references
for rare depth, scripts for anything deterministic** — and the skill file is the
thin interface over all three (brain/01's deep module, again, with token budget as
the interface cost).

## What else this repo does exceptionally well

1. **The official meta-process is eval-driven.** skill-creator's loop: draft →
   test prompts → run in background → qualitative *and* quantitative evaluation
   (eval viewer, benchmarks with variance analysis) → rewrite → expand the test
   set. Plus a dedicated description-optimizer for triggering accuracy. Notably,
   this *agrees* with superpowers' TDD-for-skills discipline — the two differ in
   register (flexible guidance vs Iron Laws), not in method. The eval loop is the
   consensus of every serious skill author studied.

2. **Verification is built into the workflow, not appended.** The docx skill's
   creation path ends: render to PDF, rasterize to images, *look at them*. Same
   evidence-before-claims gate as superpowers/ECC, applied to visual output.

3. **Trigger descriptions engineered against the observed failure mode.** Claude
   currently *under*-triggers skills, so official guidance says make descriptions
   deliberately "pushy," enumerate trigger phrases, and put **all** when-to-use
   information in the description (never the body). This composes cleanly with
   superpowers' description-leak rule: triggering info belongs in the description;
   *workflow* summaries never do. Two rules, one boundary: the description is a
   routing surface, not a summary surface.

4. **Small, honest touches of production quality.** Stripping symlink entries from
   untrusted `.docx` archives before unzipping (documents as attack surface);
   documenting their own tools' failure modes ("`accept_changes.py` joins
   paragraphs correctly, *except* when followed by an empty spacer — pandoc never
   joins them"); audience-calibrated communication guidance in skill-creator
   (plumbers-to-grandparents are opening terminals now — gate jargon on evidence
   the user knows it).

5. **A template that practices minimalism.** The entire required shape is six
   lines. The spec was moved out to a neutral home (agentskills.io) as it became
   a multi-vendor standard — the ecosystem play done cleanly.

## Questionable calls and tradeoffs

- **No evals in the repo itself.** skill-creator preaches and tools the eval loop,
  but the shipped skills carry no test suites or eval results — "demonstration and
  educational purposes" per the disclaimer. The production document skills clearly
  have internal validation (their scripts *are* validators), but the public repo
  doesn't model the discipline it recommends. Superpowers' external evals repo
  remains the only public example.
- **Mixed licensing in one tree** (Apache 2.0 examples beside proprietary
  source-available document skills) — pragmatic transparency, slightly awkward
  reuse story; THIRD_PARTY_NOTICES and per-skill license fields handle it honestly.
- **The 546-line claude-api skill** pushes the "<500 lines ideal" guidance it
  ships next to — minor, but the tension between its own rules and artifacts is
  visible in places.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Write agent docs as knowledge deltas: only where reality diverges from model belief, each entry harvested from an observed failure | docx footgun list | All agent-facing docs; requires actually collecting the failures |
| Three-tier progressive disclosure; scripts execute without loading — deterministic capability is context-free | skill-creator loading model; 182-file docx package | Any skill/tool packaging; the ratio of prose to script is a design choice |
| The description is a routing surface: all trigger info there, pushy against under-triggering, zero workflow summary | skill-creator guidance + superpowers' rule | Skill/tool/command descriptions everywhere |
| End creation workflows with sensory verification (render and look), not just exit codes | docx verify loop | Anything producing visual/formatted output |
| Treat inbound documents as attack surface (strip symlinks before unzip) | docx editing workflow | Any pipeline unpacking user-supplied archives |
| Document your own tools' failure modes beside the tools | accept_changes.py caveats | All internal tooling; the alternative is users rediscovering the bug |

## Brain updates made

- `brain/09-agentic-engineering.md`: added **"Skills are knowledge deltas, packaged
  with progressive disclosure"** — the delta principle, the three-tier loading
  economics, prose/references/scripts division of labor; extended the interface
  section with the description-as-routing-surface synthesis (pushy triggers +
  no workflow summaries).
