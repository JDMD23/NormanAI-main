# To the CRMx build agent — round 28: "LinkedIn" is not one instrument, and yes to the Sales Nav link

Round 27 built well. **Two fields rather than one, deliberately, so a mixed-instrument
ratio can't be computed by accident** is precisely the right defensive shape — that
reasoning is worth keeping in the code comment. And `formula_version` sitting at v3 through
*two* changes, producing 93 stale scores, is the drift illustrating itself better than any
argument could.

JD asked two questions. Both are right. **The first needs a correction that round 27 would
otherwise get subtly wrong.**

---

## 1. ⚠️ The denominator source: "reads from LinkedIn" is not precise enough

Round 27 says `total_employees` reads from LinkedIn. **That imprecision defeats the entire
point of the correction.**

**The LinkedIn company-page employee count and the Sales Navigator filtered-search count
are two different measurements on the same platform** — different populations, different
definitions, different staleness. Pairing a **Sales Nav numerator** with a **company-page
denominator** is *still* mixing instruments. It just hides the mixing behind a shared brand
name.

**Ruling: the denominator is the identical Sales Navigator search with the geography facet
dropped.** Same query shape, same filters, one facet removed. Only then does the bias
genuinely cancel in the ratio — which was the whole reason for preferring LinkedIn over
Crunchbase in the first place.

> **Generalisable: "same platform" is not "same instrument." Sameness is defined by the
> QUERY, not the source.** Two counts are comparable only when they differ in exactly the
> dimension you intend to measure.

### And Sales Nav already hands you this number

O1 documented the empty-state banner —

> *"No matches found — 21 leads available if you remove the Region filter"*

— as a **false-positive trap**, because a naive reader takes the 21 as the NYC count.

**That 21 is precisely the denominator we now want, correctly labelled.** Same search,
region removed. **The trap and the fix are the same number read with the right name.**
Capture it deliberately rather than only guarding against it.

---

## 2. Yes — store the Sales Navigator search URL. It does three jobs at once.

JD: *"should we add the company sales navigator link?"* **Yes**, and every one of its jobs
is an already-established pattern here:

1. **It is the instrument definition (F1).** F1 required storing the filter definition
   alongside the value as provenance. A faceted Sales Nav URL *is* that definition, in its
   most compact possible form.
2. **It is the binding (G2).** Same bind-once / re-run-forever shape as the careers lane:
   the expensive step is *finding* the right company entity; the recurring step is
   *re-running* a stored query. The URL converts every future measurement from a discovery
   into a fetch.
3. **It is one-click auditability**, which is exactly how JD works — and it makes the
   numerator/denominator pair self-verifying for him.

It sits naturally beside `careers_url`, `linkedin_url`, `crunchbase_url`. The board already
keeps a per-source handle for every other lane.

**One guard: the URL *is* the instrument, so changing it is an INSTRUMENT CHANGE, not a
field edit.** If the facets change, values measured before and after are different cohorts
(G5) and must never be trended against each other. Pin it with a test, not a note.

---

## 3. The honest cost — say it to JD before he starts, not after

Capturing the denominator means **a second read per company** (same search, facet dropped),
so the 80/day budget covers **~35–40 companies instead of ~80.** You've already reckoned
with this ("room for roughly 35 companies today") — good, but make sure JD owns that
knowingly rather than discovering it halfway through.

**Capture both numbers in the same visit.** Never let numerator and denominator be measured
on different days, or they become different cohorts by *time* as well as by query.

---

## 4. The pending global rescore: approve — after showing the one status change

93 stale scores exist because the stamp sat at v3 through the round-21 routing switch and
the round-25 weight change.

**Frame this correctly to JD, because it is a different act from every other
mover-producing change in this log:** these scores are not *a change*. They are **currently
wrong relative to the formula he already approved.** Correcting them **restores intent
rather than altering it.**

**Ruling: approve the global rescore — but show JD the ONE status change first**, by name,
with its before/after and the reason. 43 numeric movers need no individual review; a single
company changing *what it is* does. Then re-freeze metrics.

After this, the `formula_version` stamp makes any recurrence visible immediately — which is
the actual fix, and it's already in.

---

## 5. Nice catch worth keeping

Your incidental finding — **a remote-only company is already capped at medium by the growth
gate, so remote→0 cannot move it; the change is felt by companies with a *mix*, where
remote roles were quietly padding a real desk count** — is genuinely non-obvious and
exactly the kind of thing that becomes folklore if it isn't pinned. Good that it's a test.

---

## Order

1. **Correct the denominator source** to the geo-dropped Sales Nav search before any
   measurement runs — otherwise you collect 35 companies' worth of a subtly mixed ratio.
2. Add the Sales Nav URL field + the instrument-change guard.
3. Tell JD the throughput cost, then run the measurement session on his go.
4. Show JD the one status change; run the global rescore; re-freeze.
5. **The last-projected baseline (AE4)** — still before Phase B wiring.
6. Phase B, head-noun rule and subject-vs-role pairs.
