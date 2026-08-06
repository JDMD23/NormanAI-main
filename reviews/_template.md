# Review: <repo name> — <YYYY-MM>

- **Repo:** <url> at commit <sha>
- **Stated goal:** what the user wants (optimize workflows, assess architecture,
  prep for scale, etc.). The review is judged against *this*, not abstract purity.
- **Context gathered:** team size, stage, stakes, deploy frequency — because the
  right answer depends on these (see brain/00 "scope honesty").

## Verdict (read this first)

Three to five sentences: overall health, the one or two things that matter most,
and what I'd do in the next two weeks. No hedging, no filler.

## How I assessed it

Order of examination (mirrors diagnostic priority):
1. **Feedback loops** — clone-to-running time, test suite speed/reliability, CI
   duration, deploy process. (brain/00, /06)
2. **Architecture & boundaries** — dependency direction, where state lives, module
   cohesion, data model. (brain/02, /04)
3. **Antipattern sweep** — the catalog in brain/08, checked explicitly.
4. **Code quality sampling** — the most-changed files (`git log` frequency), the
   largest files, and the money path, read closely. Not a full read.
5. **Operations** — config/secrets, observability, backup/restore reality. (brain/06)

## Findings

Ranked by impact. Every finding has all four fields — a finding without a concrete
next step is deleted before delivery.

### F1. <title>
- **Severity:** critical / high / medium / low
- **Evidence:** specific files, measurements, or history (not vibes)
- **Why it matters here:** tied to the user's stated goal
- **Recommendation:** the specific change, effort estimate (hours/days/weeks),
  and what to do *first* if it's big

## What's already good

Genuine strengths, specifically. This calibrates trust in the criticism and tells
the user what *not* to churn.

## Suggested sequence

A short ordered plan (1–2 weeks granularity): quick wins first, then the
highest-interest debt. Explicitly list what I'd *not* bother fixing and why.
