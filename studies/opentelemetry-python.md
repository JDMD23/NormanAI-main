# Study: opentelemetry-python

- **Repo:** https://github.com/open-telemetry/opentelemetry-python
- **Studied:** 2026-08-06 at commit `7bccdfc`
- **What it is:** The reference Python implementation of OpenTelemetry — the
  CNCF observability standard (traces, metrics, logs). A monorepo of
  independently versioned packages: `opentelemetry-api`, `opentelemetry-sdk`,
  semantic conventions, proto, exporters, propagators, shims. The canonical
  implementation of a large multi-language spec.
- **Why it was worth studying:** The best real example of two architecture
  principles the brain states but hadn't seen at standards-body scale: **API/SDK
  decoupling with a no-op default**, and **stability tiers encoded in the package
  structure itself**. Also brings the observability doc (brain/06) a concrete
  reference implementation.

## Architecture at a glance

```
opentelemetry-api/     interfaces + no-op defaults; what libraries depend on
opentelemetry-sdk/     the real implementation; what applications install
  api ← sdk            dependency points one way: SDK implements API, never reverse
semantic-conventions/  the shared vocabulary (attribute names) as a package
proto/ proto-json/     wire format (generated from the cross-language spec)
exporter/ propagator/ shim/   pluggable edges
rationale.md           why the versioning/stability model is what it is
```

## The two headline patterns

### 1. API/SDK split with a no-op default — instrumentation you can always add

The load-bearing decision: a **library** instruments its code against
`opentelemetry-api` only; an **application** chooses and installs an
`opentelemetry-sdk` (or doesn't). The API ships **no-op implementations** —
`NoOpTracer`, `NoOpMeter`, `ProxyTracerProvider` — so instrumentation calls in a
library do *nothing, cheaply*, until an application installs an SDK that a
`ProxyTracerProvider` then routes to. Consequences:

- **A library can instrument itself with zero cost imposed on its users.** No
  SDK installed → the calls are no-ops → no dependency forced, no overhead, no
  configuration required. This is the reason OTel instrumentation can live in
  third-party libraries at all: the API is a tiny, stable, side-effect-free
  contract; the SDK is the heavy, swappable implementation the *application*
  owns. Brain/02's dependency-inversion (depend on interfaces, choose
  implementations at the composition root) and brain/05's "return a safe default"
  fused into a distribution strategy.
- **The no-op is a real design artifact, not an afterthought.** `ProxyTracer`
  bridges the gap in time between "library imported" and "SDK configured" —
  early calls route to no-ops, then transparently switch to the real provider
  once set. Deferred binding done correctly (brain/01 temporal-coupling
  avoidance at framework scale).

The general lesson, now in the brain: **split a cross-cutting capability into a
thin stable API (with working no-op defaults) that everyone codes against, and a
heavy swappable implementation the application selects.** It's the only structure
that lets instrumentation, logging, or plugin hooks live in library code without
forcing cost or config on downstream users.

### 2. Stability encoded in package + naming structure

`rationale.md` makes the versioning model explicit and *mechanical*:

- **API stability is a cross-version promise:** code instrumented with
  `opentelemetry-api 1.0.1` works with `opentelemetry-sdk 1.11.33` *or* `1.3.4` —
  any same-major SDK. The contract users depend on is stated as a concrete
  compatibility guarantee, not a hope.
- **Experimental signals are marked in the code, by prefix:** immature signals
  ship "in the same packages as the core components, but prefixed with `_` to
  indicate they are unstable… NO STABILITY GUARANTEES." Stability is legible from
  the *import path* — `_logs` tells you what `logs` wouldn't. Pre-release
  suffixes (-Alpha/-Beta/-RC) layer on top.
- **"Public SDK stays backward compatible; internal interfaces are allowed to
  break."** The stable/unstable line is drawn deliberately and documented, so
  maintainers keep refactoring room exactly where users aren't standing.

This is brain/05 (compatibility is a discipline) made *structural*: the stability
of a thing is encoded in where it lives and what it's named, so a user can't
accidentally depend on an unstable surface without typing an underscore.

## What else it does well

- **`rationale.md` as a genre.** A whole document answering "why is the
  SDK/versioning shaped this way," so the reasoning "doesn't get lost over time" —
  ADRs (brain/07) elevated to a standing architectural rationale. Every large
  project should have this doc.
- **Semantic conventions as a shared vocabulary package.** Attribute names
  (`http.request.method`, …) are versioned shared infrastructure — the ubiquitous
  language (Pocock's CONTEXT.md, brain/09) at ecosystem scale, so every exporter
  and backend agrees on what a field means.
- **Spec-driven code generation** (proto, semantic conventions via `codegen/`)
  from the cross-language specification — the single source of truth is the spec,
  language implementations are generated/validated against it (jsonschema's
  shared-suite instinct, applied to wire format and vocabulary).
- **An AGENTS.md written to constrain AI contributors** with unusual specificity:
  "never post AI-generated comments on issues/PRs — discussions are for
  humans"; "keep AI-assisted PRs tightly isolated… never include unrelated
  cleanup"; "agree implementation direction with maintainers first." A standards
  body defending its human review process — the maintainer-burden concern
  (superpowers' slop-PR defense) formalized by a CNCF project.

## Questionable calls and tradeoffs

- **Ceremony is high — appropriately.** Monorepo, many independently versioned
  packages, tox matrices, per-signal stability suffixes, a spec to track. For a
  multi-language standard with thousands of downstream dependents this is
  *correct* weight (brain/00 scope honesty cuts both ways — this is the case that
  justifies the machinery), but none of it should be copied by a small app.
- **The API/SDK indirection has a learning cost.** New users routinely conflate
  the two packages and are confused that installing only the API produces no
  telemetry (by design). The power (no-op default, swappable SDK) is paid for in
  onboarding friction; docs carry the burden.
- **Underscore-prefixed public-ish modules** are a convention, not enforcement —
  nothing stops a determined user importing `_logs`; Hyrum's Law still applies to
  anything importable (brain/05), the prefix just makes the contract's intent
  legible.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| Split cross-cutting capability into a thin stable API with working no-op defaults + a heavy swappable implementation the app selects | opentelemetry-api vs -sdk, NoOpTracer, ProxyTracerProvider | Instrumentation, logging, plugin systems, any "libraries emit, app decides" concern |
| No-op defaults let libraries adopt a capability at zero cost/config to their users | NoOp* in the API | Any optional cross-cutting hook shipped in library code |
| Encode stability in structure: stable vs experimental legible from package + import name (`_`-prefix), with a stated cross-version compatibility promise | rationale.md + `_logs` etc. | Any library shipping stable and experimental surfaces together |
| Keep a standing `rationale.md`: why the architecture/versioning is shaped as it is, so decisions don't get lost | rationale.md | Any long-lived project (ADRs that outlive their PRs) |
| A shared vocabulary (semantic conventions) is versioned infrastructure the whole ecosystem depends on | semantic-conventions package | Multi-party systems needing agreement on field meaning |

## Brain updates made

- `brain/02-architecture.md`: added the API/implementation split with no-op
  defaults (thin stable contract everyone codes against + heavy swappable
  implementation chosen at the composition root; no-ops make library adoption
  zero-cost) to the dependency-rule section.
- `brain/05-apis-and-boundaries.md`: added encoding stability in structure —
  stable vs experimental legible from package/import name, with a stated
  cross-version compatibility promise, plus the standing `rationale.md` habit.
