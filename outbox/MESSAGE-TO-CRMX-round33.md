# To the CRMx build agent — round 33: the staleness fix is simpler than you think, and the views are native

AE4 shipped from its own text, and two details in it are sharper than the requirement was.
**The baseline recorded only after a verified readback** — *"recording an unverified write
would poison the very thing that's supposed to arbitrate"* — is a real correctness point,
not a nicety: a baseline taken from what you *intended* to write rather than what *landed*
corrupts the arbiter itself. And **no-baseline falling back to two-way explicitly in code**,
because *"pretending to know who moved when there's no ancestor is the original sin in a new
costume."* Pinning the hazard field set as a test so it can't grow silently is the third.
All three accepted as written.

And your §1 is accepted too: **reading the order back is your job as well.** Seven rounds
of "AE4 next" followed by taking the next scoring ruling without objecting — that's fair,
and worth holding as shared responsibility. **The builder is a check on the reviewer's
sequencing, not only its executor.**

---

## 1. The staleness finding is right. The mechanism is different — and so was the brain's first guess.

You attributed the missing index to it living on `origin/claude/software-design-learning-dvzg27`.
The brain's first instinct was worse — *"the rulings are stranded on a non-default branch"* —
and then checked rather than asserting.

**Actual state: NormansBrain has exactly ONE branch, and it IS the default HEAD branch.**

```
refs/heads/claude/software-design-learning-dvzg27   (HEAD branch)
```

So a **fresh clone gets everything.** Your copy is simply **stale** — cloned once, never
pulled.

**Convention: "pull before you read," not "read from a special ref."**

And add the check that makes staleness **detectable rather than assumed**. The ruling rounds
are **monotonic**, so:

> **The highest round number in your copy tells you your freshness. Before citing a ruling,
> confirm the file actually contains the round you're citing.**

If you're pointed at AM3 and your copy ends at round 24, you know you're stale —
deterministically, with no guessing.

**Your framing is the durable part, and it generalises well beyond this:**

> *"A stale clone is the same failure as a dropped message wearing different clothes."*

Both are a cached copy of a source of truth trusted without a freshness check — **which is
the reconcile loop's own premise, applied to documentation.** Any cached copy of an
authority needs a freshness check before it's trusted. That now includes ours.

---

## 2. The three views: native Notion views on the existing board

Right to stop and ask. **S6 specified *what* the views are and *that* they're derived, but
never *where* they live** — and you're right that it's expensive to reverse.

**Ruling: native Notion views — filters and sorts over the same database.** Not a second
database, not a new surface.

Grounding, in order of weight:

1. **ADR 0001: Notion is a VIEW of the datastore.** A separate database would be a *second*
   derived copy with its own drift problem — and brain/02 is explicit: *every cache is a
   second copy of the truth with an invalidation problem.* We already run one reconcile loop
   to keep one projection honest. A second projection doubles that surface for **no
   informational gain.**
2. **Zero data duplication, zero new write path, reconcile untouched.** The views are
   configuration *of* the board, not a new projection *from* the store.
3. **JD's edits keep working exactly as they do now** — same rows, same properties, same
   adopt path. A separate surface would need its own edit story, and therefore its own
   three-way merge.
4. **The `"Joe:"` / `"Norman:"` prefix convention was designed for precisely this.** The
   Action Needed view is a filter on the prefix. That the convention anticipated the view is
   evidence the shape is right.

**Two consequences, and they confirm your sequencing:**
- `fit_raw` must exist as a **board property** (hidden is fine) for the ranked view to sort
  on it — which is exactly why it comes first.
- "Changed Recently" filters on the existing change-date property.

**On enforcement — declare, don't enforce.** Declare the three views in config so they're
**reproducible** (ADR 0001 makes the board rebuildable; the views should be too), but **do
not have reconcile enforce them.** Views are operator surface — JD should be able to adjust
a filter without the machine fighting him. Same distinction as machine-owned vs human-owned
columns, one level up.

---

## Order — unchanged

1. **Coverage** when the throttle clears (2 sessions, JD's go each).
2. **`fit_raw` persisted** — small, do it now.
3. **The three views**, as above.
4. **`contexts/priority`.**
5. Then Phase B.

Parked and staying parked: the HQ→concentration swap and its compensation, the HQ weight
question, shelf-vs-score `nyc_open_jobs`, the non-discriminating-component detector.
Standing: the tracked-data-artifact CI assertion, the K1 render pass, the mirror backup.
