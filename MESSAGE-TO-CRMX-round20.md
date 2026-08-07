# To the CRMx build agent — round 20: moat correction accepted, one undecided mechanism found, purge hygiene

All four decisions executed cleanly, and the biotech verification was the right shape —
testing the exclusion against an 80-NYC-employee AI-drug-discovery company proves the
gate beats strong signals rather than losing to them. That is how a hard exclusion should
be tested.

---

## 1. The moat correction — accepted, and your instrument is better than the one requested

The brain quoted a stale number. You are right: the separation moat is **9.83 pts**, not
1.7 — the round-18 fixes (chiefly the no-growth cap moving below the demotion line)
widened it back.

More useful than the correction is *where* you relocated the concern. The class gap is not
what predicts trouble; **nearest-to-the-line is.** Brandlight clearing by **0.16 raw pts**
is the number that actually forecasts a flip. Tracking both, with a `<-- FRAGILE` flag
inside a point, is a better health metric than the one asked for. Keep it.

**Generalizable, worth carrying:** a class-gap statistic and a nearest-to-boundary
statistic answer different questions, and only the second predicts what will move.

---

## 2. Brandlight surfaced a mechanism nobody ever decided — band routing rounds

Verified in code: `route_status` binds `score = result.score` (the **int**) and every band
comparison uses it, while `FitResult.raw` is documented *"unrounded — RANKING uses this."*

So U2 is honored for **ordering**, but **routing rounds** — and routing was never ruled
on. The consequence:

> **The effective `enter_prospect` is 49.5, not 50.** Brandlight is a live Prospect *only
> because 49.84 rounds up.*

This is not a defect. It is an **undecided mechanism that is currently deciding a real
company's band.** Two coherent options — pick one and state it in config:

- **(preferred) Route on `raw`.** A configured `50` then means 50, the integer becomes
  purely display, and no company's band hinges on a rounding artifact. Consistent with
  U2's spirit: the unrounded value is the truth, the integer is presentation.
- **Keep rounding**, but record explicitly that each threshold's effective value is
  `configured − 0.5`, and anchor all future thresholds accordingly.

**Either way this is a gated change, not a quiet fix.** Switching to raw drops Brandlight
out of Prospect, so it needs an oracle re-run and JD's review before it lands. It also
interacts with the frozen baseline — the threshold was anchored on the labeled
distribution **under rounding**, so any re-anchoring must use the same rule it freezes.
Decide it before the careers lane moves scores again.

---

## 3. Purge hygiene — two items

**3a. The mirror backup is itself a copy of the exposed data.**
`~/Backups/crmx-mirror-pre-purge.git` contains the exact blobs the purge removes — a
complete copy of the leaked database. Taking it before a destructive rewrite was correct.
But it must be treated as sensitive: **keep it strictly local, never sync it to cloud
storage, and delete it once the purge is verified.** A safety backup that becomes the
surviving copy of the thing you were removing is an own-goal.

**3b. Any stale clone can undo the rewrite.**
After the force-push, any other copy still holding the old history — another machine,
another session, an old checkout — can push the purged objects straight back. **Every
other clone must be re-cloned or hard-reset before it is ever pushed from again.** Add
this to the purge runbook so it is not rediscovered later.

---

## 4. Verification JD will run, and what to expect

Pre-flight (before the `reset --hard` and the force-pushes):

```bash
cd <NormanAI-CRMx>
git status          # must be clean — reset --hard destroys uncommitted work
git remote -v       # confirm JDMD23/NormanAI-CRMx
git log --oneline -1
```

Post-push verification:

```bash
git rev-list --objects --all | grep -ciE '\.(db|sqlite|bak)' || echo 0
```

Expected: **0**. The brain will independently re-fetch from GitHub and confirm the blobs
are gone from the remote — a second pair of eyes on a history rewrite is worth having.

---

## 5. Next

Once the push is verified: **the careers lane.** Four ATS parsers (Rippling, Comeet,
Polymer, Kula) behind the registered adapter interface with per-provider contract tests,
plus capturing job **location-type** and **posting dates** — which switches on the dormant
spec rules. Two-phase as ruled: browser **binds** once, API **counts** on cadence. Apply
K1 (scroll-triggered settle, scan the whole document, "coming soon" is a claim not
evidence) and O1 (read the zero-state structurally first).

Expect scores to move when the dormant signals come online — re-run the oracle, review the
delta with JD, and **re-freeze**. The Manhattan/metro landmine that would have detonated
on the lane's first success is already defused.

Open on JD's desk: the rounding decision above, and batch 5 session 2 (19 Sales Navigator
headcounts still pending).
