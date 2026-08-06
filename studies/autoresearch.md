# Study: autoresearch

- **Repo:** https://github.com/karpathy/autoresearch
- **Studied:** 2026-08-06 at commit `228791f`
- **What it is:** Karpathy's overnight-research harness: an agent autonomously
  edits a single-file GPT training script (simplified from nanochat), trains for
  a fixed 5-minute wall-clock budget, keeps or reverts by one metric (val_bpb),
  and loops — ~100 experiments while you sleep. Ten files; three that matter:
  `prepare.py` (frozen), `train.py` (agent's surface), `program.md` (human's
  "research org code").
- **Why it was worth studying:** The eighteenth study and a new genre — the
  **autonomous experimentation loop** — designed by the field's best
  simplifier. Nearly every line of `program.md` encodes a harness-design
  principle; several are new to the brain.

## Architecture at a glance

```
prepare.py   FROZEN: constants, data, tokenizer, dataloader, evaluate_bpb (the judge)
train.py     AGENT'S: model, optimizer, training loop — "everything is fair game"
program.md   HUMAN'S: the org code — setup ritual, loop, accept rules, autonomy contract
results.tsv  untracked experiment log: commit / val_bpb / mem / keep|discard|crash / description
git branch autoresearch/<tag>: commit → run → advance on improvement, reset on regression
```

## The design principles, one per mechanism

1. **A Goodhart boundary: the agent cannot touch the judge.** `prepare.py` is
   read-only and "the `evaluate_bpb` function is the ground truth metric";
   dependencies are frozen too. The experiment surface and the measurement
   apparatus are separated by a hard rule — reward hacking is excluded *by
   construction*, not by hoping the agent behaves. Any autonomous optimization
   loop without this boundary will eventually optimize the metric's
   implementation instead of the thing.

2. **Fixed wall-clock budget as the normalizer.** Every run gets exactly 5
   minutes of training regardless of what changed, so every experiment is
   directly comparable across architecture, size, and batch changes — and the
   loop converges on the optimum *for your hardware*. The tradeoff is stated
   plainly (results aren't portable across platforms). One decision buys
   comparability, predictable cost (~12 experiments/hour), and a natural kill
   criterion (>10 min → kill, discard).

3. **One scalar metric, chosen for invariance.** val_bpb is vocab-size-
   independent, so it survives the changes the agent is *allowed* to make.
   Metric selection is harness design: pick the number that remains meaningful
   under every legal move.

4. **Complexity is priced into the accept rule.** The "simplicity criterion"
   gives the hill-climber an exchange rate: "a 0.001 improvement that adds 20
   lines of hacky code? Probably not worth it. A 0.001 improvement from
   *deleting* code? Definitely keep. ~0 improvement but much simpler? Keep."
   Without this, an autonomous keep-if-better loop accretes complexity
   monotonically — every accepted hack becomes the baseline for the next. This
   is brain/00's complexity economics operationalized as a loop invariant.

5. **Git is the experiment ledger.** Fresh branch per run (`autoresearch/<tag>`
   must not exist), commit before each run, advance on improvement, `git reset`
   on regression; rewinds allowed "very very sparingly (if ever)". The
   brain/09 ledger pattern with git as the state machine — plus a human-facing
   `results.tsv` (deliberately untracked) logging every attempt including
   discards and crashes, so the *negative* results survive even though the code
   doesn't.

6. **Context hygiene inside the loop.** "Redirect everything — do NOT use tee
   or let output flood your context"; extract the metric with grep; read only
   `tail -n 50` on crashes. Token discipline written into the procedure, not
   left to agent judgment.

7. **A crash policy with bounded judgment.** Dumb failure (typo, import) → fix
   and re-run; fundamentally broken idea → log `crash`, move on; more than a
   few fix attempts → give up. The retry ladder and circuit breaker (brain/09)
   in three sentences.

8. **An explicit autonomy contract.** The NEVER STOP clause: no "should I
   continue?" — the human is asleep; and when out of ideas, *the idea-generation
   fallback is specified* ("read papers referenced in the code, re-read the
   in-scope files, combine previous near-misses, try more radical
   architectural changes"). Anti-stopping instructions plus a boredom protocol
   — the two things autonomous loops actually fail on.

9. **Two-level programming.** The human's job is explicitly moved up a level:
   "you're not touching the Python files… you are programming the `program.md`"
   — iterate on the *research org*, not the model. Substrate (frozen) /
   experiment surface (agent) / org code (human) is a three-layer contract, and
   the README frames org-code iteration as the real meta-game.

10. **Scope honesty in public.** Single NVIDIA GPU only; platform support
    refused ("would bloat the code… I'm not 100% sure I want to take this on"),
    with forks invited, concrete tuning advice for small machines given, and an
    offer to link notable forks. Maintainer boundaries as a feature.

## Questionable calls and tradeoffs

- **Greedy hill-climbing gets stuck on local optima** — rewind is discouraged,
  there's no population/branching search, no statistical treatment of run
  variance (a lucky seed can "improve" val_bpb). Deliberate: this is a
  baseline org design, and the README says the game is improving it. But users
  should know a 0.001 "win" may be noise — the harness measures once per idea.
- **The metric is the only truth.** Sample quality, downstream tasks, anything
  val_bpb misses is invisible to the loop — fine for pretraining research,
  fatal if copied naively to domains where the scalar is gameable or partial
  (Goodhart's law applies to the *choice* of judge even when the judge is
  frozen).
- **results.tsv untracked** keeps experiment noise out of git history but means
  the run log survives only on that machine — a deliberate ephemerality that a
  serious lab fork would want to revisit.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Autonomous optimization needs a frozen judge: hard-boundary the metric/eval from the agent's editable surface | read-only prepare.py | Any self-improving loop; without it, reward hacking is a matter of time |
| Normalize experiments by fixed budget (time/cost), not by configuration | 5-minute wall clock | Benchmarking, tuning loops, CI perf tests |
| Price complexity into the accept rule or hill-climbing accretes cruft monotonically | the simplicity criterion | Every keep-if-better loop, incl. agent-driven refactoring |
| Choose the metric that stays meaningful under every legal move | val_bpb vocab-invariance | Metric design for autonomous loops |
| Log every attempt including discards and crashes; the negative results are the research record | results.tsv | Experiment tracking everywhere |
| Give autonomous loops a boredom protocol, not just a stop rule | "if out of ideas, think harder: …" | Long-running agent loops |
| The human iterates on the org code, one level above the work | program.md framing | Agent-workflow design generally — the meta-lesson of this whole studies/ collection |

## Brain updates made

- `brain/09-agentic-engineering.md`: new section **"Autonomous experiment
  loops"** — frozen judge, fixed-budget normalization, invariant metric,
  complexity-priced acceptance, git-as-ledger with negative results logged,
  bounded crash policy, boredom protocol, and the two-level programming
  contract.
