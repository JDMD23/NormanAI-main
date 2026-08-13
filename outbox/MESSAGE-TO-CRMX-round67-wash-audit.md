# NORMAN — FINAL DOOR + WASH AUDIT RULINGS (round 67, locked)

One-company car wash. No fleet redesign. Rulings first, methods second, code checklists at the end.

---

## A / B / C

**A — KEEP, with one word changed: run P1 and P3 anyway.** A LOOKED-NONE on careers is a
*terminal result for one lane*, not a freeze on the company — evidence is written as it lands,
the score waits at the barrier, so freezing the wash would waste the two free lanes to protect a
gate the barrier already enforces. **Rule: lanes never wait on each other; only the SCORE waits
on all of them.**

**B — May be honestly "none" and still score: investors, funding history/velocity, founded, the
funding record itself.** Each earns 0 of its own small weight and touches nothing else. **Must be
real values or no score: NYC Employees, NYC jobs (from a live door), HQ, industry, funding stage.**
The first two are 60 of 100 points; HQ flips the meaning of "small" (stall vs new satellite);
industry is the qualification gate; stage is the lens everything is read through. **Rule: context
may be empty, primaries and lenses may not.**

**C — CONFIRMED, with one cap.** No door = LOOKED-NONE = flag JD, no score. Door exists + a
measured 0 = write 0 = score. **The cap: an ATS-API 0 is a real 0; a DOM-read 0 is written but
marked Partial until a second, different signal corroborates it** — a page reader confirmed its
own bug once already (Brandlight, 3 real roles read as 0, 26 points suppressed). **Rule: zero
from an API is a fact, zero from a rendered page is a claim.**

---

## 1–18

**1 · Name-only (X).** Use the X profile's own website link as the anchor first — most profiles
have one, and it is the company asserting its own identity. No link: search
`"{name}" {two words from the X bio describing what they do}` and open only results ON a
first-party domain. **Refuse:** Crunchbase/LinkedIn/Pitchbook as "the website," news, investor
portfolio pages, app-store pages, parked or for-sale domains. **Lock only when the site's own
copy describes the same product the X bio claims.** Stop: page 1 all directories → LOOKED-NONE
on website. **Miss caught:** a parked exact-match domain that would have become the identity key.

**2 · Identity minimum.** The key is the **registrable domain** (eTLD+1, lowercase,
post-redirect), stored with aliases for every redirect hop. Signals: LinkedIn About "Website"
→ same domain · Crunchbase "Website" → same domain · careers board links back to the domain.
**Two of three match, none contradicts = bound.** Two match and one doesn't: the odd one out is
*unbound* (that URL is dropped and re-hunted), the company survives on the two that agree —
unless the odd one is the website itself, then everything above it is suspect → LOOKED-NONE.
**Miss caught:** a CB org whose website field points at a same-name company in another country.

**3 · Twins with no founder on the card.** Never bind on name + city + industry — that triple is
exactly what twins share. You need a **domain chain from the intake evidence to the candidate**
(X bio link → domain; CB website field → domain). Two candidates that both fit the story and
neither chains to the intake evidence = **LOOKED-NONE required, picking forbidden** — a scored
stranger is worse than an unscored company. **Miss caught:** two NYC "Thrive"s, both venture-backed,
different products.

**4 · CSV with website + LI + CB.** Trust nothing, verify cheaply — three field reads, no
judgment: fetch the website (follow redirects, record the canonical domain), read LI About
Website == domain, read CB Website == domain. Match → bound. Any mismatch → that ONE url is
unbound and re-hunted; the others keep their binding. The CSV is one vendor's join and vendor
joins misbind at measured rates (Apollo: 1 in 6 domains, their own eval). **Miss caught:** the
CSV's LinkedIn column pointing at the twin because the vendor matched on name.

**5 · CB watcher, CB URL only.** Start ON the Crunchbase page — its Website field is the anchor
— then reach LinkedIn from the *website's own* footer/social links. Never Google the name first:
every hop in the CB→site→LI chain is the company asserting its own identity, while a name search
re-opens the twin door you didn't need to open. **Miss caught:** name-search landing on the
better-SEO twin while the CB page had the real domain the whole time.

