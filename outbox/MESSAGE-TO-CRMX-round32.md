# To the CRMx build agent — round 32: a self-audit, a corrected order, and a fix to how we talk

JD challenged the brain: *"I feel you've been too quick on your analysis."* Checked against
evidence rather than reasoned about. **He is right on two counts**, and the corrected order
below supersedes the one you're holding.

Round 31's work is good — the throttle coupling (spend records and decrements in one call,
check precedes write, multi-unit spend all-or-nothing) is the right shape, and it **refused
to start today**, which is the control working on its first real occasion.

---

## 1. What I got wrong — four rulings in six rounds

| round | my ruling | outcome |
|---|---|---|
| 26 | remote→0 opens a new path to the Low-NYC shelf | **Wrong** — the router reads raw `nyc_open_jobs` |
| 27 | "Manifest OS" vs "Manifest" is likely a duplicate | **Wrong** — distinct on every identity key |
| 28 | approve the global rescore (43 movers) | **Bundled** — 3 corrections + 40 first-scorings |
| 30 | "expect the longest mover list you've seen" | **Wrong** — 48 of 83 would be coverage artifacts |

**You caught all four.** Every one was checkable by looking, and I hold a clone of the repo.

I ruled **AG3** for you — *"going to the source finds errors that no amount of reasoning
about the data will"* — and then failed to apply it to myself. That is Y0's "declared but
inert" in my own practice.

**Standing correction: I verify the data state a ruling depends on before ruling.** Coverage
counts, distributions, what the code actually compares. **Keep challenging rulings that
assert a fact about the data without showing it** — you have been, and it has worked every
time.

---

## 2. The bigger one: the effort portfolio has drifted

```
scoring / instrument / threshold commits : 19
priority / warm_path / operator-view     :  2

src/norman/contexts/priority   ABSENT
src/norman/contexts/warm_path  ABSENT
src/norman/operator/views      ABSENT
```

**~9 of the brain's last 12 rounds concern the Fit scoring layer or its measurement
inputs.** Meanwhile **51 of 95 companies are Prospects and there is no ranked "chase these"
surface.**

We have been applying maximum rigor to a component worth **6 of 100 points**, whose measured
re-ranking effect you yourself called *modest* (9 rise / 14 fall / 18 hold) — while the
layer that turns a board into a decision does not exist.

**That is a weight-class mismatch (brain/00).** And it is the same finding as the step-back
review, which recommended: validate the scorer → add product observability → **start
Priority.** The first two landed. **The third never started.**

---

## 3. AE4 is the casualty, and the brain is what kept deferring it

Round 24 found a real architectural defect: **reconcile cannot distinguish "JD edited the
board" from "a lane advanced the store,"** so it planned to adopt stale board values over
fresh measurements and revert real work. Its mitigation — synchronous projection — is a
**discipline, not a mechanism**, and **the outbox exists precisely to decouple producers, so
the first async lane re-opens it.**

**It has been deferred in rounds 25 through 31 — seven consecutive rounds — by me**, each
time behind a scoring refinement. Every message ended "AE4 — still before Phase B," and then
the next round ruled on something else. **A data-loss defect with a discipline-only
mitigation outranks every scoring item currently open.**

---

## 4. Process fix: stop using JD as the message bus

*"Rounds 29 and 30 never reached me."* Two rulings lost in transit — and you correctly
**refused to reconstruct AJ3 from its name** rather than guess. That was the right call and
it is why this was caught rather than silently mis-built.

The rulings are **already committed to NormansBrain**, and
`reviews/phase1-lane-design-decisions.md` **now opens with a topical index** (plus an
ID-collision note — `Q1`–`Q4` are used twice, qualify as `R2·Q1` / `R10·Q1` — and a
superseded table).

**Ruling: read rulings directly from that file. The messages become a convenience summary,
not the channel of record.** A process whose reliability depends on a human copying text
will drop messages — it just did, twice.

**AJ3, since you're missing it** — the Silna ruling. The exclusion rule stays absolute; what
changes is the confidence required of its *input*:

| trigger | action |
|---|---|
| **Declared / self-described** (the company describes itself as therapeutics) | fire immediately |
| **Inferred / third-party tag only** | **route to REVIEW** — the gate proposes, the human disposes |

> **Match a gate's strength to the confidence required of its input. A keyword match is a
> hypothesis, not a finding — and the more irreversible the action it triggers, the more
> verification it owes.**

---

## 5. The corrected order — this supersedes the one you're holding

1. **Finish coverage** (2 sessions, JD's go each). In flight and half-done; stopping now
   wastes it.
2. **AE4 — the last-projected baseline.** Before anything else. Seven deferrals is enough,
   and it is the only open data-loss defect.
3. **The product layer**, in this order: **`fit_raw` persisted** → **S6's three views** →
   **`contexts/priority`.** This is what 51 Prospects actually need.
4. **Park and batch the scoring refinements** into one later "scoring hygiene" round: the
   HQ→concentration swap and its compensation, the HQ weight question, shelf-vs-score
   `nyc_open_jobs`, the non-discriminating-component detector. All real, all small, **none
   urgent.**
5. Then Phase B.

**The rule to hold: depth of rigor stays; breadth of attention rebalances.** The rigor
caught the J1 inversion, an eval gate that could never fire, and a throttle that could not
stop anything. That standard is right. What was wrong was where it was pointed.
