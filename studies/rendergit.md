# Study: rendergit

- **Repo:** https://github.com/karpathy/rendergit
- **Studied:** 2026-08-06 at commit `14d7a58` ("tweak readme one more time. ok
  i'm going to go do something useful now")
- **What it is:** Four files. A 520-line single-file Python utility that flattens
  any GitHub repo into one static HTML page with two toggleable views — a Human
  view (syntax highlighting, sidebar, Ctrl+F everything) and an LLM view (the
  whole codebase as CXML, ready to paste into a model). Two dependencies.
  0BSD license.
- **Why it was worth studying:** The twentieth study is the collection's
  opposite pole — the *disposable utility done honestly* — and it carries one
  genuinely important design principle plus the best example of weight-class
  matching in the whole set.

## Architecture at a glance

There barely is one, which is the point: ~20 small flat functions
(clone → collect → decide per file → highlight/render → build HTML → open
browser), two frozen dataclasses (`RenderDecision`, `FileInfo`), binary/size
filtering heuristics, a `tree` command with a pure-Python fallback, Pygments +
Markdown as the only dependencies, installable as a `uv tool` with a console
script. Everything the job needs, nothing it doesn't.

## The two lessons

### 1. Every artifact now has two readers

The view toggle — 👤 Human / 🤖 LLM — is the clearest expression anywhere of a
quiet 2026 truth: code, docs, reports, and tool outputs are now consumed by
*two* audiences with opposite needs. Humans want hierarchy, highlighting,
navigation; models want one flat, delimited, indexed stream (CXML:
`<document index="N"><source>path</source><document_content>…`). rendergit
doesn't pick — it renders both from one pass. The generalization, now in the
brain: when building any artifact or tool output, ask what the *machine
rendering* looks like, and consider shipping it beside the human one. (Every
"export" feature, report generator, and dashboard has this dual-reader
question; most answer only half.)

### 2. Weight-class matching: governance proportional to intent

Every meta-signal of this repo is tuned to what it actually is:
- README: "I vibe coded this utility… I keep using it very often so I figured
  I'd just share it. **I don't super intend to maintain or support it though.**"
- License: 0BSD, chosen in a commit that says "apache 2.0 is way too heavy for
  this" — the license itself right-sized.
- No CONTRIBUTING, no CoC, no roadmap, no badge wall, no sponsor tiers.

Declared non-maintenance is a *service*: users can calibrate reliance, forks
are implicitly invited, and nobody is misled by ceremony into expecting
support. Contrast the studied repos that dress weekend-utility cores in
enterprise governance (dual licenses, CLAs, 30 translated READMEs) — the
mismatch taxes every reader. Brain/00's scope honesty extends to the *repo's
paperwork*: license, governance, and support posture should match the
artifact's true weight class, and stating that posture out loud beats implying
one you won't honor.

## Small craft notes

- **Publishing the personal tool as-is** beats both hoarding it and
  over-productizing it — the third option most people miss.
- **Graceful fallback** (`tree` binary → Python reimplementation) and honest
  per-file failure handling ("Failed to read: …" inline in the output rather
  than a crashed run).
- **The distribution is right**: `uv tool install git+…` — no PyPI release
  obligations for a tool with no maintenance promise, yet still one-command
  installable.
- No tests — and at this weight class that's *correct*; a test suite here
  would be ceremony (the brain's karpathy-skills study made the same
  write-cost/carry-cost point from the other direction).

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Design outputs for both readers: human rendering and machine rendering from one pass | Human/LLM view toggle | Reports, exports, docs tooling, dashboards |
| Match license, governance, and support posture to the artifact's weight class — and declare the posture | 0BSD + "don't intend to maintain" | Every repo; the inverse failure (ceremony on a toy) taxes readers |
| Ship the personal tool honestly rather than productizing or hoarding it | the whole repo | Utilities you already use weekly |
| A flat list of small functions is the right architecture below ~1k lines | rendergit.py | Single-purpose tools; structure is cost |

## Brain updates made

- `brain/09-agentic-engineering.md`: added the dual-reader principle (ship the
  machine rendering beside the human one) to the knowledge-packaging section.
- `brain/00-philosophy.md`: one sentence extending scope honesty to repo
  paperwork — governance, license, and declared support posture match the
  artifact's weight class.
