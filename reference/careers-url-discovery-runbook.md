# Finding a company's careers board — the runbook

**For someone doing this 80 times.** Target: **under 90 seconds per company, 3 minutes hard cap.**

**What you are producing is not a job count. It is a BINDING:**

```
careers_url  +  ATS provider  +  board token
```

**Norman counts the jobs.** You find the door. **Do not hand-count roles** — that spends the
expensive resource (you) on the cheap half of the job. Once the token is bound, counting is a free
API call, forever, with no browser.

**Honesty note:** this sandbox blocks company sites and ATS APIs, so nothing below was walked live
in this session. The URL patterns come from the recorded ATS ruling (Q2), the failure modes from
the Brandlight post-mortem (K1), and the Q15 example from the build record.

---

## 1 · Where you look first — and it is not the homepage

**Google first, with one multi-ATS query.** Not the website, not LinkedIn, not Crunchbase.

**Two reasons, both measured:**

**~50% of boards are embed-only.** The careers link and the ATS embed live in JS-rendered DOM, so
the homepage often shows you nothing useful without a render and a scroll. **Measured: 5 of 12
Ashby boards were embed-only** — which made the browser path the default, not the fallback.

**The ATS-hosted board is what you actually want.** A company's `/careers` page is frequently a
wrapper around Greenhouse or Ashby. **The wrapper is not the thing** — the ATS board behind it is
API-countable and the wrapper is not. Going to the homepage first means finding the wrapper and
then having to dig out the token anyway.

> **One search can hit all four major ATSes at once. One homepage load hits nothing at once.**

**Go to the site second, not first.** It is the fallback for companies too small to be indexed.

---

## 2 · The exact queries — five templates

**Run #1. If it returns a board, you are done in ten seconds.**

**① The multi-ATS sweep — your default**
```
"{Company}" (site:job-boards.greenhouse.io OR site:boards.greenhouse.io OR site:jobs.ashbyhq.com OR site:jobs.lever.co OR site:apply.workable.com)
```

**② The source-code hunt — catches embedded boards Google indexed through the wrapper**
```
"{domain}" (greenhouse OR ashbyhq OR lever OR workable OR comeet OR rippling)
```

**③ The site-restricted sweep — when you know the domain but not the path**
```
site:{domain} (careers OR jobs OR hiring OR "open roles" OR "join us")
```

**④ The aggregator-stripped search — forces first-party results up**
```
"{Company}" careers -site:linkedin.com -site:indeed.com -site:glassdoor.com -site:ziprecruiter.com -site:builtinnyc.com
```

**⑤ The disambiguator — use when the name is generic**
```
"{Company}" "{domain}" jobs New York
```

**Use the domain, not just the name, in at least one query.** Name-only search is where twins get
picked up, and Apollo's own eval measured **1 in 6 domains misbound** on name matching.

---

## 3 · On the site: the click order

**① Footer, immediately.** One `End` keypress. Careers lives in the footer far more often than the
header, and the footer is static HTML on sites where the header is a JS component. **Look for:**
`Careers` · `Jobs` · `Join us` · `Work with us` · `We're hiring` · `Team`.

**② Header nav, only if there is a `Company` or `About` dropdown.** Standalone header "Careers"
links are less common than footer ones.

**③ Type `/careers` directly.** Faster than hunting if the footer is a mega-menu.

**④ View source and search it** — see §10. **This is the step most people skip and it is the one
that finds embedded boards.**

**⑤ `/sitemap.xml`.** One fetch, enumerates every URL the site admits to having.

**Do not scroll the homepage hunting for a "We're hiring" banner.** Marketing banners are the
lowest-yield signal on the page and they cost the most time.

---

## 4 · The off-site boards, and the exact pattern for each

**The token is derived from the DOMAIN ROOT, not the display name.** "Silna Health" at
`silnahealth.com` is `silnahealth` far more often than `silna-health`.

