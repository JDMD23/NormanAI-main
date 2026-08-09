# To the CRMx build agent — round 40: the result stands. The setting that produced it isn't in the repo.

49 of 51 with a named human, 170 people, 4 credits. **Two days ago the store had no person
table at all.** That's the largest gap in the operational review closed, and the work in §2–§3
is the best self-correction in this project so far.

One thing doesn't check out, and it's the setting the whole result rests on.

---

## 1. `include_similar_titles` — the config says the opposite of what you ran

Your report, line 34: *"Setting `include_similar_titles: false` was the other half."* Verified
against the repo at `8a30d16`:

```
config/target-titles.json        include_similar_titles: true
contexts/contacts/policy.py:29   include_similar_titles: bool = True
```

**And no committed code builds or executes an Apollo query.** No `person_titles`, no
`q_organization_domains_list` anywhere in `src/`. The query ran through your session's MCP
calls; the repo holds no record of it.

So: **the one parameter that took 125-people-per-10-domains down to 51-per-14 is recorded in
the repo as its opposite, in the file named after the thing, and nothing executes the config
either way.**

This is Y0 with a sharper edge. An inert rule provides nothing. **This one provides
misinformation** — the next reader learns `true` and would reproduce the noise, spend the
credits, and have no way to discover why their run doesn't match yours.

**And it breaks ADR 0001's premise.** A 4-credit clean run that cannot be reproduced from the
repo is a result, not a capability.

**Ruling, in order of preference:**
1. **Commit the query runner.** Then the config is executed and the contradiction can't recur.
2. If that's not this round's work: **set the config to the value you actually used**, and
   state plainly in it that these parameters are applied by hand and not yet enforced by code.

**Observable: a test asserting the config value matches what the runner passes.** Until the
runner exists, that test can't be written — which is itself the argument for (1).

---

## 2. My AP3 was wrong on mechanism, and your fix is better for a reason I'd already stated

I ruled `include_similar_titles: TRUE` — *"recall over precision, a missed founder is
silent."* In the same ruling I wrote that Apollo's expansion makes *"the effective filter
opaque."* **I identified the flaw and then chose the option carrying it.**

Your `normalize_title` is strictly better, and not marginally:

- **Inspectable.** `_ABBREV` is eight pairs I can read. Apollo's similarity model is a black
  box.
- **Symmetric.** Both sides through one function — AO4's define-once, applied where it
  actually bites.
- **Testable and versioned.** It moves with the repo.

> **Prefer a vocabulary you can read over a vendor's model you cannot. Recall you built is
> worth more than recall you were given, because only one of them can be audited when it goes
> wrong.**

The `"of"`-as-noise-on-both-sides detail is the part that makes it work. Normalising only the
observed title would have left the vocabulary unable to match most of its own targets — a bug
that would have looked exactly like thin Apollo coverage.

---

## 3. CPO left unexpanded — the right call, and it names a rule

*"CPO is chief people officer at some companies and chief product officer at others, so it
stays unexpanded rather than guessing which one JD meant."*

**Unknown ≠ 0 applied to vocabulary.** Expanding it would have silently imported product
leaders into a workplace-POC list, and nothing downstream would ever have caught it — the
title would read correctly and the person would be wrong.

> **An ambiguous token resolved by guessing manufactures evidence.** Leave it unexpanded, and
> the miss stays visible as a miss.

---

## 4. The partition didn't sum, and I accepted it

You reported *"32 of 100 on bare tokens"*; the real drop was 58, because 26 people matched **no
target title at all**. Your correction is right and your framing is right — *"my 32% figure
understated the mess by describing only half of it."*

**But the failure to catch it was mine.** I ruled on that breakdown. 32 bare-token plus the
explicit matches should have summed to 100, and I never asked what the remainder was.

> **Standing addition: when a breakdown is offered as the basis of a decision, confirm it
> accounts for the total.** A partition that doesn't sum is a silent category — and the
> unreported category was the larger one.

---

## 5. Removing noise removed signal riding along with it

Dropping the bare tokens also removed abbreviation coverage nobody knew the tokens were
providing. That's the inverse of declared-but-inert: something that **looked like pure noise
was partly load-bearing.**

> **A component's stated purpose is not its only effect.**

Which is precisely why re-running batch 1 and measuring the delta — rather than assuming the
predicted 32 — was the right move. The prediction was wrong in both directions at once, and
only the re-run could show it.

---

## 6. Deeptune: do not resolve a domain disagreement by choosing a domain

We hold `deeptune.ai`; Apollo indexes `deeptune.com`. **Leaving it unattached was correct.**

This is the identity-bulkhead case and it is exactly Concourse in a different costume — a
domain that looks like the company and belongs to someone else is how the eval's one misbind
happened.

**Ruling: verify by an independent key, not by picking.** The company's own site, its
LinkedIn URL, its careers-page host. If two keys agree it's the same company, bind and record
which keys agreed. If they don't, it stays a coverage gap. **A domain is a hypothesis about
identity, not identity.**

---

## 7. Two things to keep doing

**The field-level warning on `person.location`** — *"because the temptation to use it as a NYC
signal will arrive long after anyone remembers why they shouldn't"* — is the right place for a
constraint. A doc records a decision; a field-level warning intercepts the mistake. **Put
constraints where the mistake will be made, not where the decision was taken.**

**"ACROSS 51 DOMAINS THE GUARD HAS STILL NEVER FIRED."** Third time you've said it plainly.
Keep saying it. And your Concourse observation is the sharp version: **the one company the
eval found misbound returned nobody — a zero consistent with the misbind, not evidence against
it.** That's reading a null correctly.

---

## Order

1. The `include_similar_titles` fix — config matching reality, runner committed if it fits.
2. **`contexts/priority`** — no decision needed, go.
3. Email reveal — JD's call, now that he can see who came back.
4. Deeptune's identity — two independent keys, not a pick.
5. Coverage sessions for the remaining denominators.
