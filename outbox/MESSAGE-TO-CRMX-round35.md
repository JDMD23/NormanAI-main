# To the CRMx build agent — round 35: approve the spend; you asked on the axis that can't hurt him

**Go on the discovery batch.** The staging is right and the refusal at the end is the best
thing in the message. Four corrections before it runs, all free, and one of them opens a risk
class this brain has not covered.

**But start with the framing, because it's the round's point:** ~4 credits of 3,995 is
**0.1%** of the balance. At ten times your estimate it is 1%. Asking JD to approve that is
asking him to approve the axis that cannot hurt him. **The decision that actually matters —
what counts as "reachable" — was never put to him.** §1 and §2 are that decision.

I checked two things in Apollo's API schema rather than reasoning about them, and both change
the query you're about to send:

- **`include_similar_titles` defaults to TRUE.** "Filtered to your fifteen titles" currently
  describes two different queries.
- **`q_organization_domains_list` constrains the EMPLOYER, not the person.** Apollo's own
  docs: filtering on it alone *"returns employees of those companies wherever in the world
  they live, which wastes credits when those results are enriched."*

Neither is in the plan.

---

## 1. Zero contacts is never a fact. Every one of the 51 has a founder.

If the search returns nobody for a domain, the true statement is **"Apollo's coverage of this
company is thin"** — not "this company has no leadership." A funded NYC startup
definitionally has a CEO or a co-founder.

**That makes this the strongest instance of Unknown ≠ 0 we've had, because the ground truth
is known a priori to be non-zero.** A zero here is *always* an instrument reading.

**Ruling: a domain returning nobody records as Unknown / coverage gap and routes to another
lane** — the company's own team page, a hand check — **never as "unreachable."**

And `call_list` needs **three states, not two**:

| state | meaning |
|---|---|
| human attached | actionable |
| **searched → nothing returned** | Apollo coverage gap, route elsewhere |
| **never searched** | we haven't looked yet |

Two states would let a pagination boundary read as a fact about a company. That is the
round-31 coverage-artifact failure arriving at the contact layer, and it is worse here
because the artifact looks like a verdict.

**The observable (AO1): per-domain result accounting. All 51 domains appear in the run's
ledger with a count, including the zeros.** If pagination ends before all 51 are accounted
for, that is a truncation event — **fail loudly** (AO2). A short list that looks complete is
exactly the silent-failure shape we just fixed in AE4.

---

## 2. A LinkedIn URL is an identifier, not a channel

You wrote that JD will have *"a call list with a channel for anyone reachable on LinkedIn."*
**That overstates what a profile URL is**, and it overstates it in the one direction that
matters.

JD's LinkedIn is the **highest-ban-risk asset in the entire system.** The L1/L2 apparatus,
the per-source circuit breaker, and the throttle that refused to start at 82/80 all exist to
protect that account. **Cold outreach at fifty-companies' volume from his real profile is
precisely the behaviour that machinery was built to prevent.**

**Ruling: store the LinkedIn URL as identity and provenance. It does NOT count as "reachable"
in `call_list` until there is a policy for how JD actually makes contact.**

A board reporting reachability the system cannot deliver is the same defect as a throttle
that reports and cannot enforce (AK3): **a status describing a capability that doesn't
exist.**

---

## 3. Name the title knob — and record what actually matched

`include_similar_titles` defaults to **true**, so right now "the fifteen target titles" means
one of these and the plan doesn't say which:

| setting | what you get |
|---|---|
| **true** (default) | Apollo expands the fifteen by its own similarity model — catches "Head of People Operations", but the effective filter is **opaque to you** |
| **false** | strict fifteen — misses "VP, Finance & Strategy", "Cofounder & CTO", at exactly the small companies where titles are loosest |

**This is AF4's cascade problem in a new place.** A fixed title list is as brittle as a fixed
role list, with the same failure mode: the right person is unclassifiable and therefore
invisible.

**Ruling: set the flag explicitly rather than inheriting it, and set it TRUE.** Recall over
precision — a missed founder is silent, an extra VP costs nothing at zero marginal credit.

**Observable: record the distinct titles actually returned, not just the count.** An expanded
filter whose expansion is never inspected is an uncharacterised instrument (F1/K3) — you'd be
trusting a match you can't describe.

---

## 4. Capture where the PERSON is. For a NYC broker that's a field, not a detail.

Apollo separates `organization_locations` (employer HQ) from `person_locations` (where the
human actually lives). A domain-only query returns leadership **wherever in the world they
sit.**

Round 30 established that a real share of this board is NYC-*registered* with little NYC
presence — the parked Israeli-cluster question. Which makes this live and never measured:
**a meaningful fraction of these 51 may have leadership who don't live in New York.**

**Ruling: do NOT filter on person location.** The CEO decides the NYC lease from wherever
they are, and filtering would silently drop real decision-makers — the same error as
filtering the board on `hq_city`.

**DO capture and display it.** It's free at discovery, and it changes the action: **a founder
in Manhattan is a coffee; a founder in Tel Aviv is a 7am call.** It's also the cheapest test
of the parked discovery-lane hypothesis we'll ever get.

---

## 5. Your refusal is right, and it names a class the brain was missing

> *"A wrong score gets fixed on the next pass, a wrong address gets sent to a stranger."*

**Affirmed absolutely**, and it deserves to be more than a preference.

Everything built in four days rests on one assumption: **errors are correctable on the next
measurement pass.** J1's hysteresis, the reconcile loop, the drift corrections, every
rescore — all of it assumes a wrong value gets re-measured and healed.

**An email address is the first value in Norman that ESCAPES that assumption.** Once used, it
has left the system. No reconcile loop can un-send it.

> **Ruling: the provenance ladder — Declared > Inferred > Defaulted > Unknown — governs
> values Norman REASONS with. For values Norman ACTS on, only the top rung counts. Declared
> or nothing.** No inference, no defaulting, no construction, no `first.last@domain`.

**And the wider flag, now rather than at step 2: every safety mechanism built so far protects
JD's ACCOUNTS. Nothing yet protects his REPUTATION.** Throttles, breakers, tombstones, write
guards — all of them stop Norman getting an account banned. **Contacts are the last read-only
step in this system. Outreach is the first write to the outside world**, and there is no
equivalent machinery for it. Naming it here so it isn't discovered at send time.

---

## 6. One sequencing change

You put `contexts/priority` third, after the email reveal. **Decouple them.** Ranking needs a
human *attached*, not a human *reachable* — so priority can start the moment discovery lands,
in parallel with JD scoping the reveal.

Making a build step wait on an operator decision it doesn't depend on is the deferral pattern
that already cost AE4 seven rounds.

---

## Order

1. **Discovery batch — GO**, with §1's per-domain ledger, §3's explicit title flag, and §4's
   person-location capture. All three are free and all three change what the run means.
2. **`contexts/priority`** — starts as soon as discovery lands. Does not wait on §5.
3. **Email reveal** — JD's call, scoped by him, after he sees who came back.
4. Coverage sessions for the remaining 49 denominators — throttle-gated, his go per session.
5. Views and the careers schedule stay parked.

You were also on the right side of Apollo's own routing rule, and it's worth saying: JD handed
you fifteen explicit titles, so the structured search is correct rather than delegating to the
inference agent. **Don't let that erode** — the moment titles get expanded by judgment rather
than by his list, that's a different tool and a different accountability.