| ATS | board URL | count endpoint | token shape |
|---|---|---|---|
| **Greenhouse** | `job-boards.greenhouse.io/{token}` *(legacy: `boards.greenhouse.io/{token}`)* | `boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true` | domain root, lowercase, no punctuation |
| **Ashby** | `jobs.ashbyhq.com/{token}` | `api.ashbyhq.com/posting-api/job-board/{token}` | domain root; sometimes display name |
| **Lever** | `jobs.lever.co/{token}` | `api.lever.co/v0/postings/{token}?mode=json` | domain root |
| **Workable** | `apply.workable.com/{token}/` | widget API on the same host | domain root, hyphenated |
| **Rippling** | `ats.rippling.com/{token}/jobs` | — | display name, hyphenated |
| **Comeet** | `comeet.com/jobs/{token}/...` | declares workplace type explicitly | company slug |
| **YC** | `ycombinator.com/companies/{slug}/jobs` | — | YC's own slug |
| **Wellfound** | `wellfound.com/company/{slug}/jobs` | — | company slug |
| **Notion-hosted** | any `notion.site` URL | **none — no API** | — |

**Try the token by domain root first. If that 404s, try the hyphenated display name. Two guesses,
then stop guessing and go back to search.**

**Greenhouse and Ashby are the two that pay.** Together they cover most NYC startups at this
stage. **Check those two before the others.**

**Notion-hosted boards have no API.** Bind them, but flag them — they will always need the DOM
reader, so they carry the DOM reader's error profile forever.

---

## 5 · LinkedIn → careers URL: don't

**Short answer: LinkedIn is a bad tool for this and a risky one. Skip it.**

**Why it does not work:**

- **The About tab's Website field is the domain you already have.** Zero new information.
- **"See all jobs" goes to LinkedIn Jobs**, which is LinkedIn's own listing surface — **not the
  company's board.** It is not API-countable, it under-reports, and it is not a careers URL.
- The only genuinely useful LinkedIn path is **a recent hiring post that links the ATS directly**,
  and hunting for one costs more than the search in §2.

**Why it is risky:** LinkedIn is the highest-exposure account in the system. It is UI-only,
attended, one approval per session, **halt on the first challenge with no retry.** Spending that
budget on careers discovery — a job four free searches do better — is the wrong trade.

**Sales Nav is for headcount. Nothing else.**

---

## 6 · `/careers` and `/jobs` both 404 — the next five, in order

**① `/sitemap.xml`** ← **do this first, it beats the other four combined**
One fetch, then search the XML for `career`, `job`, `hiring`, `join`. **It enumerates the paths
the site admits to having**, so it turns guessing into reading.

**② View source on the homepage, search for ATS strings** — see §10.

**③ The path variants**, in this order:
```
/company/careers   /about/careers   /join   /join-us
/work-with-us      /hiring          /careers.html
```

**④ The two token guesses** — `jobs.ashbyhq.com/{domain-root}` and
`job-boards.greenhouse.io/{domain-root}`.

**⑤ `/team` or `/about`.** Team pages very often carry a "we're hiring" link when there is no
top-level careers nav — especially at seed stage.

---

## 7 · Telling a real board from a marketing page

**Classify on STRUCTURE, never on TEXT.** This is the rule that came out of the Brandlight
post-mortem, where the reader got it wrong three reinforcing ways at once.

**It is a real board when:**
- **Repeated role-structures appear** — the same title + location + link pattern, two or more
  times. A list of things with a shape is a board.
- Each entry links somewhere applyable.
- Locations are attached per role, not stated once at the top.

**It is a marketing page when:**
- There is a values statement, photos of the team, and a single `hello@` or "send us your resume."
- Roles are named in prose but do not link anywhere.

**Three traps, each of which caught the machine once:**

**"Coming soon" and "no open roles" are CLAIMS, not evidence.** A zero requires **zero
role-structures across the entire settled page.** A page's words are marketing; its structure is
the fact.

**Listings lazy-load on scroll.** Scroll to the bottom and wait until DOM nodes **stop appearing**
— not a fixed timer. A timed wait repeats the exact miss.

**Never anchor on the first heading.** Take the **union of role-structures across the whole page.**
First-match extraction grabbed a hero section instead of the real board.

**And the contradiction check that would have caught it:** a page that **lists office cities**
("NYC · London · TLV") and extracts **zero roles** is internally contradictory. Office cities are a
claim of presence a zero contradicts. **That routes to "needs a real read," never to a confident
zero.**

