# Study: Open Policy Agent (OPA)

- **Repo:** https://github.com/open-policy-agent/opa
- **Studied:** 2026-08-10
- **What it is:** a general-purpose policy engine that decouples policy *decisions* from the
  services that *enforce* them, with policy written as a declarative artifact carrying its own
  test suite.
- **Why it was worth studying:** BK1 — `fresh_raise_growth_pts = 14` against a `growth` weight of
  `10`. **Not a code bug.** A relationship between two constants in a config file, where nothing
  owns relationships. Norman has ~180 rulings living as constants-with-prose-notes.

## Architecture at a glance

Three inputs, one output, and the separation is the point:

```
  RULES  (policy, declarative, versioned, tested)
  DATA   (the context the decision is about)
  QUERY  ("is this permitted?")            →   DECISION   →   the service ENFORCES
```

*"Services integrate with OPA by executing queries when policy decisions are needed."* The
service never contains the rule. It contains the *call* and the *enforcement*.

## What this codebase does exceptionally well

**1. Policy is an artifact, not a scattering.** The rule does not live in six `if` statements
across four modules. It lives in one place, is queried, and its answer is enforced elsewhere.
**This is the direct inverse of what a config file full of magic numbers does.**

**2. Policy has a test suite of its own.** Not "the code that uses the policy has tests" —
**the policy itself is subject to formal tests**, with coverage. That is the missing piece in
Norman: `config/fit-score.json` has 21 numeric constants and no test that asks whether they are
mutually coherent.

**3. The decision/enforcement split is a boundary, not a convention.** OPA *returns* a decision;
it cannot act. That means a policy bug produces a wrong answer, never a wrong action — the blast
radius is bounded by construction.

**4. Policies are reusable across systems** because they are decoupled from any one caller. The
same rule governs the API, the CI gate, and the admission controller.

## Questionable calls and tradeoffs

- **Rego is a real language with a real learning curve**, and its declarative/set-oriented model
  surprises people who expect imperative evaluation. They accepted this because a
  general-purpose policy language must express things a config schema cannot — but for a
  single-operator system, **the language is the part to leave behind.**
- **A separate process is an operational dependency** and a latency cost. Justified at
  infrastructure scale; absurd for Norman.

## Transferable lessons

| Lesson | Evidence here | Where it applies / limits |
|---|---|---|
| **Policy is an artifact with its own tests, not constants embedded in the code that obeys them** | Rego modules + `opa test` | Anywhere rules outnumber a handful; below ~10 rules, constants are fine |
| **Separate DECIDING from ENFORCING.** A decision-maker that cannot act has a bounded blast radius | query → decision → service enforces | Scoring, routing, gating; Norman already does this for scoring and not for config coherence |
| **The relationships BETWEEN constants need an owner.** A value can be individually valid and jointly incoherent | policy tests over the rule set | Any config with interacting thresholds, caps, floors, weights |
| Auditability comes free once policy is a versioned artifact | policy in VCS | Any regulated or contested decision |
| Do not adopt a policy *language* to solve a policy *organisation* problem | Rego's cost | Small systems: keep JSON, add the tests |

## Brain updates made

- `brain/07-decision-frameworks.md`: **the relationships between constants need an owner.** A
  config where every value is individually valid can still be jointly incoherent — a floor above
  the ceiling it feeds, a cap above the demotion line it is meant to sit under. Norman has now
  produced **both** of those (AY3 caught by boot validation; BK1 not caught).
- `brain/03-code-quality.md`: **a rule set deserves the same test discipline as code** — coverage
  over the rules, not only over the code that reads them.
