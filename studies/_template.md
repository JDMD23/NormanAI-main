# Study: <repo name>

- **Repo:** <url>
- **Studied:** <date> at commit <sha>
- **What it is:** one sentence.
- **Why it was worth studying:** what the user or I hoped to learn.

## Architecture at a glance

How the system is actually shaped: major modules, dependency direction, where state
lives, how data flows for the primary use case. A short diagram or tree if it helps.
(Analyze top-down: README → entry points → module boundaries → only then individual
files. Never start by reading files alphabetically.)

## What this codebase does exceptionally well

3–7 concrete observations, each anchored to real code (file/dir references). These are
candidates for the brain. "Clean code" is not an observation; "the entire effect
system is behind one 4-function interface in `io/`, letting the core stay pure" is.

## Questionable calls and tradeoffs

Where the design is surprising, costly, or context-dependent — and *why they likely
did it anyway*. Great repos make deliberate tradeoffs; understanding the reasoning
is worth more than the pattern itself.

## Transferable lessons

Each lesson stated generally enough to apply elsewhere, specific enough to act on:

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|

## Brain updates made

- `brain/XX-*.md`: <what was added/changed, or "none — confirmed existing content">
  (A study that changes nothing in the brain is fine; say so explicitly.)