**6 · Careers hunt order.** (1) one Google ATS sweep:
`"{Company}" (site:job-boards.greenhouse.io OR site:boards.greenhouse.io OR site:jobs.ashbyhq.com OR site:jobs.lever.co OR site:apply.workable.com OR site:ats.rippling.com OR site:jobs.personio.com OR site:career.teamtailor.com OR site:join.com)`
(2) homepage footer/header links (Careers · Jobs · Join · We're hiring). (3) **page-source scan**
for `greenhouse|ashbyhq|lever.co|workable|rippling|personio|teamtailor|join.com|comeet|myworkdayjobs`
— the embed token is in the source even when the render shows nothing (~half of boards are
embed-only, measured 5-of-12 on Ashby). (4) `/sitemap.xml`, grep career|job|hiring|join.
(5) token guess `{domain-root}` on Ashby + Greenhouse + Lever. **Stop after 5.** Bind = provider
+ token parsed from the URL pattern, **verified by one API fetch that answers** and a board that
links/brands back to the domain. **Miss caught:** the embed-only Ashby invisible to steps 1–2,
caught at 3.

**7 · Live vs stale.** A board is live when **the ATS API answers for the token** (0 jobs is
still live — a measured 0) or the rendered page shows **repeated role-structures with apply
links**. A 200 at /careers with no role-structures is a marketing page: do NOT bind it, run
steps 3–5 to find the real board behind it, and if nothing → LOOKED-NONE with date. **Never bind
the marketing URL as careers_url — a bound door that can't be counted looks measured forever.**
**Miss caught:** "Coming soon!" read as no-board while 3 roles sat below the fold.

**8 · Fake careers (product SPA at /careers).** Render, scroll until DOM nodes stop appearing
(not a timer), count role-structures across the whole page. **Zero structures + zero ATS markers
in source = not a board.** Cross-check: same nav bar as the homepage and no job schema = the
product, not a board. **Rule: bind only what an API answer or counted role-structures prove.**
**Miss caught:** the SPA that reloads the homepage at every path.

**9 · Two ATS live.** Bind the one the company's **own site links to** — the first-party chain is
the company telling you which is current. Site links neither: bind the one with the **newest
posting date**, record the other as an alias with a re-check note. **Never both — two boards is
two rulers, and their disagreement would be unreadable.** **Miss caught:** the abandoned
Greenhouse left live after an Ashby migration, feeding stale counts to whoever binds first-found.

**10 · Acquired, child redirects to parent.** **Confirmed: do not bind the parent board.** The
parent's 5,000 roles measure the parent's demand, not this company's. Write: canonical domain =
parent (child domain recorded as alias), careers = LOOKED-NONE with reason `acquired — parent
board is not this company's demand`, and **flag JD with the acquisition itself** — that is a
status event (Tracking or Do Not Pursue is his call), and it's also one of his five outreach-angle
events. **Miss caught:** a 40-person child "hiring 900 roles" because the parent board leaked in.

**11 · LOOKED-NONE stop rule.** Honest to stop when the coded list below is exhausted — the five
hunt steps plus the LinkedIn Jobs check — roughly 3 minutes of machine time. Always written as
`looked-none · {date} · {steps tried}`, suppressed ~30 days, then re-hunted (a company with no
board opens one when it raises). **Miss caught:** the permanent "no careers page" that was never
re-asked after the company doubled.

**12 · ATS API count.** Verified endpoints: Greenhouse
`boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true` (location.name + offices), Ashby
`api.ashbyhq.com/posting-api/job-board/{token}` (location + isRemote), Lever
`api.lever.co/v0/postings/{token}?mode=json` (categories.location + workplaceType). Rippling /
Personio / Teamtailor / JOIN go through the adapter registry the same way — **record one real
payload per provider and write the adapter against the recording, don't code field names from
memory.** **Location rules:** NYC bucket = case-insensitive token match on {new york, nyc,
manhattan, brooklyn, new york city, ny}; **Jersey City / Hoboken / Stamford = metro-not-NYC**
(counted separately, per the Manhattan-skew ruling); multi-location roles count once, NYC wins.
**Workplace type:** use the provider's declared field when it exists (Lever, Comeet declare);
else infer from title/location string ("Remote" → remote, "Hybrid" → hybrid); **neither declared
nor inferable = location-type unknown → Desk Jobs stays blank, never assumed in-office.**
**Miss caught:** "Remote — New York" counted as an NYC desk.

**13 · First-party board, no ATS.** The DOM reader with the full protocol: scroll-settle,
structure count, union across the page, never first-match. **Parseable structures → count, capped
Partial until a different signal corroborates. Unparseable → LOOKED-NONE (JD), never 0** — a
reader that can't parse has measured nothing, and a deterministic reader bug re-runs identically
forever. **Miss caught:** the same broken reader "confirming" its own zero on the scheduled
re-check.

**14 · Sales Nav path.** From stored `/company/{slug}`: read the numeric org id out of the loaded
page → navigate `linkedin.com/sales/company/{id}` → **verify the SN header shows the same name
AND website** → people list → filter **Person geography = the pinned config constant** (settle
Metro-Area vs "New York, New York, United States" once, in config, before the batch) → **write
the header count as NYC Employees**, recording which constant produced it. **Refuse:** name
search into SN, the "Company headquarters location" filter (where it's registered, not where
humans sit), and saving the people-search URL anywhere — the search URL is a measurement, the
`/sales/company/{id}` URL is the identity. **Miss caught:** an HQ-filtered count writing 200
Delaware-registered heads as NYC.

**15 · SN shows 0.** Three checks before anything is written: **(a) right company** — header name
+ website match the store; **(b) right filter** — the geography chip shows the pinned constant
and the company chip shows this company; **(c) plausibility** — if LI About says 51-200 with NYC
HQ, or the careers board shows NYC roles, a 0 is internally contradictory → write nothing, flag
`needs a real read`. All three pass → write 0 marked Partial (a UI zero), corroborate next pass.
**Miss caught:** a hollow soft-block page serving an empty result that looks exactly like a
clean zero.

**16 · Missing jobs must not raise Fit.** **Code rule: the denominator is always 100. Never
renormalize.** Every component scores out of its fixed weight; a missing input earns 0 of that
component and no other component's weight moves. Enforce it with a boot property next to
`formula_is_coherent`: for every component, `score(input missing) <= score(input present)` — a
missing anything that raises any score fails the boot. The 57→66 case was renormalization: drop
jobs and the other weights inflate ~11%. (Under COS gate 2 jobs is a required primary so the
company wouldn't score at all — the boot check is for every optional component too.)

**17 · No funding history.** **"Not applicable," score without the velocity refinement — never
LOOKED-NONE.** Growth is keyed on the two signals the wash actually measures — live NYC hiring
and a fresh raise — and dated-round velocity is a refinement where history exists. Blocking on
velocity would block on data most CSV companies can never have. No renormalization: growth earns
what the live evidence supports, out of 10.

**18 · Dedup.** Identity key = registrable domain, post-redirect, aliases recorded. Same domain
from CSV and watcher = **same row**: merge, keep BOTH `added_from` tags — two independent sources
finding the same company is itself a mild positive signal, not a conflict. Same name, different
domains = not a dup; hunt both companies' doors and let the domains decide. **Never create the
second row and "clean it up later" — the tombstone rule exists because deleted rows resurrect on
the next CSV.**

---

## CODED DOOR-HUNT CHECKLIST

```
INPUT: intake_name + whatever URLs the intake carried
KEY:   registrable_domain (eTLD+1, lowercase, post-redirect). Aliases for every hop.

D1  WEBSITE
    a  intake has website URL?            → fetch, follow redirects, canonical = final domain
    b  else X profile has a link?         → that link is the anchor. fetch, canonicalize
    c  else search: "{name}" {2 bio words}, first-party domains only
       refuse: linkedin/crunchbase/pitchbook/news/portfolio/app-store/parked
    d  page copy matches intake claim?    → LOCK. else next result. page-1 exhausted → LOOKED-NONE

D2  CRUNCHBASE
    a  stored CB URL → read Website field → == canonical domain?  → bound
    b  mismatch or none → CB search by domain, not name → none → cb: looked-none (funding blank, still scoreable per B)

D3  LINKEDIN
    a  stored /company/ URL → About → Website == canonical domain? → bound
       also read: HQ, founded, size band (this IS total employees)
    b  mismatch → unbind, find LI from website's own footer/social links
    c  none → li: looked-none → NO SCORE (Sales Nav has no door) → flag JD

D4  CAREERS  (steps in order, stop on first bind)
    1  Google ATS sweep (query in ruling 6)
    2  homepage footer/header links
    3  page-source scan for ATS strings          ← catches embed-only (~50%)
    4  /sitemap.xml grep career|job|hiring|join
    5  token guess {domain-root} on ashby, greenhouse, lever
    BIND = provider + token, verified: API answers AND board links/brands to domain
    all 5 fail + LI shows no ATS-linked jobs → careers: looked-none · date · steps

GATE COS-1: D1 locked AND (2 of {D2,D3,D4} bound, none contradicting) → identity PASS
            two agree + one odd → unbind the odd one, re-hunt it, company survives
            odd one is D1 itself → LOOKED-NONE the company, flag JD
GATE COS-2: score only if NYC Employees, NYC jobs, HQ, industry, stage are real values
            (measured 0 counts; blank or looked-none on a primary = no score, flag JD)
```

## CODED P2 COUNT CHECKLIST

```
C1  ats_provider known?  → hit the provider API with board_token
C2  per job:
      nyc      = location tokens {new york|nyc|manhattan|brooklyn|new york city|ny}
      metro    = {jersey city|hoboken|stamford|white plains|long island} → count separately
      type     = provider's declared field first (lever.workplaceType, comeet, etc.)
                 else title/location string: "remote"→remote, "hybrid"→hybrid
                 else → location_type = unknown
      multi-location: count once, NYC wins
C3  nyc_open_jobs   = count(nyc)
    desk_jobs       = office + 0.8*hybrid   (remote=0; unknown → desk_jobs BLANK)
    posting dates, seniority, role-type → stored per job
C4  API 0 → real 0, Verified.
C5  no API (first-party board) → DOM reader: scroll-settle, structure count, union
      parseable → count, mark Partial
      unparseable OR (0 structures but office cities listed on page) → looked-none, flag JD
C6  bound endpoint 404s → re-enter door hunt (D4), never write 0
```

## SALES NAV — 10 LINES

```
1   open stored linkedin.com/company/{slug}           (never name search)
2   read numeric org id from the loaded page
3   go to linkedin.com/sales/company/{id}
4   check header: name == store AND website == store   → mismatch: STOP, twin
5   open people list for this company
6   filter: Person geography = PINNED_GEO_CONSTANT     (never Company HQ location)
7   read the header count
8   count 0? run ruling-15 checks (right company / right filter / plausible) → contradiction: flag, write nothing
9   write NYC Employees = count (+ geo constant used); 0 → mark Partial
10  /checkpoint/ /challenge/ authwall 401 at ANY step → HALT the lane, no retry, tell JD
```

## BUILD-NEXT (only what the machine is missing)

1. **`PINNED_GEO_CONSTANT` in config** — settle Metro-Area vs "New York, New York, United
   States" once against a known company, pin the winner, every measurement records it.
2. **`ats_provider` + `board_token` + `bound_via` + `bound_at` as first-class store columns** —
   if the adapter registry already persists them, confirm with a query, not the code's word.
3. **`door_status` per door** (website / cb / li / careers): `bound | looked-none {date, tried}` —
   this is what makes COS-1/COS-2 computable instead of narrative.
4. **`added_from` becomes multi-source** — the dedup-merge in ruling 18 needs to keep both tags.
5. **`metro_not_nyc_jobs` count field** — the Jersey-City bucket from C2, so the Manhattan skew
   is a number, not a footnote.
6. **The boot property from ruling 16** — `score(missing) <= score(present)` per component,
   beside `formula_is_coherent`.
7. **Recorded payloads for Rippling / Personio / Teamtailor / JOIN** before their adapters are
   written — one real response each, tests against the recording.

Locked.
