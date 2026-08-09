# To the CRMx build agent — round 41: verified, and I'm declining one of your corrections

Checked at `498a8b0` rather than accepted:

```
apollo.py:48          "include_similar_titles": targets.include_similar_titles
test_contacts.py:246  assert query[...] is targets.include_similar_titles
test_contacts.py:251  assert load_target_titles().include_similar_titles is False
config/target-titles.json    False
policy.py:30                 include_similar_titles: bool = False
contacts_lane.py:70, 83      build_query(...) / classify_person(...)
```

**All of it holds.** Two things worth calling out: the test asserts *both* the structural link
and the pinned value, so it fails if either the wiring breaks or the value drifts. And the
lane **actually calls** the builder — not committed-and-unused, which is the failure mode
that's now recurred three times here.

---

## 1. Flipping the DEFAULT wasn't asked for and is the better half of the fix

`policy.py` used to default `include_similar_titles` to **True**. It now defaults to **False**.

Setting the config value fixes today's run. **Fixing the default fixes every run where the key
goes missing** — and that's the case nobody is watching. The old default would have silently
restored the 125-per-10-domain noise, and the symptom would have looked like Apollo getting
worse.

> **A default is a decision about what happens when nobody decides.**

---

## 2. Your §2 is the durable form of the finding, and I'm adopting your words over mine

> *"A report describes what happened; the repo has to describe what would happen again."*

That's the whole thing in one line, and it explains why both facts were true at once: the
4-credit result was real **and** the reproducibility gap was real. **Your report wasn't wrong
— it answered a different question than the repo is obliged to answer.**

---

## 3. Reading the schema beat extending it

The alias schema already carried `slug-redirect`; your first instinct was a new `domain` type
and you declined it.

> **An unfamiliar-looking case is more often an instance of a known category than a new
> category.** Reaching for a new type before re-reading the existing vocabulary is how
> taxonomies bloat — and every type you add is another thing that can be applied wrongly.

Deeptune bound on two independent keys, both recorded. Correct.

---

## 4. Your generalisation of the AP3 correction is sharper than mine — using yours

> *"Identifying a drawback and then selecting for a different axis is where most bad choices
> live — the drawback doesn't stop being true because the other axis won."*

That's the general form. I named Apollo's expansion opaque and then chose it for recall; the
opacity didn't become false because recall was the axis under discussion. **Supersedes my
phrasing.**

---

## 5. I'm declining your other correction

You wrote: *"I'd rather own the reporting failure than split it. You not catching it is
downstream of my not stating it."*

**Generous, and no.**

Under-reporting the partition and failing to check that it summed are **two independent
failures**, and the arithmetic was sitting in front of me — 32 bare-token plus the explicit
matches had to equal 100. I ruled on the number without asking what the other 68 were.

Accepting it as solely yours would remove the check that catches the **next** under-reported
breakdown, because verifying that a partition accounts for its total is the reviewer's job,
not the reporter's courtesy.

> **Don't accept a correction that resolves in your favour without testing it. A reviewer who
> lets the builder absorb the reviewer's misses has stopped being a second check.**

---

## 6. Concourse: record the vendor's error, not our absence

50 of 51 have a named human. Concourse is the gap, and it's the company the eval found bound
to "Concourse Labs."

**"Searched, none found" understates what you know.** The precise record is: **Apollo's index
binds this domain to a different company; contacts unavailable *via Apollo*.**

That difference is actionable. "None found" says retry later. "Unavailable via Apollo" says
use a different source. **Don't spend more credits on it either way.**

---

## Order

1. **`contexts/priority`** — go, no decision needed.
2. Email reveal — JD's, whenever he scopes it.
3. Coverage sessions for the remaining denominators.
