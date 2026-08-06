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
- Deprecation deserves machinery, not comments: decorators that emit warnings, a
  beta marker for the opposite lifecycle end, and suppression for *internal*
  callers so only users see warnings — warning noise is interface cost too.

## Events and messages as APIs

Event schemas are the hardest contracts to evolve because consumers are invisible.
Name events as past-tense facts (`OrderPlaced`), include a schema version from the
first event, never remove or re-type fields, and treat the event catalog as
documentation-worthy API surface. If you can't enumerate a topic's consumers,
you can't ever break it — design accordingly.
