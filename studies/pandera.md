# Study: Pandera

- **Repo:** https://github.com/unionai-oss/pandera @ `106a663` (2026-08-05)
- **What it is:** A framework for **dataframe validation** — "statistically typed
  dataframes." Declarative schemas (columns with dtype, nullable, checks) over
  pandas / polars / pyspark, with coercion and rich failure reporting. A Union.ai
  open-source project.
- **Why studied:** The data-contract layer for Norman's boundary — the
  "parse-don't-validate" rule (brain/04) made mechanical for tabular enrichment.
  Maps to `core/trust/` and `core/contracts/`.

## The design worth stealing

- **Schema as a typed declaration.** A `DataFrameSchema` / `Column` declares
  dtype, `nullable`, and a list of **`Check`s** (value ranges, regexes, custom
  predicates). The schema *is* the contract, in code, versionable and testable —
  the tabular sibling of jsonschema (studies/jsonschema.md).
- **`coerce`** — the schema can *coerce* a column to its declared dtype on
  validation, not just assert. A declared fix, in the nonconformance-policy family.
- **Lazy vs eager validation — the sharp idea.** Default is eager: raise
  `SchemaError` on the **first** failure. `lazy=True` evaluates **all** checks and
  raises `SchemaErrors` with a structured **`failure_cases`** table — every row and
  column that failed, at once. For a data pipeline this is the difference between
  "fix one error, re-run, hit the next" and "see every problem in the batch in one
  pass." Norman's batch enrichment wants lazy: one report of everything wrong with
  a batch of 10 companies, not ten sequential surprises.
- **`nullable` as an explicit modeling statement** — a column is nullable or it
  isn't, declared, enforced (brain/04: nullability is a modeling statement;
  Unknown≠0). Missing is representable and validated, never silently zero-filled.

## Lessons for Norman
- **Validate enrichment data at the boundary against a declared schema**, before
  it enters the store — dtype, nullability, value-range checks per field. Parse
  once into a typed shape; interior code then trusts it (brain/04).
- **Use lazy validation for batches** so a batch-of-10 run surfaces *all* data
  problems as a structured `failure_cases` table (feeds Review-Required routing and
  the audit surface) rather than failing on the first bad row.
- **Coerce where safe, reject where not** — the coerce/raise choice is the
  nonconformance policy per column.

## The nonconformance-policy convergence (dlt + guardrails + pandera)
Three independent, mature frameworks — a data loader, an LLM guard, a dataframe
validator — all converged on the same core design this study round: **validation
is not pass/reject; it's a declared policy per rule for the nonconforming case.**
- dlt: `evolve / freeze / discard_row / discard_value`
- guardrails: `reask / fix / filter / refrain / exception / noop`
- pandera: `coerce (fix) / raise (freeze)`, eager-vs-lazy reporting
That convergence is now a first-class brain concept (`brain/04`).

## Transferable lessons
| Lesson | Norman application |
|---|---|
| Schema-as-typed-declaration with per-column checks is the tabular data contract | `core/contracts`: enrichment payloads validated before they hit the store |
| Lazy validation collects ALL failures into a structured table | Batch-of-10 enrichment: one failure report, not sequential surprises |
| `coerce` vs `raise` is the per-column nonconformance policy | Coerce safe types; route/reject the rest |
| nullable declared and enforced; missing ≠ zero | Unknown stays Unknown, validated, never zero-filled |

## Brain updates
- `brain/04`: pandera completes the **nonconformance-policy** convergence, and
  contributes lazy-collect-all-failures + coerce to the boundary-validation guidance.
