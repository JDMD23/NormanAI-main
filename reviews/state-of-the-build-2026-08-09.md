# State of the build — operational read, 2026-08-09

Not a design review. This asks: **what can Norman actually do, who does it, and what does it
cost a human?** Every number below was read from the repo, not recalled.

Sources: `JDMD23/NormanAI-CRMx` @ `c01076e` (73 commits), NormansBrain @ `f25efc3` (119
commits). Both synced today.

---

## The shape of the whole build, in four days

| day | commits | what it was |
|---|---|---|
| **Aug 6** | 53 | Built the entire spine in 12 hours |
| **Aug 7** | 9 | Audit and repair — security purge, 9 defects, J1 inversion, spec v3 |
| **Aug 8** | 5 | The careers/desk measurement instrument |
| **Aug 9** | 6 | Same instrument, plus reconcile's baseline |

**Day 1 built the machine. Days 2–4 have been calibrating one dial on it.**

That first day is genuinely remarkable — entity, identity resolver, SQLite store, Notion
projection, fit score, funding velocity, check ledger, cadence policy, status router, and a
live reconcile loop, all in a working day. It's the reason there's anything to critique.

**Codebase today:** 8,917 source lines, 4,627 test lines, 20 test files, 15 ADRs, 95
companies enriched and scored on a frozen ruler. A >0.5 test-to-source ratio at four days old
is unusual and it is not decoration — it caught real defects this week.

---

## Finding 1 — Norman knows 95 companies and **zero people**

This is the largest gap between what is built and what makes money.

```
store tables: aliases, changes, check_ledger, companies,
              funding_rounds, observe_events, projected, write_context
```

**There is no person table. No contact, no title, no outreach state, no last touch, no
reply, no meeting.**

Two fields exist — `workplace_contact`, `workplace_contact_email` — plumbed through the
entity, the store schema, reconcile's field map, and the projection. **No lane ever writes
them.** They are human-owned columns waiting for JD to type into.

And the sharpest version of it: the fifteen titles you named as your targets — CEO, founder,
COO, CFO, chief people officer, head of ops/finance/people, VP ops/people/finance, chief of
staff, head of workplace, head of real estate — appear in the codebase in exactly one place:

```
config/desk-roles.json          # "chief of staff", "Head of Workplace"
src/norman/contexts/careers/deskrole.py
```

They are there as **evidence that a desk is needed**. Never as **a person to call.** The
build learned your target vocabulary and used it to score companies instead of to reach them.

Your job is phone calls. Norman produces a ranked list of *logos*. Between that list and a
call there is still an entirely manual step — find the human, find the channel — that the
system does not touch at all.

---

## Finding 2 — Nothing runs by itself. Not one thing.

```
.github/workflows/     ABSENT
cron / scheduler       none
daemon / while True    none
```

The check ledger and cadence policy were built on **day 1, hour 2** — Prospect: careers 7d,
Crunchbase 14d, LinkedIn 30d. It computes what is due. **Nothing fires when it comes due.**
`work_queue.py` prints the queue to a terminal and exits.

So Norman is not an automation. It is a very well-engineered set of **hand tools** that move
only when you open a chat session and an agent types a command. Every measurement this week
was human-initiated.

And here is the checkable version of it, from the build's own source:

```python
# src/norman/contexts/careers/fetch.py
# "...which is why it is the first lane cleared to run unattended."
```

The careers lane hits Greenhouse, Lever, Ashby, and Comeet **public APIs**. No login, no ban
risk, explicitly cleared for unattended operation — **and there is no scheduler to run it.**
A lane that is authorized to run alone and has nothing to start it. That is "declared but
inert" (Y0) at the level of the whole system rather than a single rule.

The LinkedIn lane being attended is correct and deliberate (L2, account risk). The careers
lane being attended is an omission.

---

## Finding 3 — "Ranked trust" is the product, and the ranking layer has never been started

