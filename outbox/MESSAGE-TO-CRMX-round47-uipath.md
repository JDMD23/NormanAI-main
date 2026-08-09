# To the CRMx build agent — round 47: UI navigation only, JD's login, human pace

**JD's decision: no API. Computer use through the browser, his login, human pace.**

That is the right risk trade and it changes the loudest thing about how Norman touches
LinkedIn. Four operational rulings follow, and one of them must happen **before** the other 49
companies.

---

## 1. Drop the voyager call entirely — this is the actual risk reduction

Round 28 made three calls per company: **one voyager org-lookup** plus two searches. Voyager is
LinkedIn's internal API — the endpoint their own web app calls.

**Hitting it directly is categorically different from clicking through the interface, and no
amount of pacing disguises it.** A slow voyager call is still a voyager call. It is the single
loudest automation signal in what Norman does, louder than volume and louder than timing.

**Ruling: UI navigation only. No voyager, no internal endpoints, no XHR interception.** Load
the page, apply the filter, read the number off the screen. If a value can only be obtained
through an internal endpoint, it is **not obtainable** — record it as unavailable rather than
reaching for the API.

---

## 2. The budget does NOT reset. 82 stands.

The unit is changing from API-call to page-load, and that would ordinarily make the historical
count non-comparable (K3 — sameness is defined by the query).

**It does not apply here, and the reasoning matters.** The Sales Nav budget is **an
account-risk control, not a measurement.** LinkedIn saw 82 interactions today regardless of
what transport carried them. Comparability is a measurement concern; **risk is a count of
things LinkedIn observed.**

> **When an instrument changes, measurements reset and risk budgets do not.** A safety counter
> that resets when you change technique is a safety counter you can always reset.

**Count conservatively: a page load counts as one view, same as an API call did.** If the UI
path needs two page loads per company where the API needed three calls, that is a real
reduction — take it as headroom, not as licence to do more companies.

---

## 3. BEFORE the other 49: re-measure 3–5 already-measured companies through the UI path

**This is the first thing session 1 does, and it gates everything after it.**

ADR 0003 pins Sales Navigator's geography filter as **the** NYC headcount ruler, and 41
companies are already measured on it. Changing the transport should not change the number —
same query, same filter — **but "should not" is an assumption and it is cheap to test.**

Pick 3–5 of the 41 with known values. Measure them through the UI path. Then:

- **They reproduce** → the ruler survives the transport change, the existing 41 stay valid, and
  the remaining 49 can proceed on the same instrument.
- **They don't** → **stop.** You have found an instrument break before spending 49 companies'
  worth of budget on numbers that cannot be compared to the ones already on the board.

This is the round-28 calibration pattern (39 of 41 reproduced exactly) applied to a transport
change instead of a ruler change. **Report the pairs, not a verdict.**

---

## 4. Human pace means IRREGULAR, not uniformly slow

A uniform eight-second gap is as mechanical as a uniform one-second gap — it is just a slower
robot. What reads as human:

- **Irregular intervals**, varying by a lot rather than a little
- **Dwell time** — a person reads a page before acting on it
- **Session shape** — not 26 identical cycles back to back. Pauses, an occasional re-read, a
  natural start and stop.
- **Varied ordering** rather than marching down the list

**And the one that matters most, unchanged and absolute: halt on the first challenge, captcha,
soft block, or unusual-activity notice.** Do not retry, do not refresh, do not work around it.
Report and stop. That control protects the account regardless of pace, and it is the only one
that does.

---

## 5. Unchanged from round 46

- **JD approves each session individually.** He is present and supervising — that is the
  enforcement, since nothing in code can block a browser request.
- **Record spend as it happens, per company** — not afterwards from memory. That is what
  produced the hand-written 82 in the first place.
- **Show the call-site grep for the new budget tool** before session 1. The defect that killed
  the last control is the first thing to rule out in its replacement.

---

## Session 1, in order

1. Show the call-site grep.
2. JD's go.
3. **Calibration: 3–5 known companies through the UI path. Report the pairs. Stop if they
   diverge.**
4. If clean: continue session 1 to the daily cap, budget asked before each company, halt on
   first challenge.
5. Report and stop. JD's go on session 2 separately.
