# Running the next batch — what it takes, what it costs, what's in the way

Grounded in the repo at `b805e90` and the real command signatures, not from memory.

---

## The pipeline is complete end to end, for the first time

Four days ago this stopped at "score." As of yesterday it runs:

```
CSV  →  ingest  →  enrich  →  score  →  route  →  project  →  contacts  →  chase list
```

Every stage exists and is committed. `brain/02` says architecture is *the decisions expensive
to reverse* — those are all made and they held: **SQLite is truth, Notion is a rebuildable
view, one reconcile loop keeps them converged.** Nothing in four days has forced a reversal of
that, which is the strongest signal available that the shape was right.

**What's in the box:** `core/` (entity, identity, store, contracts, guard, lanes, observe,
schedule, reconcile) · `contexts/` (discovery, fit, careers, contacts, priority) · `operator/`
(projection, board schema) · `evals/` (oracle, corpus, held-out gate) · 15 ADRs · 517 tests.

---

## The commands, verified

Everything defaults to **dry-run**; `--apply` writes. That's the round-27 rule — a dry run has
to be the apply path, or it's testing a different program.

```bash
# 0. session ritual — throttle state, tripwires, pending work
uv run python -m norman.tools.session_start   <db>

# 1. intake — new companies from the Crunchbase export
uv run python -m norman.tools.ingest_csv      <csv> <db> --added-from crunchbase:2026-08

# 2. careers lane — NYC roles, desk demand, posting dates    [FREE, no ban risk]
uv run python -m norman.tools.careers_lane    <db> --apply

# 3. Sales Nav headcount                                      [ATTENDED — the bottleneck]
#    no command: JD-supervised, 80 views/day cap, ~2 views per company

# 4. score and route
uv run python -m norman.tools.rescore         <db> --apply

# 5. push the board
uv run python -m norman.tools.reconcile_sweep <db> --apply

# 6. contacts                                                 [~4 Apollo credits / 50 cos]
uv run python -m norman.tools.contacts_lane   <db> --print-query
uv run python -m norman.tools.contacts_lane   <db> --apply <response.json>

# 7. the chase list
uv run python -m norman.tools.chase           <db> --limit 20
```

---

## The bottleneck is one thing, and it is not the code

**Sales Navigator headcount.** Attended, JD-supervised, capped at 80 views/day, measured at
**~2 views per company** (round 28 spent 82 views on 41 companies).

| work | cost |
|---|---|
| CSV ingest, scoring, routing, projection, chase list | **minutes** |
| Careers lane (public ATS APIs — Greenhouse, Lever, Ashby, Comeet) | **minutes, free, no account risk** |
| Contacts | **~4 Apollo credits per 50 companies** — measured, not estimated |
| **Sales Nav headcount** | **~2 attended days per 50 companies** |

**And there is a backlog before any new batch: 49 of the existing 95 still have no
denominator.** That's ~2 more attended days.

> **Clearing the backlog and adding 50 new companies is roughly 4 attended Sales Nav sessions.
> Everything else in the pipeline is minutes.**

---

## The one change that permanently lowers the cost of every future batch

**Schedule the careers lane.** From the build's own source:

```python
# src/norman/contexts/careers/fetch.py
# "...which is why it is the first lane cleared to run unattended."
```

It hits public job-board APIs. No login, no ban risk, explicitly cleared — **and there is no
scheduler, no cron, no CI, nothing that starts it.** The check ledger computes what's due;
nothing fires when it comes due.

If that lane ran on a timer, every new company would self-enrich on the free axis, and the
only human-gated step in the whole pipeline would be Sales Nav. **That is the difference
between a batch being "a day of work" and "a day of waiting."**

This has been true and unaddressed since day one. It is the last of the three findings from
the operational review still open — contacts closed, priority closed, **unattended operation
never started.**

---

## On the review loop — an honest read

Rounds 34–42 have run: brain finds defect → build fixes → brain verifies → brain finds next
defect. **Eight rounds, and the defects were all real** — a baseline recording nothing, a
config stating the opposite of the run, every contact stored twice, a migration that can't run
against the state it diagnosed.

**But that loop terminates only when someone stops looking, because there is always another
defect.** `brain/00` names it: *scope honesty*, and *feedback loops are the real product* —
the loop is supposed to feed the product, not become it.

**The stopping rule: review is gated on shipping, not the other way round.** Batch the open
defects into one list, fix them in one pass, and don't round-trip each one. The next round is
not a review round — it's a batch.

**Open defects, to be fixed in one pass rather than one per round:**
1. The dedup migration + the two row counts + the seeded-duplicate test *(round 42)*
2. The non-discriminating-field detector — ruled in round 30, parked, now twice demonstrated
3. The three Notion views — spec'd, JD builds them in the UI once
4. `last_touched_on` — the field exists and nothing writes it

None of these blocks a batch.

---

## The order I'd run it

1. **Schedule the careers lane.** Hours of work, and it's the only item that makes every
   future batch cheaper.
2. **Clear the 49-company denominator backlog** — 2 attended sessions. Finishing what's
   started beats widening it.
3. **Ingest the new CSV**, run careers + score + project. Minutes.
4. **Sales Nav on the new batch** — 2 attended sessions.
5. **Contacts + chase list** on the full board. ~4 credits.
6. The four open defects, in one pass, whenever.
