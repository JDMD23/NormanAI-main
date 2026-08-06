# Study: Guardrails

- **Repo:** https://github.com/guardrails-ai/guardrails @ `798d2c4` (2026-07-27)
- **What it is:** A Python framework for reliable LLM apps that does two things:
  (1) runs **Input/Output Guards** that detect, quantify, and mitigate risks in
  LLM inputs and outputs via composable **validators**; (2) generates **structured
  data** from LLMs. A Hub of pre-built validators, benchmarked (the Guardrails
  Index compares 24 guardrails across 6 risk categories).
- **Why studied:** Norman's biggest unbuilt exposure is untrusted scraped/LLM
  content becoming a written fact. Guardrails is the framework form of Research's
  hand-rolled evidence-clamp. Maps to `core/trust/`.

## The core design: validators + a declared on_fail action

A **validator** checks one property of an LLM input or output. What makes the
framework is the **`on_fail` action** — a *declared policy per validator* for what
to do when the check fails:
- **`reask`** — send the failure back to the model to try again (with the reason).
- **`fix`** — programmatically repair the value to a conforming one.
- **`filter`** — drop the offending field, keep the rest.
- **`refrain`** — refuse to return anything (the whole output is voided).
- **`exception`** — raise (hard stop).
- **`noop`** — record the failure but pass the value through.

**Guards compose validators** and wrap the model at the input *and* output
boundary. This is the mature, named version of what Research invented by hand:
its evidence-clamp (`fitHint → none` when unsupported) is a `fix`/`filter` action;
routing to Review Required is a `refrain`/`reask`; "no source URL = reject" is an
`exception`. And the on_fail vocabulary is *the same shape* as dlt's schema
contract and pandera's coerce/lazy — the **nonconformance-policy** convergence
(brain/04): validation is a declared policy per rule, not a boolean.

## The other half: structured generation
Guardrails also constrains an LLM to emit data matching a schema (with the same
on_fail machinery to repair/reask when it doesn't) — directly Norman's need to
turn Grok/enrichment output into typed, trustworthy fields rather than free text.

## Lessons for Norman
- **Guard both boundaries.** An *input* guard sanitizes scraped page content
  before it reaches the enrichment prompt (the prompt-injection defense — scraped
  pages are untrusted input); an *output* guard validates the model's claims
  before they become facts (the hallucination defense).
- **Every validator carries a declared on_fail action** — reask / fix / filter /
  refrain / exception / noop — chosen per risk. Norman's Review-Required reason
  codes are on_fail actions; make the mapping explicit.
- **Prefer a validator hub + benchmarked measures** over bespoke checks where one
  exists (PII, toxicity, competitor-mention, groundedness) — but Research proves
  the highest-value validator here is domain-specific (evidence-groundedness) and
  cheap to hand-write.

## Transferable lessons
| Lesson | Norman application |
|---|---|
| Validator + declared on_fail action (reask/fix/filter/refrain/exception/noop) | Every LLM-touching stage in `core/trust`; Review-Required reasons ARE on_fail actions |
| Guard both input and output boundaries | Input guard = injection defense on scraped pages; output guard = hallucination defense before writes |
| Constrain LLMs to emit schema-conforming structured data, repair/reask on miss | Grok/enrichment output → typed fields, not free text |
| Groundedness is the load-bearing validator; often cheap and domain-specific | Generalize Research's evidence-clamp into a reusable groundedness guard |

## Brain updates
- `brain/09`: the guardrails **on_fail action taxonomy** and **input+output
  guards** added to the trust-boundary section (generalizing Research's clamp).
- `brain/04`: guardrails is one of the three pillars of the **nonconformance-
  policy** convergence.
