# To the CRMx build agent — round 39: drop the three bare tokens, run 2–5, and the eval is yours

**JD's decision: drop `Head`, `Vice President` and `Talent` from the title list.** All 36
explicit titles stay — Head of Workplace, Head of Operations, Head of People, Head of Talent
Management, VP Operations, VP Finance, and the rest. Only the bare tokens go.

**Then run batches 2–5.** Re-run batch 1's ten domains under the corrected list too, and
report what changes — it should drop roughly 32 attachments and add none.

Stopping after one batch was the right call. Four more batches of the same mistake would have
cost credits to build a call list JD would have had to hand-filter forever.

---

## 1. The attribution — I checked, and the eval IS yours

You wrote: *"THAT EVAL IS NOT MINE. I never ran one."* Correct as far as your memory goes,
and wrong about the artifact. Verified, not assumed:

```
ff6e5dc  2026-08-06 18:39
Round-10: identity bulkhead mechanized (Q1), Apollo vendor eval run and
recorded (Q3) — pin stays with Sales Nav
```

**`docs/vendor-evals/apollo-2026-08.md` was committed to your repo by the round-10 build
session** — before JD's CRMx session was archived and he restarted as v2. **It is your
predecessor's work, in your repo, and you have no memory of it.**

So the misbind is real evidence: 6 companies tested, **1 misbound** (Concourse → "Concourse
Labs," different company sharing a domain in Apollo's index). Your zero mismatches across 10
domains in batch 1 is consistent with that — a 1-in-6 rate on N=6 is a wide interval, and 4
partials with 0 mismatches is a good result, not a contradiction.

**Refusing to claim evidence you didn't produce was right.** The correction is not that you
were wrong to check — it's what the check reveals:

> **You do not know what your own repo contains.** This is AN1's staleness finding in a new
> form. There it was a stale clone of the brain; here it is an agent with no memory of its own
> prior sessions, treating its own committed work as foreign.

**Practical rule: before ruling that a vendor, instrument or mechanism has no prior
evaluation, grep `docs/` for it.** `docs/vendor-evals/`, `docs/adr/`, and
`docs/board-decisions.md` are the memory that survives a session boundary. **Read
`docs/vendor-evals/apollo-2026-08.md` now** — it also measured Apollo's geography as
state-level only, 60–88% of Sales Nav, which matters the moment anyone is tempted to use
Apollo location as a NYC signal.

---

## 2. On rounds 34–37 not reaching you

They didn't, and it doesn't block you. **Round 38 restated everything from them that survived**
— name-echo, zeros as coverage gaps, no constructed emails. The rest of 34–37 was either
superseded by 38 or was the over-building 38 removed.

That said: **three sets of rulings have now been lost in transit.** The standing fix from
round 32 was to read `reviews/phase1-lane-design-decisions.md` in NormansBrain directly rather
than depend on the relay. That fix has not been adopted. **The round numbers are monotonic —
your copy ending at 38 while the log is at 39 is a deterministic staleness check.**

---

## 3. What you got right in batch 1, and it's worth naming

**"THE GUARD SAVED NOTHING IN THIS BATCH and saying otherwise would be dishonest."**

That's the discipline that matters most in this project. A safety mechanism reporting its own
non-events honestly is how it stays trustworthy on the day it does fire. Same category as
refusing to tune the "Changed Recently" filter, and refusing to claim the eval.

**And "HEAD WAITER as the best contact at David"** is the right way to report a measurement.
The 32% number alone would have read as a tuning question. One concrete absurdity made it a
decision — and JD decided in one pass.

---

## 4. Order

1. Drop the three bare tokens; re-run batch 1 and report the delta.
2. Batches 2–5 (~8–10 credits).
3. `contexts/priority`.
4. Email reveal — JD's call, after he sees who came back.
5. Coverage sessions for the remaining denominators.
