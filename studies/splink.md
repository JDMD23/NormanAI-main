# Study: Splink

- **Repo:** https://github.com/moj-analytical-services/splink @ `0a3bc99` (2026-08-05)
- **What it is:** Fast, scalable **probabilistic record linkage / entity
  resolution** — deduplicate and link records from datasets that lack a shared
  unique ID. Fellegi-Sunter model, unsupervised (EM, no training data), runs on
  DuckDB (a million records in ~a minute) or Spark. Used across UK government,
  academia, industry (ONS census linkage).
- **Why studied:** Norman's identity resolution is load-bearing (brain/10 #6) and
  hand-rolled. Splink is how specialists do it. Maps to `core/entity/`.

## How entity resolution is actually done (the pipeline)

1. **Blocking** — don't compare all N² pairs; generate *candidate* pairs via
   blocking rules (e.g. same postcode, or same first-3-of-name), then only score
   those. This is the scalability trick and the first design decision.
2. **Comparison** — for each candidate pair, compare each field at graded
   **levels** (exact / fuzzy-near / different) using a comparison library
   (name, date, fuzzy) — *not* a single boolean same/different.
3. **Match weights via m/u probabilities** — for each level, learn two numbers:
   **m** = P(this level | records truly match), **u** = P(this level | they
   don't). The ratio is the evidence weight. Learned **unsupervised via
   Expectation-Maximisation** — no labeled pairs required.
4. **Term-frequency adjustments** — matching on "Smith" is weaker evidence than
   matching on a rare surname; the model adjusts for value frequency.
5. **Match probability → clustering** — sum weights to a probability, threshold,
   then **cluster** the pairwise links into entities (a canonical ID).

## The lessons for Norman

- **Identity is probabilistic evidence-weighing, not string equality.** Norman's
  "is this the same company?" (rediscovery idempotency, the `identity conflict`
  Review-Required reason) is a Fellegi-Sunter problem: compare name + domain +
  LinkedIn + HQ at graded levels, weight the evidence, threshold. RapidFuzz
  supplies the fuzzy *levels*; Splink supplies the *weighing and clustering*.
- **Blocking is the design decision that makes it tractable** — pick blocking
  keys (domain, normalized name prefix) so you never compare all pairs.
- **Multiple non-correlated fields beat one strong field.** Splink "performs best
  with multiple columns that are not highly correlated" and is explicitly *not*
  for a single bag-of-words. Norman has exactly the right shape (name, domain,
  LinkedIn URL, HQ, sector) — use them all, and note correlation (domain↔website).
- **Term-frequency adjustment** is the sharp idea most hand-rolled matchers miss:
  a match on a common token is weak evidence; weight rare-value matches higher.
- **Diagnosable by design** — interactive match-weight charts let you see *why*
  two records linked. Norman's identity decisions should be explainable (feeds the
  Review-Required card).

## Transferable lessons
| Lesson | Norman application |
|---|---|
| Entity resolution = block → compare-at-levels → weight (m/u) → cluster | The identity resolver in `core/entity/`; the `identity conflict` reason code |
| Weigh multiple non-correlated fields, not one; graded levels not booleans | name+domain+LinkedIn+HQ+sector, each fuzzy-graded |
| Term-frequency adjustment: rare-value matches carry more weight | Don't over-trust a match on a common company-name token |
| Blocking keys make it tractable and are a first-class design choice | Block on domain / normalized-name-prefix before scoring pairs |
| Make the match explainable | Surface *why* two sources linked in the Review card |

## Brain updates
- `brain/04`: identity-resolution depth added to the "make illegal states
  unrepresentable / identity before write" guidance — probabilistic linkage
  (block→compare→weight→cluster), not string equality.
