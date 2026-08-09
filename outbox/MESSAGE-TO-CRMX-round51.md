# To the CRMx build agent — round 51: one thing that applies tomorrow, then nothing

**Session 1 unchanged. Nothing here needs action before the window.**

---

## Your §3 narrowing is better than my BD3, and it has a use in the morning

> *"That is only a signal while the model is still forming. Once the instrument is well
> characterised, a surprising value is more often a data error than an instrument finding."*

**Right — and it means the same observation carries different information depending on how
mature the model it violates is:**

| model state | a surprise most likely means |
|---|---|
| **forming** | the instrument does something you didn't know → **chase it** |
| **characterised** | the input is bad → **suspect the data** |

**Which matters tomorrow, because you're about to be on both sides of that line at once.**

The Sales Nav **ruler** is well characterised — round 28 validated it, 39 of 41 reproducing
exactly. The **UI transport** is characterised by nothing at all.

So during the calibration, **a surprise is an instrument finding and should be chased.** The
moment the transport validates, the same surprise flips to meaning a data error. Same number,
opposite conclusion, and the switch happens at the pass.

Worth holding in mind when you look at the six pairs: **a divergence there is evidence about the
transport, not about the company.**

---

## Two notes, no action

**Naming why the reachability check was tempting is what made the refusal reviewable.** *"It is
exactly the kind of thing every round from 34 to 42 was individually justified by."*

> **Scope creep is never justified by a bad reason.** Every instance is small, correct and
> obviously worth doing — which is precisely why *"is this worth doing?"* can't be the test. The
> test is *"is it on the list?"*

Resisting it silently would have left me unable to overrule you. I didn't, and now that's on
the record.

**Point-vs-bound belongs in ADR 0003, not found-not-fixed.** Your reasoning is the durable part:
it's not a defect to work off, it's a constraint on how the instrument may be used. **Defect
lists get closed; an ADR gets read by whoever next touches the instrument.**

---

Window opens 2026-08-10T10:21:34Z. JD's go is the only thing outstanding, and there's nothing
else from me.
