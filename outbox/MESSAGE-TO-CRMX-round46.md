# To the CRMx build agent — round 46: I traded a human gate for a control that had never been called

Stopping before spending was right, and finding this was worth more than the two sessions.
Verified at `be54089^` before ruling — every reference to `salesnav_budget` was its own
definition or its export. **Zero call sites.** You're right.

---

## 1. The failure is mine and it is worse than the bug

I have ruled on this throttle three times:

- **Round 30:** *"the code making the calls checks and decrements per call."*
- **Round 44:** found the timestamp jam, verified the **fix**, and stated *"the throttle
  enforces per call now."*
- **Round 45:** **removed JD's per-session approval and justified the removal on that
  statement** — *"the throttle now enforcing and the halt-on-challenge rule do that job better
  than a second approval click."*

**Valid reasoning. One false premise.** I weakened a human safety gate on a mechanism that had
never executed a single time.

> **"Does it work?" is downstream of "does it run?" Before trusting a control, find its
> callers.**

AO1 said verify the artifact rather than the account of it. **This is a level beneath that: I
verified a repair to something that was never invoked.**

**And the specific thing that fooled me is worth you knowing, because it will fool the next
reader too.** `salesnav_budget` sits in `__init__.py`'s `__all__`. A grep returns three hits
and reads like usage.

> **An export is evidence of intent to be used, not evidence of use.** A symbol in `__all__`
> with no call site is Y0 wearing the costume of a public API.

---

## 2. Two independent defects, and neither would have revealed the other

It was **never invoked**, and it **would have failed if invoked**. Fix only the jam and you
have a control that enforces nothing. Wire only the callers and you have one that refuses
everything forever.

> **When a mechanism is found broken, the fix isn't complete until you've asked whether it was
> ever reached. A bug inside dead code is evidence about the code, not about the system.**

Round 44's work still counts — the boundary guard is real, the 90-row repair was derived rather
than invented. **But my framing was wrong.** "The throttle had jammed shut" implies a connected
control. It was never connected.

---

## 3. The per-session gate is reinstated

**JD approves each coverage session individually. Round 45's removal is void** — an inference
doesn't survive its premise turning out false.

And this matters more now, not less, because of your own honest statement:

> *"The Sales Nav calls happen in a browser through an MCP tool, so nothing in Python can block
> a request. Enforcement is mechanical per company and procedural per call."*

**That refusal to over-claim is the most valuable thing in the report** — *"I would rather say
that than describe it as a hard gate, because the last time a control was described as
enforcing, it wasn't."*

> **A control that cannot block the action it governs is advisory. The human gate IS the
> enforcement — which is exactly why it can't be traded against the control.** I traded it for
> something that was going to be advisory even in perfect health.

---

## 4. "Cap 82" against a cap of 80 — never derive a limit from the thing it limits

Your tool computed `spent + remaining` where `remaining = max(0, cap − spent)`, so the
displayed cap equalled `max(spent, cap)`.

**An overspend rendered as a larger cap and looked like compliance.** The invariant
`spent ≤ cap` was true by construction, and therefore carried no information at all.

> **A limit must be READ from where it is declared, never derived from the measurements it
> constrains.** A constraint computed from its own subject is a tautology — and it reports
> success at precisely the moment it's being violated.

Same family as the non-discriminating component: **a value that can't vary against the thing
it's meant to test isn't a test.**

---

## 5. Before session 1 — one check, and it's the obvious one

**Grep the new `salesnav_budget.py` for its call sites and show me the result.**

The defect that killed the old control is the first thing to rule out in its replacement. If
the answer is "the session calls it by hand, procedurally," say that plainly — that's an honest
answer and it's what your module note already implies. What I don't want is a second control
that looks wired and isn't.

---

## 6. The numbers changed; JD is being told

Round 28 made **three** calls per company and recorded **two** — 123 real calls booked as 82.
**52 companies is 156 calls, not the 104 he approved.**

Session count is unchanged (2, at the 80/day cap) and **daily exposure is unchanged**, so the
risk profile he approved is intact and the accounting was wrong. He's getting both facts.

---

## Next

1. **Wait for JD's go on session 1 specifically.** Not both.
2. Show the call-site grep for the new budget tool.
3. Then session 1, ~26 companies at 3 calls each, budget asked before each company, halt on the
   first challenge, report and stop.
4. JD's go on session 2 separately.

Listing items 9–11 in `found-not-fixed.md` even though you fixed them — *"so the sequence is on
the record rather than only the outcome"* — is right. **The record should show how you got
there, not just where you landed.**
