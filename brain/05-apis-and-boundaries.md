# 05 — APIs and boundaries

An API here means any contract with consumers you don't control at edit-time:
HTTP endpoints, library public surfaces, CLI flags, event schemas, file formats.

## The prime directive: easy to use correctly, hard to use incorrectly

Every other API rule derives from this. Concretely:
- The obvious way to call it should be the right way. If correct usage requires
  reading docs about call ordering, flag interactions, or cleanup obligations, the
  design has failed — encode the obligation in the shape (context managers, builders
  that can't produce invalid configs, required parameters instead of "remember to set").
- Defaults do the safe, common thing. Danger requires explicit opt-in.
- Symmetry: operations that look parallel behave parallel (`open`/`close`,
  `add`/`remove` take the same argument shapes, plurals behave like collections).

## Design from the caller's side

Write the calling code first — real examples for the top three use cases — then build
the API that makes those examples clean. APIs designed from the implementation outward
export their internals (the "how" leaks into every signature) and force every caller
to do the assembly the library should have done.

Minimalism compounds: every public method, parameter, and exported type is a promise
you must keep forever. **When in doubt, leave it out** — adding later is trivial,
removing later is a breaking change. Private-by-default everything.

## Compatibility is a discipline, not an intention

- Additive changes are safe: new endpoints, new optional fields, new enum values
  *only if* consumers were told to handle unknowns.
- Breaking changes need a version and a migration window — or better, expand/contract:
  ship new alongside old, migrate consumers, remove old. Silent behavior changes are
  the worst kind of break because nothing fails loudly.
- Encode stability in *structure*, so a user can't accidentally depend on an
  unstable surface: make stable vs experimental legible from the package and
  import name (OpenTelemetry ships experimental signals `_`-prefixed in the same
  package — `_logs` vs `logs` — "NO STABILITY GUARANTEES"), and state the
  cross-version compatibility promise concretely (API 1.0.x works with any
  same-major SDK). Draw the "public stays compatible, internals may break" line
  deliberately and write it down. Keep a standing `rationale.md` explaining why
  the versioning/architecture is shaped as it is, so the reasoning outlives the
  PRs that made it (studies/opentelemetry-python.md).
- Hyrum's Law: with enough users, *every observable behavior* becomes a dependency —
  error message text, ordering, timing. Minimize observable surface; document what's
  contractual vs incidental.

## HTTP/REST specifics that actually matter

- Resources and verbs used honestly (GET is safe and cacheable, PUT idempotent);
  nobody cares about REST purity beyond that.
- **Idempotency keys on any mutating endpoint a client might retry** — payments and
  order creation especially. Retries without idempotency are duplicate-writes waiting
  for a network blip.
- Errors: structured bodies (machine-readable code, human message, correlation ID),
  correct status classes (4xx caller's fault, 5xx yours). Never 200-with-error-inside.
- Pagination from day one on every collection endpoint (cursor-based if data churns);
  retrofitting pagination onto consumers that assume "the whole list" is misery.
- Rate limits and timeouts documented as part of the contract.

## Library and internal-module boundaries

- Accept interfaces, return concrete types. Depend on the narrowest thing that works
  (a function takes a `Reader`, not a `File`; takes the two fields it needs, not the
  whole config object) — this is what makes code testable and reusable for free.
- Don't force your dependencies on callers (log via an injected/standard interface;
  don't mandate a global logger config, a specific runtime, a singleton).
- Wrap third-party SDKs you don't control behind a thin interface you do — sized to
  your usage, not theirs. When the vendor changes or gets replaced, one file changes.
  Exception: don't wrap the standard library or the framework you've committed to;
  wrapping everything is ceremony (see 02, failure modes).
- When third parties implement *your* interfaces (plugins, providers, drivers),
  ship the conformance test suite as a versioned artifact they subclass and run —
  the contract becomes executable and evolves centrally. Treat new tests as
  breaking changes for implementers (they'll pin; document that). Below a handful
  of implementers, plain integration tests suffice. (Evidence: langchain-tests.)
- The consumer-side inverse: when *you* depend on a third-party service, pin the
  behaviors you assume with contract tests in your own suite — response shapes,
  paging, error forms, consistency timing — so vendor drift fails your CI as a
  red test instead of failing production. (Evidence: MiroFish's Zep contract
  tests.)
- When a *spec* has many independent implementations (a format, protocol, or
  standard), the conformance suite is shared infrastructure owned by the spec and
  consumed by all implementers — the communal counterpart to shipping your own
  kit. It keeps "correct" a single agreed meaning across a polyglot ecosystem and
  lets a new implementation earn credibility by passing it. And model the spec's
  *versions* as data (a keyword→function map built by a factory), never as a
  subclass hierarchy — a new version is a new mapping, and each rule stays
  isolated in one small function. (Evidence: jsonschema's vendored JSON Schema
  Test Suite + `create`/`extend`.)
- Deprecation deserves machinery, not comments: decorators that emit warnings, a
  beta marker for the opposite lifecycle end, and suppression for *internal*
  callers so only users see warnings — warning noise is interface cost too.

## Provider adapters: the N-integration pattern

When you integrate N interchangeable providers (payment gateways, storage
backends, LLM vendors, job-board APIs), the durable shape (ats-scrapers is the
reference — studies/ats-scrapers.md):
- **ABC interface + decorator registry as the *only* lookup.** Each adapter is
  one self-registering file implementing one method; callers resolve by registry
  key, never by importing adapter classes by path. A new provider adds a file
  and touches nothing else.
- **Declare per-provider capability as class-attribute data**, consumed by a
  shared client — HTTP engine, auth mode, escalation policy, headers. Default to
  the cheap path; make the expensive one (browser engine, impersonation, extra
  auth) an opt-in declaration on the adapters that provably need it. Behavior
  lives in the shared client; only the *declaration* varies per provider.
- **Capture the provider's quirks in a docstring beside the adapter** — the
  exact endpoint, what the API does and doesn't return, the costly flags, the
  rate-limit reality. This is the knowledge-delta principle (brain/09) aimed at
  external APIs: the next maintainer inherits the hard-won knowledge or relearns
  it by outage.
- **Pair a contract test with each adapter** so upstream drift fails your CI,
  not production (brain/05 consumer-side contract tests).

## Tools and MCP servers are APIs for agents

A tool/MCP surface is an interface whose consumer is a model; design it as
deliberately as any public API (linkedin-mcp-server is the reference —
studies/linkedin-mcp-server.md):
- **Annotate operation semantics** the model needs to choose safely — read-only
  vs mutating, open-world, tags/titles. **Confirmation-gate every mutation**;
  reads flow freely (safe-by-default at the tool layer).
- **Expose selection arguments** (which sections/fields) so the agent fetches
  only what it needs — index-then-fetch economics (brain/09) built into the
  signature, not left to the agent to overfetch.
- **Curate the agent-visible schema separately from the implementation** — hide
  internal/DI parameters from the tool's declared inputs; validate and bound
  inputs at the boundary (parse-don't-validate, brain/04).
- **Return partial failure in band**: per-part results *plus* typed per-part
  errors, so one broken piece returns the working pieces and a structured error
  for the rest — expected failures are values (brain/01), shaped for a consumer
  that can act on partials. Bonus: make each error carry a pointer toward its own
  fix (an issue-template path), so tool breakage is a feedback loop.

## Events and messages as APIs

Event schemas are the hardest contracts to evolve because consumers are invisible.
Name events as past-tense facts (`OrderPlaced`), include a schema version from the
first event, never remove or re-type fields, and treat the event catalog as
documentation-worthy API surface. If you can't enumerate a topic's consumers,
you can't ever break it — design accordingly.
