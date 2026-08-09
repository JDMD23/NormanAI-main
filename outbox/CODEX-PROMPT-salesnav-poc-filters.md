# Codex task — extract my Sales Navigator workplace-POC search filters

I need the **exact filter configuration** of my LinkedIn Sales Navigator lead search(es) for
finding workplace / office decision-makers. I am going to port the intent of these filters
into a different data vendor, so I need the configuration captured **precisely and
completely** — not summarized.

I am logged into Sales Navigator in my browser. This is my own account and my own saved
searches.

---

## HARD LIMITS — read these before you touch anything

These are not preferences. My LinkedIn account is the single highest-risk asset in this
system and it is under a documented commercial-use rate limit.

1. **Read filter CONFIGURATION only. Do not run searches to browse results, do not paginate,
   do not open any lead profile, do not export, do not save, do not modify or delete any
   saved search.** This is a read of the filter panel.
2. **Keep total page loads under 10.** Count them and report the number. Every page load
   spends a budget that other work depends on.
3. **On ANY interstitial — captcha, "unusual activity", a verification prompt, a login
   challenge, a rate-limit notice — STOP IMMEDIATELY.** Do not retry, do not refresh, do not
   attempt a workaround. Report what you saw and end the task. A single retry into a
   challenge is worse than returning nothing.
4. **Change nothing.** If an action would write, save, or alter state, don't take it.

If you can only complete part of this within those limits, **return the partial result and
say what's missing.** Partial and honest beats complete and risky.

---

## What to do

### Step 1 — enumerate
Go to Sales Navigator → **Lead search → Saved searches** (also check **Personas** and
**Lead lists** if present). List every saved search you find, with its name.

Report the list. If exactly one is obviously the workplace/office decision-maker search,
proceed with it. **If more than one could plausibly be it, capture all the plausible ones** —
I'd rather have extras than the wrong one.

### Step 2 — open the filter panel and EXPAND EVERYTHING
Open the saved search and expand every filter section. Two things that are easy to get wrong:

- **Filter chips collapse.** If you see "+3 more" or a truncated list, **expand it and
  capture every value.** A truncated list is a wrong answer, not a short one.
- **Sales Nav title/keyword filters have INCLUDE and EXCLUDE sides.** Capture both.
  **The exclusions are as important as the inclusions** and they are the thing most commonly
  missed — a collapsed panel often hides them entirely.

### Step 3 — capture these sections
Go through all of them. If a section exists but is empty, record it as empty — **"set to
nothing" and "I didn't look" are different answers and I need to tell them apart.**

- **Current job title** (including any boolean string, and included vs excluded values)
- **Past job title**
- **Seniority level**
- **Function / Department**
- **Years in current position** and **Years in current company**
- **Geography** — the PERSON's location (note the exact region strings used, e.g. "New York
  City Metropolitan Area" vs "New York, United States" — the precise wording matters to me)
- **Company headquarters location** (this is a different filter from the person's geography —
  capture both separately and do not merge them)
- **Company headcount**
- **Company type**
- **Industry** — note whether it's set on the person or the company, or both
- **Keywords** (any free-text or boolean)
- **Connection degree / relationship**, TeamLink, past colleague
- **Recent updates** — changed jobs, posted recently, mentioned in news
- **Buyer intent**, if set
- **Anything else set that I haven't listed** — capture it, don't skip it because it's not on
  my list

### Step 4 — the result count
Record the **total result count the search reports** (the number shown on the results header).
**Do not page through results to get it** — it's displayed without paginating.

I need this number. A filter set without its result count tells me nothing about how
selective it actually is.

### Step 5 — capture the URL
Copy the **full saved-search URL**, including all query parameters. Sales Nav encodes filter
state in the URL and it's the most reliable record of what was actually set.

---

## Output format

Give me **JSON**, one object per saved search, plus a short plain-English note at the end.

```json
{
  "saved_searches_found": ["...", "..."],
  "captured": [
    {
      "name": "",
      "url": "",
      "result_count": 0,
      "filters": {
        "current_job_title":       { "include": [], "exclude": [], "boolean": null },
        "past_job_title":          { "include": [], "exclude": [] },
        "seniority":               { "include": [], "exclude": [] },
        "function":                { "include": [], "exclude": [] },
        "years_in_current_position": null,
        "years_in_current_company":  null,
        "person_geography":        { "include": [], "exclude": [], "exact_labels": [] },
        "company_hq_location":     { "include": [], "exclude": [], "exact_labels": [] },
        "company_headcount":       [],
        "company_type":            [],
        "industry":                { "applied_to": "person|company|both", "values": [] },
        "keywords":                null,
        "connection_degree":       [],
        "recent_updates":          [],
        "buyer_intent":            [],
        "other_filters_set":       {}
      },
      "sections_present_but_empty": [],
      "sections_not_found_in_ui":   []
    }
  ],
  "page_loads_used": 0,
  "interstitials_encountered": "none | describe",
  "anything_ambiguous": ""
}
```

**Rules for filling this in:**

- **Copy labels VERBATIM as the UI shows them.** Do not normalize, translate, or tidy them
  into what you'd expect the field to be called. I am mapping these strings to another
  system's vocabulary, and the exact wording is the whole point. "New York City Metropolitan
  Area" and "New York, United States" are different answers.
- **Never guess a value.** If something is truncated and you couldn't expand it, or you
  couldn't tell whether a filter applied to the person or the company, put it in
  `anything_ambiguous` and say so. **An honest "I couldn't determine this" is useful; a
  plausible guess is actively harmful**, because I can't tell it apart from a real reading.
- Distinguish clearly between **"filter exists in the UI and is set to nothing"**
  (`sections_present_but_empty`) and **"I couldn't find this filter"**
  (`sections_not_found_in_ui`).

Also attach **screenshots of the expanded filter panel** as a backup — if the JSON and a
screenshot ever disagree, I want to be able to tell.

---

## Finally

After the JSON, in two or three plain sentences: **which filters look like they're doing the
real narrowing**, and which look incidental. Your read as an observer — I'll check it against
my own.
