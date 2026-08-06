# Study: Evidently

- **Repo:** https://github.com/evidentlyai/evidently @ `a4aa4c2` (2026-05-02)
- **What it is:** An open-source framework to **evaluate, test, and monitor** ML
  and LLM systems, from experiments to production. Tabular + text. 100+ built-in
  metrics from **data-drift detection** to **LLM judges**. `Report` (offline
  eval) + `TestSuite` (pass/fail assertions) + live monitoring, combined via
  `Preset`s. ~1,200 files.
- **Why studied:** Norman's silent-failure and score-drift blind spot. Maps to
  `core/observe/`.

## The three capabilities Norman needs

### 1. Data / prediction drift detection
The headline: statistical tests (KS, PSI, Wasserstein, etc.) that answer *is the
distribution moving?* For Norman: is the **Fit Score distribution** drifting (a
scoring change or a data-source change silently reshaping the board)? Are input
features (NYC head counts, funding amounts) trending in a way that signals a
broken lane rather than a real-world change? Drift is the *early* signal that
enrichment has quietly degraded — before the operator acts on a stale board.

### 2. The offline-eval → live-monitoring continuum
The same metrics run as a one-off `Report` (during development / calibration) and
as a scheduled monitoring job (in production). This is the bridge Norman is
missing: its calibration scripts are offline one-offs; Evidently's model is *the
same checks, promoted to a live monitor* — so "the scorer still ranks JD's labels
correctly" is watched continuously, not just at build time.

### 3. LLM-as-judge evals
Built-in LLM judges score generative outputs (groundedness, relevance, quality).
For Norman: score the **Second Pass** and enrichment narratives — is the priority
rationale actually grounded in the evidence? This composes with the guardrails
trust boundary (guardrails *blocks* bad output at write time; Evidently *measures*
output quality as a trend over time).

## The unifying shape: `TestSuite` = pass/fail gates on data + models
Evidently's `TestSuite` turns metrics into **assertions that pass or fail** —
which is the JustHireMe eval-harness idea (studies/justhireme.md) generalized from
scoring to *data quality and drift*. Norman's `evals/` should run both: labeled
scoring cases (JustHireMe) **and** drift/quality test suites (Evidently), in CI
offline and as a live monitor in production.

## Transferable lessons
| Lesson | Norman application |
|---|---|
| Drift detection (KS/PSI/Wasserstein) on scores + inputs is the early silent-failure signal | Watch Fit Score distribution + NYC-head/funding inputs for silent lane degradation |
| Same metrics as offline Report AND live monitor — promote calibration to a continuous watch | The calibration scripts become a scheduled monitoring job |
| LLM-as-judge evals for generative output quality over time | Score Second Pass / enrichment groundedness as a trend |
| TestSuite = pass/fail gates on data & models (drift version of the eval harness) | `evals/` runs scoring cases + drift/quality suites, in CI and in prod |

## Brain updates
- `brain/06`: **drift detection** and **LLM-as-judge evals**, plus the
  offline-eval→live-monitor continuum, added to the observability guidance
  (the runtime half of "notice when it goes quiet / when it drifts").
