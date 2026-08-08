# To the CRMx build agent — round 24: two JD notes, and the finding you're under-rating

Phase A is good work. The three live-data landmines are the argument for contract tests
against recorded payloads, and two of them deserve to survive as phrasing because they are
**field-level restatements of Unknown≠0**:

> *"A junk city value is no evidence, not evidence of absence."*
> *"A secondary location is a different place, not a modifier on this one."*

Both belong in the render/parse protocol permanently. Same for the provider-gap
discipline — **one undated role withholds the whole freshness count; a partial count is
not a smaller count, it is a wrong one.** That is the right instinct and it is rarer than
it should be.

---

## 1. JD's two notes from the report

**"Hybrid still should be valued."** Already satisfied — verified in the live config:
**in-office 1.0 · hybrid 0.8 · remote 0.15**, and Evertune's 8 all-hybrid roles → 6.4
desks confirms it end-to-end. A hybrid worker still needs a desk, just a shared one, so
0.8 matches the physical reality. **No change — but put the number to JD explicitly for
confirmation rather than assuming 0.8 is his.** It is a live knob and he is the authority.

**"It's a great idea to see the TYPE of job and ROLE for NYC."** Read this precisely: the
in-office/hybrid/remote split and the role mix are **evidence he wants to look at**, not
just inputs to a number. Right now they live only inside the score.

**Surface the breakdown on the company card:**
```
14 NYC roles · 1 in-office / 12 hybrid / 1 remote → 10.8 desks
```
That makes the desk number *legible* rather than asserted — the same discipline as the
scorer's self-explaining `why`. It also makes his spot-checks self-serve instead of
requiring you to assemble them. Fold into S6; it raises that work's value.

---

## 2. The §4 finding is bigger than you framed it, and the root cause is the lesson

`dormant_signals` was a **hand-typed list of seven**. Derived, it returns **sixteen** —
and so `tau 1.0` is computed over roughly **86 of the formula's 100 points**. The gate
has never seen HQ, funding stage, founded date, or the trend fields.

You called it uncomfortable. The uncomfortable part isn't the number — it's the mechanism:
**the list of what was missing was itself maintained by hand, so it drifted. And a
self-description that drifts is invisible precisely because it reports something.**

That is the same family as `docs/invariants.md` overstating enforcement, and the
"declared but inert" class. Three incidents now, one shape.

**Standing rule: anything that describes the system's own state or coverage — dormant
signals, invariant coverage, which configs are gated, which rulings are implemented —
must be DERIVED from the system, never typed by a human.** A typed self-description is a
*claim*; a derived one is a *measurement*. Where derivation is genuinely impossible, the
artifact must say **"hand-maintained, may drift"** in its own text.

Your fix is right and needs no backfill — `freeze_evidence` now captures all 32 fields and
the post-round-17 overrides carry the full set, so **the corpus self-heals as it grows.**
That is the correct resolution rather than the AD2-violating alternative. Report the
covered-points figure alongside tau from now on, so "gate passed" carries its own scope.

---

## 3. The reconcile finding — you're calling it an implementation note; it's an architecture gap

This is the sharpest thing in the report and it deserves more than synchronous projection.

Reconcile compares **board vs store** and infers *"they differ, therefore JD edited the
board."* When a lane writes and projection hasn't run, the store has moved ahead — so it
planned to **adopt stale board values back over fresh measurements** and revert both
status moves. Caught in dry-run only.

**That is a missing common ancestor.** You cannot tell *who* changed from a two-way diff.
You need the base state — a three-way merge.

**Ruling: build the last-projected baseline** (per company, the values as of the last
successful projection). Then the inference becomes a determination:

| condition | meaning | action |
|---|---|---|
| board ≠ base | **JD edited** | adopt |
| store ≠ base | **a lane advanced** | project; do not adopt |
| both ≠ base | **genuine conflict** | surface to JD — never silently pick a side |

Synchronous projection is correct **as an interim**, but it is a **discipline someone must
remember, not a mechanism** — and it is on a collision course with your own architecture:
**the outbox exists precisely to decouple producers from the writer, so the first
genuinely async lane re-opens this bug.**

Therefore: **the last-projected baseline is a prerequisite for the outbox becoming durable
and async**, and until it exists, **assert synchronous projection with a test** rather
than leaving it as a note. Your own line — every previous lane happened to project
synchronously — is luck being mistaken for design, and you were right to say so.

---

## 4. Coverage reporting — keep doing it this way

53 of 85 boards (62%, floor 35%), with the 31 unrecognized boards and the client-side Kula
board **named as a separate K1 render pass** rather than folded in as a vague gap. That is
how partial coverage should be reported: **a named remainder with an owner, not a
rounded-up headline.** Keep the static-discovery hit-rate as an observe metric (M5) so the
62% is tracked over time rather than re-derived by hand — which, per §2, is exactly the
habit to avoid.

---

## 5. Order from here

1. **JD's spot-check** on the seven desk-vs-raw divergences (going to him now, with the
   hybrid weight put to him for confirmation).
2. **The last-projected baseline** — before Phase B, because Phase B writes more lane data
   into the same path that just tried to revert itself.
3. **Phase B** — ~30 real titles validated with JD before the classifier feeds the score.
   Good catch on Comeet's declared `experience_level`: **prefer a provider's declared field
   over a title heuristic wherever it exists**, and treat the heuristic as the fallback for
   providers that don't publish one — same shape as declared-vs-inferred location.
4. **S6's three views + U2** (`fit_raw` persisted), now carrying AE2's breakdown display.
5. Still outstanding: the tracked-data-artifact CI assertion, and JD deleting
   `~/Backups/crmx-mirror-pre-purge.git`.
