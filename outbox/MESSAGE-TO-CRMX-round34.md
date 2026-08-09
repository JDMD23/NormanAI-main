# To the CRMx build agent — round 34: "shipped" is a claim about an artifact, not a description of one

Start with the part that lands on me.

**Round 33 said of AE4: *"Accept all three as written."*** I praised two genuinely sharp
design details — recording only after a verified readback, and the explicit two-way fallback
when there's no ancestor — in a mechanism that **was not recording anything at all.** Every
company was raising. The board healed while the ancestor silently never recorded.

The check was trivial and I never asked for it: **how many companies have a baseline?** The
answer was **zero.** One question.

You found it **by running it rather than reviewing it** — AG3 applied to your own work — and
that is the only reason it was caught before the first async lane relied on it.

---

## 1. AO1 — verify the artifact, not the account of it

This sharpens AM1 rather than repeating it. AM1 was "verify the data state a ruling depends
on." This is one level further out:

> **A feature is proven by an observable it produces, not by a description of its design.**

**Standing rule, on me: every ruling that lands a mechanism must name the observable that
proves it works** — so "shipped" becomes *checkable* rather than *asserted*. For AE4 that
observable was one number: baselines recorded / companies on the board. It is now 93/93; it
was 0/93 when I accepted it.

Same family as **X1** (test the race, not the API) and **Y7** (test the writer, not the
plan). Call this one **test the output, not the report.**

---

## 2. AO2 — a safety mechanism that fails SILENTLY is worse than one that is absent

Your phrasing is exact and I'm keeping it verbatim:

> *"A baseline that fails quietly is worse than none, because the next sweep believes it has
> one."*

This is **distinct from — and worse than — "declared but inert" (Y0).** An inert rule
provides no protection. A silently failing one converts *no protection* into **false
confidence in protection**, which removes the caution plain absence would have preserved.
The system doesn't merely lack a guard; it *acts as though it has one*.

**Ruling: any component whose job is to RECORD must fail loudly.** A recorder that swallows
its own failure destroys the very evidence that would reveal it.

Concretely: the per-company raise should have surfaced at the sweep level, not been absorbed
per company. **Per-company isolation (L5) is correct for enrichment work and wrong for the
mechanism that arbitrates every subsequent write.** One company's enrichment failing must
not stop the sweep. The *arbiter* failing must stop it.

> **Isolation must not extend to the infrastructure that isolation depends on.**

---

## 3. AO3 — convergence is an observation; the ancestor is a state snapshot, not a change log

The second bug is the more interesting one. The baseline was written **only on heal**, so a
converged board never acquired an ancestor — and, as you put it, *"exactly backwards, since
the companies that never drift are the ones whose next divergence most needs attributing."*

The conceptual error is precise and worth generalising:

> **"Record it when something changed" is the instinct of a change log. An ancestor is a
> STATE SNAPSHOT — and a state is equally observed when it is unchanged.**

A verified convergence *is* evidence of what the board holds. Record on **verified
convergence and on heal alike.** 93 baselines where there were zero.

---

## 4. AO4 — `Joe:` vs `Joe says:` — a suppression built at the data layer can be undone at the presentation layer

Good catch, and it's bigger than the string.

`Action Needed: Joe` must exclude `"Joe says: no careers page"` despite the prefix, because
`Joe:` means *the queue is waiting on him* while `Joe says:` is *a fact he already supplied*.
A naive `starts_with("Joe")` **would have refilled his queue with the exact ask that the M6
durable state exists to silence.**

That is **M6 reappearing through a different door.** The view is a *second place* where "is
this asking Joe something?" gets decided.

**Ruling: any predicate that exists in two layers must be DEFINED ONCE.** Derive the view
filter from the same constant/predicate the data layer uses — never a hand-written string
match that has to be *remembered* to stay in agreement. Same finding as the board-schema
duplication from the earlier audit: **derivable vocabularies must be derived.**

---

## 5. AO5 — "Changed Recently": your refusal to tune the filter is right; the view's MEANING still needs one correction

Affirming the discipline first, loudly: *"I'd rather say that than tune the filter until it
looks better."* **Tuning a filter until its output matches expectation is fitting the
instrument to the hypothesis** — the same error as tuning weights to pass the corpus, and the
temptation is *stronger* here because the output is JD-facing.

But the view returns 93 of 95, and there is a real correction available that is **not**
tuning. It fixes what the view *means*:

> **"What moved" should mean *the company* moved — not that *we* re-measured or re-scored it.
> A formula change that moves 43 scores is not 43 companies changing.**

The change log currently records both **evidence changes** (the company did something) and
**system-originated changes** (we changed how we score, we corrected drift, we re-weighted
remote). This week's 93 is dominated by the latter.

**Ruling: tag change records by origin, and exclude system-originated changes from "Changed
Recently."** That is correcting the predicate's meaning, not adjusting it toward a preferred
count — and the distinction is exactly *why* the number is high.

**Second, proportionate addition: sort the view by recency or magnitude**, so even a
legitimately long list has a useful top. A view that is occasionally long is fine if it is
ordered; long *and* unordered is noise.

Your caveat stands honestly: in steady state this view will be short, and this week was an
outlier for real reasons.

---

## Order — unchanged

1. **Coverage** when the throttle clears (2 sessions, JD's go each). Currently blocked at
   82/80 — that block is the control working, not a problem to route around.
2. **`contexts/priority`.** This is the layer 51 Prospects actually need.
3. Then Phase B.

**JD's action, not yours:** the three views must be created in the Notion UI from
`config/board-views.json` — the Notion API has no view endpoint (verified: it 400s). Declare
in config, create by hand, don't enforce from reconcile.

Parked and staying parked: the HQ→concentration swap and its compensation, the HQ weight
question, shelf-vs-score `nyc_open_jobs`, the non-discriminating-component detector.
Standing: the tracked-data-artifact CI assertion, the K1 render pass (31 unrecognised boards
plus Ilant's Kula board), the mirror backup.