> **A DOM-extracted zero is `Partial`, never `Verified`. A positive count with named roles is
> `Verified` immediately** — three named roles are self-corroborating in a way absence never is.

---

## 8 · Proving the board is THIS company

**The bar: a domain match, OR two independent non-name signals. Name alone never binds.**

**Ranked by strength:**

**① The board links back to the domain.** The ATS board's header logo or footer links to
`company.com`. **This is the strongest single signal** — it is the company asserting the board is
theirs.

**② The token contains the domain root.** `jobs.ashbyhq.com/silnahealth` for `silnahealth.com`.

**③ The job descriptions name the product or the domain.** Read one posting. Real postings
describe the actual product.

**④ Locations match what you know.** A NYC company whose board is entirely Bangalore roles is a
different company.

**Record WHY you bound it.** One line — *"footer links silnahealth.com"* — so a later re-check can
audit the decision instead of re-deriving it.

**When two candidates both look right: bind neither.** Ambiguity forces a pick by a human, and a
low-confidence match is never auto-bound. **A wrong binding is worse than a missing one** — it
produces confident numbers about a stranger.

---

## 9 · YC companies

**Yes, always open `ycombinator.com/companies/{slug}/jobs` — but for one specific reason.**

**Not as the answer. As a pointer to the answer.** YC's page usually links out to the company's
real ATS board, and **that link is the thing you want** — it is authoritative (the company
supplied it) and it is API-countable.

**Do not bind the YC URL as the careers URL when an ATS link exists behind it.** YC pages go stale;
the ATS board does not.

**If YC is the only thing that exists**, bind it and flag it — same category as a Notion-hosted
board: readable, not countable.

---

## 10 · Single-page apps where `/careers` reloads the homepage

**This is the ~50% case, and the token is almost always in the page source even when the render
shows nothing.**

**In order:**

**① View source and Ctrl-F for these strings:**
```
greenhouse   ashbyhq   lever.co   workable   comeet   rippling   myworkdayjobs   boards-api
```
**One of them hits far more often than not.** The embed script carries the board token as a
parameter — that token *is* your binding, and you never need the rendered page again.

**② Try the hash route** — `/#/careers`, `/#careers`. Older SPAs route on the fragment.

**③ `/sitemap.xml`** — SPAs frequently still ship a real sitemap.

**④ Open devtools → Network → filter XHR → reload.** The board data arrives as a JSON call.
**That request URL is the API endpoint**, which is better than the page.

**⑤ The two token guesses.**

> **When the render is empty and the source has a token, the source wins.** The page failing to
> display roles is not evidence there are none — **that is exactly the false zero that put a
> company on the board with the wrong number.**

---

## 11 · Crunchbase

**Do not use Crunchbase's careers or contact links.** They are stale, second-hand, and frequently
point at a `/careers` that moved.

**Use it for exactly one thing: resolving the canonical domain after a rebrand or a redirect.**
That is a real, recorded case — `deeptune.ai` redirects to `deeptune.com`, and only the second one
carries the board.

**Otherwise: website + search. Two sources, both first-party.**

---

## 12 · The time budget, and the last thing you try

**90 seconds is the target. 3 minutes is the cap. Then stop.**

```
0:00–0:15   query ① — the multi-ATS sweep
0:15–0:35   the site: footer, then /careers
0:35–1:00   view source, search for ATS strings          ← highest yield of any single step
1:00–1:30   /sitemap.xml, then the two token guesses
1:30–3:00   queries ② and ④
3:00        stop
```

**The last thing you try, always: `/sitemap.xml` plus a source search for ATS strings.** If the
site has a board and you have not found it, it is in one of those two places.

**When you write "no careers page," write it as a dated claim, not a fact:**

```
no careers page found · 2026-08-13 · tried: /careers /jobs /join sitemap source-scan ashby+gh tokens
```

**It suppresses the ask for 30 days and then re-asks — not forever.** A company with no board today
opens one when it raises. **And the re-check must actually re-run discovery**, not re-derive the
same answer from the same stored state — that bug shipped once, and the ask kept coming back after
it was answered.

---

## 13 · You found LinkedIn Jobs but no board — is that the careers URL?

**No. Keep looking, and if nothing turns up, store it somewhere else.**

