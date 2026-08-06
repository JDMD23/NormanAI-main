# NormanAI — An Engineering Brain

This repository is a living knowledge base of elite software design and architecture,
built to be used *with* Claude. It has three jobs:

1. **Hold the brain.** `brain/` contains distilled, opinionated engineering judgment —
   the principles, tradeoffs, and decision frameworks of a world-class engineer.
   It is not a textbook summary; it is the compressed "why" behind good systems.

2. **Learn from great code.** When pointed at an interesting repository, Claude studies
   it using the workflow in `studies/` and feeds durable lessons back into `brain/`.
   The brain compounds over time.

3. **Review and optimize real projects.** When pointed at one of your repositories,
   Claude runs the audit framework in `reviews/` — producing a prioritized, pragmatic
   assessment grounded in the brain, not generic best-practice noise.

## How to use it

- **"Study this repo: `<url>`"** → Claude clones it, analyzes it against
  `studies/_template.md`, writes a study, and updates the brain with anything new.
- **"Review my repo: `<url>`"** → Claude runs the framework in `reviews/_template.md`
  and delivers a ranked set of recommendations with effort/impact estimates.
- **"What does the brain say about X?"** → Claude answers from `brain/`, citing the
  relevant doc, and flags anywhere the brain is thin so it can be improved.

## Layout

```
brain/       The knowledge base (numbered, read in order for a full picture)
studies/     Analyses of external repos worth learning from
reviews/     Audits of your own repos and workflows
CLAUDE.md    Operating instructions for Claude sessions in this repo
```

## Ground rules for the brain

- **Judgment over rules.** Every principle carries its limits and its failure modes.
  A principle stated without the conditions under which it's wrong is dogma.
- **Compression over coverage.** Short and dense beats long and complete.
- **Evidence over authority.** Lessons get added because a real codebase demonstrated
  them, not because a famous book said them. Studies are the evidence trail.