```
src/norman/contexts/  →  careers/  discovery/  fit/
src/norman/contexts/priority     ABSENT — 0 commits, ever
src/norman/contexts/warm_path    ABSENT — 0 commits, ever
```

Zero commits across 73, in four days. 51 companies sit in Prospect with no "chase these
today" surface. The three views were specified yesterday, and **you still have to build them
by hand in Notion** — so as of this minute, your operator surface is what it was on day 1: a
95-row board you sort yourself.

---

## Finding 4 — What the last two days actually were

Lines changed, Aug 8–9:

```
CAREERS / DESK measurement   6,692
FIT SCORING                  1,410
OPERATOR / PROJECTION        1,015
SAFETY / OBSERVE               150
```

Fourteen brain rounds in 48 hours; roughly eight of them on the measuring instrument.

It was not wasted. It produced: remote→0 as a true zero, the desk-role cascade with the
`Head of Workplace` / `Facilities Technician` trap pair, a validated ruler (39 of 41
reproduced exactly), and the discovery that **`hq_city` is a constant** — awarding NYC-native
credit to companies with 0% NYC presence, the exact inverse of its intent.

That last one is a real find. But look at what those two days did *not* touch: not one line
toward a contact, a call list, or an unattended run. **Two of four days went into sharpening
the input to a scoring component worth ~6 of 100 points, whose own measured re-ranking effect
the build agent called "modest."**

---

## Finding 5 — The human bus is the throughput limit, and nobody has engineered it

The operating pattern, stated plainly: **you are the message bus between two AI agents.**

Observed failures this week, all of them yours to absorb:
- **Rounds 29 and 30 never arrived.** Two rulings lost in a copy-paste.
- **The build agent's clone was 40 commits stale** — reading round 16 while we were at 33.
- **Your CRMx session was archived** and you lost the thread; it needed a reseed prompt.
- **Every measurement batch waits on "JD's go."**

System throughput is bounded by how many times a day you can move text between two windows.
Nothing in 73 commits addresses this. It is the most human-facing defect in the build and it
has the least engineering attention of anything on this page.

---

## What is genuinely strong — and it is not nothing

- **The safety posture is real and has fired on live occasions.** The throttle refused to
  start a session at 82/80. The write guard blocked writes to tombstoned pages. The identity
  bulkhead is mechanized. The committed-DB leak was purged and **independently verified from
  a fresh clone.**
- **The rigor finds things reasoning does not.** The J1 hysteresis inversion (caught by
  running it — a 62→41 two-band demotion on a *missing* measurement). An eval why-gate whose
  regexes could never match. A throttle that reported and could not stop. Two AE4 bugs found
  by running rather than reviewing.
- **The evidence discipline is unusually good** — instrument + granularity on every value,
  Unknown never collapsing to zero, provenance ladder, held-out validation.

The standard is right. **Where it has been pointed is what's wrong.**

---

## What I'd do next, in order

1. **Build the contact layer. Before priority, before anything.** For the top 20 prospects:
   a named human, their title, and one reachable channel — each with a source and a date,
   under the same provenance rules as every other value. A ranked list of companies is not a
   call list, and the gap between them is the only thing on this page that converts directly
   into revenue.
2. **Then `contexts/priority`** — ranked over companies *that now have a human attached*.
   Built in the other order it ranks things you still can't act on.
3. **Schedule the careers lane.** One cron, one lane, already cleared for unattended
   operation, zero account risk. Prove the cadence can fire without you before adding a
   second lane to it.
4. **Kill the human message bus.** Both agents read the ruling log from the repo — that
   ruling exists. It needs the other half: the build agent writing its reports *to* the repo
   instead of to you. Two dropped rounds is the evidence, not a hypothesis.
5. **Freeze the scoring layer for a week.** It is measured, validated, frozen, and its
   remaining open items are all real and all small. Park them together and don't reopen until
   something downstream demands it.

**The honest summary: the machine is well built, well tested, and well guarded — and it
currently ends one step short of a phone call.**
