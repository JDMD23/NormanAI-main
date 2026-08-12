# To the CRMx build agent — round 60: careers logical order (URL → fetch → discovery)

JD asked COS (2026-08-12) to build the brain for the logical visit order after a momentum test
showed the due list was homework without textbooks.

## Observed tonight (Mac main @a833263)

- `ops due_work` / `dry_run --lane careers`: **67 due, all Research, careers_url missing**.
- **~98 companies already have careers_url** and were **not** in that due set.
- Ops `apply --gate careers_apply_day` only forwards `--limit` into the due filter — **cannot
  target with-URL boards**.
- Direct lane proof works: `careers_lane --all --limit 5` (dry) talked to Ashby on 3/5;
  Amperos would move NYC open jobs 15→16. JD **held apply**.

## Ruling — three phases, never tangled

1. **URL harvest / resolve** (or mark none)
   - Sources: JD paste on Careers Page, `careers_probe`, lane phase-1 `discover_board`.
   - Outcome per company: bound URL · unbound/needs-render · **Joe: paste** · **Joe: no page**.
2. **Fetch on cadence** (only boards with a usable careers_url)
   - Public ATS only. Writes job counts, workplace split, story fields.
   - Cadence by status stays as `config/cadence.json`.
3. **Discovery queue** (URL-less / unrecognized)
   - Separate from fetch due. Never starve the with-URL cooker to chase Research blanks first.

> **A company without a careers_url is not "due for careers fetch." It is due for discovery
> (or a human paste). Fetch due = with-URL + cadence overdue.**

## Implement targets (CRMx)

- Split ledger / due semantics: `due:careers_fetch` vs `due:careers_discovery` (names flexible;
  meaning is not).
- `ops dry_run` / `apply` for `careers_apply_day` must be able to run the **fetch** cohort
  (with-URL), not only URL-less Research never-checked.
- Keep LaunchAgent on fetch path once proven; discovery may stay lower cadence / probe batch.
- Do **not** wire `desk_check` / role-type seat classifier into score in this round (still
  validation-gated). Workplace onsite|hybrid|remote stays live.

## Seat brain (status, not a change request this round)

- **Live:** workplace mix → Desk Jobs (`in_office + 0.8×hybrid + 0×remote`).
- **Parked:** role-type "needs a commercial desk?" (`deskrole` / `desk_check`) — confirm labels
  with JD before scoring.

## Needs JD

- First supervised **fetch** apply on a with-URL limit after this lands (gate `careers_apply_day`).
- When to validate desk-role labels (separate gate).

## Facts vs assumptions

- **Facts:** due set URL-less; with-URL lane dry-run works; ops cannot pass `--all`.
- **Assumption:** splitting fetch vs discovery due is preferred over only teaching ops `--all`.