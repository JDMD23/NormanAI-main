# Study: dlt (data load tool)

- **Repo:** https://github.com/dlt-hub/dlt @ `2d25092` (2026-08-05)
- **What it is:** A Python library that automates loading data from any source
  into any destination — with **automatic schema inference and evolution**,
  **incremental loading**, and declarative **write dispositions**. Drops into a
  notebook, a Lambda, an Airflow DAG, or an agent. ~2,100 files, mature.
- **Why studied:** The mature form of Norman's enrichment pipeline + causal
  outbox. Maps to `core/store`, `core/outbox`, `core/lanes`.

## The three ideas Norman needs

### 1. Write disposition as a declared policy per resource
Every load declares how it merges: **`append`** (add rows), **`replace`**
(overwrite), or **`merge`** (upsert on `primary_key`, deduping overlapping items
with the same cursor). Norman's writes are ad-hoc per lane; making disposition an
explicit per-resource declaration — merge-on-identity is the upsert every
enrichment lane wants — turns "how does this write combine with what's there?"
from tribal knowledge into a typed field.

### 2. Incremental cursor persisted in state
`dlt.sources.incremental('created_at', initial_value=...)` stores a cursor in
persistent pipeline state and resumes from the last value; `primary_key` dedups
overlapping items across runs. This is exactly Norman's funding-watcher ledger —
dlt is the generalized, tested version. **Cursor + primary-key dedup = idempotent
incremental ingestion** (brain/10 #6), the core loop of every scheduled source.

### 3. Schema contracts with evolution modes — the standout
The killer feature. A resource declares a **schema contract** over three
entities (`tables` / `columns` / `data_type`), each with an evolution mode:
- **`evolve`** — accept the new shape, migrate the schema.
- **`freeze`** — reject data that doesn't fit (raise).
- **`discard_row`** — drop the whole nonconforming row.
- **`discard_value`** — drop just the offending value, keep the row.

This is **the answer to "what happens when incoming enrichment data doesn't match
what we expected?"** — a *declared policy per field family*, not a scattered pile
of `if` statements. And it converges with two other repos studied this round
(guardrails' `on_fail`, pandera's coerce/lazy) on the same insight — see the
**nonconformance-policy** concept now in `brain/04`. Plus **versioned schemas
with explicit upgrade paths** (`migrations.py`) and **versioned+hashed pipeline
state** — resumable and diffable.

## Transferable lessons
| Lesson | Norman application |
|---|---|
| Write disposition is a declared per-resource policy (append/replace/merge-on-key) | Every lane declares its disposition; merge-on-identity is the enrichment upsert |
| Incremental cursor in persistent state + primary-key dedup = idempotent ingestion | The funding watcher and every scheduled source, generalized |
| Schema contract with evolution modes (evolve/freeze/discard_row/discard_value) | The store + trust boundary: a declared policy for nonconforming enrichment fields |
| Versioned schema with explicit upgrade paths; versioned/hashed state | The SoR migration story (expand/contract, brain/05) |

## Brain updates
- `brain/04`: new **"Validation is a declared nonconformance policy, not a
  boolean"** section (dlt schema contracts + guardrails on_fail + pandera),
  and schema-evolution modes added to the data-crossing-boundaries guidance.