**`careers_url` means "an endpoint Norman can count from on a cadence."** A LinkedIn Jobs URL is
none of those things — it is not API-countable, it under-reports NYC roles, and it carries no
in-office/hybrid/remote classification, **which is the field the score actually needs.**

> **Putting a LinkedIn URL in `careers_url` does not fill the gap. It hides it** — the board shows
> a careers URL, the count path silently produces nothing, and the company looks measured.

**Record it as the LinkedIn-jobs fallback state instead.** That state already exists
(`Norman: LinkedIn jobs fallback`), it keeps the company countable-ish, and it keeps it visibly
**in the backlog** rather than falsely resolved.

---

## 14 · What you write down when you find it

**Three fields. That is the binding.**

| field | example |
|---|---|
| **`careers_url`** | `https://jobs.ashbyhq.com/silnahealth` |
| **`ats_provider`** | `ashby` |
| **`board_token`** | `silnahealth` |

**Plus two lines of provenance:** the date, and **why you believe it is this company** — *"footer
links silnahealth.com."*

**Do NOT hand-count roles.** Norman hits the API and counts them, with location type, posting date,
seniority and role type attached — **none of which you can reliably read by eye, and all of which
the score needs.** Counting by hand is slower and produces a worse number.

**Two exceptions worth ten seconds:**

- **If the board renders zero roles, say so** — "board found, 0 roles visible." A DOM zero is
  capped at `Partial` and needs independent corroboration before it is trusted, so your
  observation is a data point, not a conclusion.
- **If it is a Notion-hosted or otherwise API-less board, flag it.** It will need the DOM reader
  forever.

---

## 15 · A real case — Deeptune

**Stated plainly: I could not reach the internet from this session, so I did not walk a fresh
company. This one is from the build record.**

**Deeptune is the recorded case of the first URL failing and the board still being found:**

```
1 · The stored domain is  deeptune.ai
2 · deeptune.ai  redirects to  deeptune.com          ← the first key resolves, but not to itself
3 · deeptune.com  links an Ashby board
4 · That Ashby board was ALREADY IN THE STORE, bound to a different key
5 · Bound on two independent keys — the redirect and the board link — both recorded
```

**The lesson that made it worth recording:** the first instinct was to add a new `domain` alias
type to the schema. It was declined — **the alias schema already carried `slug-redirect`, which
covers exactly this.**

> **An unfamiliar-looking case is more often an instance of a known category than a new one.**

**Practically, for you:** when a domain redirects, **the redirect target is a second identity key,
and the board may already be in the system under it.** Check before you bind — you may be creating
a duplicate rather than finding a board.

**And the case worth knowing for the opposite reason — Brandlight.** The board *was* found. The
reader still got it wrong, three ways at once: **it did not scroll** (missed lazy-loaded
listings), **it anchored on the first section** (took the hero, not the board), and **it read
"Coming soon!" as a zero** (text as evidence). **There were 3 real roles.**

**The company sat on the board with a false zero — which suppressed 26 of 100 scoring points.**

> **A deterministic reader bug re-runs identically forever. A scheduled re-check does not heal a
> false zero — it confirms it.**

**Which is why §7 is written the way it is: structure, never text.**

---

# THE CARD — print this

```
GOAL: careers_url + ats_provider + board_token.  NOT a job count.
TIME: 90s target · 3min hard cap

1  SEARCH   "{Co}" (site:job-boards.greenhouse.io OR site:jobs.ashbyhq.com
                    OR site:jobs.lever.co OR site:apply.workable.com)
2  SITE     footer → /careers
3  SOURCE   view-source, Ctrl-F: greenhouse ashbyhq lever workable comeet rippling
4  SITEMAP  /sitemap.xml → search: career job hiring join
5  GUESS    jobs.ashbyhq.com/{domain-root} · job-boards.greenhouse.io/{domain-root}
6  STOP     record: no careers page · DATE · paths tried

BIND ONLY IF: domain match, or two non-name signals. Write down WHY.
REAL BOARD  = repeated role-structures. NOT the words on the page.
"Coming soon" is a CLAIM. Zero roles + office cities listed = needs a real read.
LinkedIn Jobs is NOT a careers_url — it's the fallback state.
Domain redirects? The target is a second key — it may already be bound.
```
