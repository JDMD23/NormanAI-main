# Study: jsonschema

- **Repo:** https://github.com/python-jsonschema/jsonschema
- **Studied:** 2026-08-06 at commit `826e5b2`
- **What it is:** The reference Python implementation of JSON Schema validation —
  every draft (4 through 2020-12), pluggable formats and types, rich error
  trees, a CLI. ~4,600 lines of core, decades-hardened, a dependency of half the
  Python data ecosystem.
- **Why it was worth studying:** A pure specimen of **implementing a moving
  external specification** — the classical-engineering counterpart to all the
  agent tooling — and the cleanest real example of two brain principles:
  conformance-suite-as-shared-artifact and versioned-spec plugin architecture.

## Architecture at a glance

```
validators.py   create() factory + extend(); one validator class per draft,
                built from a keyword→function mapping (data-driven, not a class tree)
_keywords.py / _legacy_keywords.py   each schema keyword is a small function
_types.py       TypeChecker — pluggable, immutable type-definition registry
_format.py      FormatChecker — opt-in format validation, register by decorator
exceptions.py   ValidationError tree with JSON paths, best_match, error context
json/           the official JSON Schema Test Suite, vendored as a git submodule
```

## The two headline lessons

### 1. Conformance suite as a shared, external, executable artifact

The `json/` directory is the **official cross-language JSON Schema Test Suite**,
vendored as a submodule — the same test corpus every language's implementation
(Rust, Go, JS, Python…) runs against. The spec's meaning is defined by an
*executable* suite maintained *outside any one implementation*, and jsonschema's
own test run is largely "load the shared suite, run every case."

This is the langchain-tests lesson (studies/langchain.md) at ecosystem scale and
inverted in ownership: langchain *ships* a conformance kit to its implementers;
JSON Schema has a *communal* kit that all implementers consume. The principle
the brain gains: when a specification has multiple independent implementations,
the conformance suite is shared infrastructure that belongs to the *spec*, not
to any implementation — it's how "correct" stays a single agreed meaning across
a polyglot ecosystem, and how a new implementation bootstraps credibility (pass
the suite) without re-litigating semantics.

### 2. Versioned-spec plugin architecture: data over class hierarchy

There is no `Draft4Validator(BaseValidator)` inheritance tree. Instead,
`validators.create(meta_schema=…, validators={keyword: fn, …},
type_checker=…, format_checker=…)` *builds* a validator class from a **mapping of
keyword → validating function**; each supported draft is one `create()` call with
that draft's keyword set. `extend()` derives a new validator from an existing one
by overlaying keywords. Consequences:

- **A new spec version is data, not a subclass** — supply its keyword map. Draft
  differences are visible as diffs in a dict, not scattered across overridden
  methods (brain/01 information hiding: each keyword's logic is isolated in one
  small function; brain/08 avoids the god-class-hierarchy anti-pattern).
- **Users extend the same way the library does** — custom keywords, custom
  formats (`@FormatChecker.checks("uri")`), custom types (`TypeChecker.redefine`)
  are the *public* API, and the library builds its own drafts through it. The
  framework dogfoods its extension seam (the langgraph/langchain lesson again:
  the built-ins go through the public seam, so the seam is real).
- **Immutable, composable configuration** — `TypeChecker` is a frozen registry
  with `.redefine()`/`.remove()` returning new instances; validators are attrs
  classes. State is pushed to construction time (brain/01 temporal-coupling
  avoidance, brain/04 immutability).

## What else it does exceptionally well

- **Errors as a navigable data structure**, not strings. `ValidationError`
  carries the JSON path (`absolute_path`), the failing schema location, sub-errors
  for composite keywords, and helpers like `best_match` to surface the *one* error
  a human most likely cares about out of a combinatorial `anyOf` explosion. Error
  design as a first-class feature (brain/03) — validation's whole value is in the
  quality of the "why it failed."
- **Backward compatibility as a sacred contract.** Old drafts stay supported
  forever (`Draft4Validator` still ships); `_legacy_keywords.py` isolates the
  behaviors that changed between drafts so the current path stays clean while the
  old semantics remain exactly correct. Expand without contract, because the
  consumers (schemas written years ago) can't be migrated (brain/05).
- **Reference resolution isolated** behind a referencing library — the genuinely
  hard, security-sensitive part (`$ref`, remote schemas) is a separate concern
  with its own boundary, not tangled into keyword logic.

## Questionable calls and tradeoffs

- **`validators.py` at 1,410 lines** concentrates the factory, iteration engine,
  ref-resolution glue, and all draft definitions — coherent but at the upper edge
  of one-file comprehension (brain/03), a recurring finding in mature single-
  purpose cores (langchain's runnables, this).
- **The `create()` factory building classes dynamically** is powerful but opaque
  to newcomers and to static analysis — the price of data-over-hierarchy is that
  the class you're using has no literal source definition. A deliberate,
  correct trade for this domain; worth naming.
- **Draft sprawl is inherent** — supporting six spec versions forever is real
  permanent cost, mitigated (not removed) by the legacy-keyword isolation.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| A spec with multiple implementations needs a shared, external, executable conformance suite owned by the spec, not any implementation | vendored JSON Schema Test Suite | Any standard/protocol/format with >1 implementer |
| Model spec *versions* as data (keyword→function maps) built by a factory, not as a subclass hierarchy | create()/extend() | Anything supporting multiple versions/dialects of a spec |
| Build your own product through the public extension seam users get | drafts built via the same create/TypeChecker/FormatChecker | Extensible libraries; proves the seam and keeps it honest |
| Errors are a navigable data structure with a "most relevant" selector, never just a message | ValidationError tree + best_match | Validators, parsers, compilers, linters |
| Isolate behaviors that changed across versions so the current path stays clean and old semantics stay exact | _legacy_keywords.py | Long-lived libraries with backward-compat obligations |

## Brain updates made

- `brain/05-apis-and-boundaries.md`: extended the conformance-kit guidance —
  when a spec has *many independent* implementations, the suite is shared
  infrastructure owned by the spec (consumed by all), the communal counterpart
  to shipping your own kit; and model spec versions as data built by a factory,
  not a subclass tree.
