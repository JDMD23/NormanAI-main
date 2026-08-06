# 06 — Operations and delivery: how code gets to production and stays healthy

This is the domain most directly tied to *workflow optimization* — where engineering
quality converts into team speed.

## The delivery pipeline is the team's central nervous system

The four DORA metrics remain the best scoreboard: deploy frequency, lead time
(commit → production), change-failure rate, time-to-restore. Elite is deploy-on-demand,
lead time under an hour, failures rare and recovered in minutes. Every workflow
recommendation should trace to improving one of these without degrading another.

Pipeline standards:
- **One command** builds, tests, and runs the project locally from a fresh clone.
  If onboarding is a wiki page of manual steps, every environment is a snowflake and
  "works on my machine" is guaranteed.
- CI runs on every push; the main branch is always releasable. A red main is a
  stop-the-line event, not background noise.
- **CI under ~10 minutes** for the blocking path. Beyond that, developers batch
  changes, context-switch, and stop running tests locally — the slowdown compounds.
  Split slow suites: fast blocking tier, slower post-merge tier.
- Deploy is one command/click, automated, with automated rollback. Deploys that
  require a runbook and a senior engineer happen rarely, batch hugely, and fail big.
  Small frequent deploys are *safer*, not riskier — smaller diff, clearer blame,
  cheaper rollback.
- Trunk-based development with short-lived branches (<2 days). Long-lived branches
  are merge-conflict factories and delay integration feedback — the thing CI exists
  to provide. Feature flags decouple deploy from release when work spans deploys.

## Configuration and environments

- Config in the environment, secrets in a secret manager — never in the repo, never
  baked into images. One artifact promoted through environments; "built for prod"
  vs "built for staging" images mean staging tested nothing.
- Dev/prod parity within reason: same database engine, same versions. Docker Compose
  (or equivalent) for local dependencies so parity is cheap.
- Every dependency pinned via lockfile; upgrades are deliberate, small, frequent
  (automated PRs), not annual big-bangs. An unpinned build is unreproducible by
  definition.

## Observability: logs, metrics, traces — designed, not accreted

- **Structured logs** (JSON, key-value) with correlation/request IDs on every entry.
  A log you can't filter by request is a wall of noise. Log at boundaries and
  decisions, not every function entry. ERROR means a human should eventually look;
  alert-worthy means a human should look *now* — inflation of either destroys signal.
- Metrics for rates, latencies (percentiles, not averages — p99 is where users live),
  and saturation. The four golden signals (latency, traffic, errors, saturation)
  cover most services.
- Alerts page on *symptoms users feel* (error rate, latency), not causes (CPU%).
  Every alert must be actionable; an alert channel people mute is worse than none.
- The debugging question to design for: "a user says X failed at 3pm — can I find
  exactly what happened in under five minutes?" If not, observability has failed,
  regardless of how many dashboards exist.
- **For data/ML/LLM systems, add drift and quality monitoring — the silent-failure
  signal metrics miss** (evidently). A pipeline can be green on every golden signal
  while its *output distribution* rots: scores drift, an input feature trends
  wrong because a source quietly broke, an LLM's answers degrade. Run statistical
  drift tests (KS/PSI/Wasserstein) on key scores and inputs, and LLM-as-judge evals
  on generative output. The powerful move is the **offline-eval → live-monitor
  continuum**: the *same* checks you run as a one-off during development get
  promoted to a scheduled production monitor, so "the model still ranks the labeled
  cases correctly / the score distribution hasn't shifted" is watched continuously,
  not just at build time. This is the runtime complement to the eval harness
  (brain/03): eval gates catch regressions you ship; drift monitors catch
  degradations the *world* ships.

## Operational maturity

- Backups exist *only if restores are tested*. An untested backup is a hope.
- Runbooks for the known failure modes, written the first time each is handled.
- Blameless postmortems that produce *systemic* fixes (a guardrail, a lint, an alert),
  not "be more careful."
- Toil budget: anything done manually more than ~monthly gets automated or killed.

## Right-sizing (the failure modes)

Ops maturity must match stakes. A weekend project doesn't need SLOs and canary
deploys; a revenue system without rollback and alerting is negligent. The common
review findings at each extreme:
- **Under-built:** manual deploys, no staging, secrets in repo, no error tracking —
  fix in that order.
- **Over-built:** Kubernetes for one container, seven environments, a service mesh
  for three services, dashboards nobody opens. Complexity here taxes every deploy
  forever; simplify to the stakes.
