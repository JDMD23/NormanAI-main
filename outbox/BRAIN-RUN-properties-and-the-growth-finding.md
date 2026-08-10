# The property module — built, run, and it explains `newly computed: 0`

**Built, not specified.** `reference/properties.py` in NormansBrain — 135 lines, runnable against
any checkout:

```
python3 properties.py <path-to-crmx>
```

Run against `6d54b06`:

```
POLICY   PROPERTY               DETAIL
FAIL     P2 discriminates       growth: its input changed and its contribution did not
FAIL     P4 floor<=ceiling      fresh_raise_growth_pts=14 exceeds the 'growth' weight of 10
REPORT   P5 reachability        14 functions with no caller in src/
----
16 findings — 2 gate the build, 14 report only
```

**It independently confirms your Band 0 work:** `compute_velocity`, `changes_tags` and
`status_owner` no longer appear. The check found them before your fix and doesn't now.

---

## THE FINDING — the growth component needs data the intake source does not carry

Your `newly computed: 0` had a mechanism, and P5's report surfaced it. The chain:

```
compute_velocity        operates on DATED ROUNDS, ≥2 needed
funding_rounds table    written by exactly one method: add_funding_round (sqlite.py:957)
add_funding_round       NO CALLER IN src/
Crunchbase CSV          supplies latest_funding_round (a type string)
                        and funding_round_count (an integer)
                        — no dated round history at all
```

> **Nothing populates `funding_rounds`, and the CSV cannot.** Wiring `compute_velocity` could
> never have produced a new value, because its input table is fed by a method nobody calls, from
> a source that does not carry the data.

**This is not fixable by wiring.** It is a mismatch between what a scoring component requires and
what the intake source contains — and it means **`growth` cannot be computed for any
CSV-sourced company, ever, as currently designed.**

### The resolution is in JD's own spec, not in a preference

`FIT-SCORING-SPEC.md` §1b: a growth signal is **active in-office NYC hiring** *or* **fresh
funding**. Against what the system can actually obtain:

| growth signal | source | available? |
|---|---|---|
| active NYC hiring | careers lane | **yes** |
| fresh funding (date + amount) | Crunchbase CSV | **yes** |
| round-to-round velocity | `funding_rounds` | **no — nothing writes it** |

**Velocity is the one input of the three that the intake cannot supply.** So the honest shape:
**`growth` keys on hiring and funding recency — both obtainable — and velocity is a refinement
that applies only where dated round history happens to exist.**

That is not a weakening of the component. **It is the component matching its evidence**, and it
follows §1b rather than overriding it.

**Do not implement this before JD sees it.** It changes what growth means and that is his call.

---

## THE OTHER FINDING — four store writers nobody calls

```
add_funding_round · add_alias · set_salesnav_url · ledger_digest
```

`add_funding_round` is the one above. **The others are the same shape and deserve the same
question: what writes this table, and can the intake source supply it?**

`add_alias` in particular — the alias table is the identity/rebrand mechanism, and a rebrand is
exactly the case where it earns its keep.

---

## HOW THE MODULE IS BUILT, and why each choice

- **Properties, not examples** (`studies/hypothesis.md`) — *is this true of everything*, which is
  the only question that catches a component nobody wired.
- **Lazy, never fail-fast** (`studies/pandera.md`) — every violation in one table. Fail-fast
  would have shown P2 and hidden P4, and P4 is the one that says *why*.
- **Per-property policy** (`brain/04`) — `FAIL` gates the build; `REPORT` does not. P5 reports
  because a dead alias and a disconnected mechanism both trip it and only one is a bug. **A
  detector that fails on non-bugs gets silenced.**
- **P3 and P4 are the same rule, empirical and static.** P3 measures that no component exceeds
  its weight; P4 reads the config and says which constant caused it. **One tells you *that*, the
  other tells you *why* — keep both.**

---

## WHAT IT CANNOT DO WITHOUT THE LIVE BOARD

Three properties from the loop-3 spec need the database and are yours:

- every board column has ≥1 non-null
- no field is identical across all rows
- count of rows carrying a rule version older than current

**Wire this module into `make check` and add those three.** The scaffolding is done; they are
three more functions in the same shape.
