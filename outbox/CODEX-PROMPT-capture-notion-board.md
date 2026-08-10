# Codex task — capture my Notion board as it actually is

I need an accurate picture of my Norman CRM board so it can be redesigned against reality
rather than against a schema file. **Read only. Change nothing.**

---

## HARD LIMITS

1. **Do not create, edit, delete, or reorder anything** — no properties, views, rows, or filters.
2. If an action would write, don't take it.
3. If something is ambiguous, **say so** — do not guess.

---

## WHAT TO CAPTURE

### 1 · The board as I see it
Screenshot the default view, full width. Then screenshot each existing view/tab.
**Include the tab bar in every shot** so I can see what views exist and their order.

### 2 · Properties — what's actually there vs what's hidden
For the database, list **every property**: name · type · and for select/status, its options.

**Critically: for each view, which properties are VISIBLE and which are HIDDEN.** A property that
exists but is hidden everywhere is different from one I actually read, and the schema file cannot
tell me which is which.

### 3 · Views — the real configuration
Per view: name · layout (table/board/list/gallery/timeline/calendar) · filters · sorts ·
group-by · visible properties, in their left-to-right order.

### 4 · A row, opened
Screenshot one company page **opened** — the properties panel and the page body. I want to see
what's in the body today and how much of the panel is scrolling.

### 5 · The feel
Two or three plain sentences: how many columns before it scrolls sideways? Does the default view
look scannable or dense? Anything visibly broken, empty, or duplicated?

### 6 · Capability check
In the Notion UI, note which of these exist in **my** workspace and plan:
- **Button** property · **Formula** · **Rollup** · **Relation** · **Unique ID** · **Verification**
- **Sub-items** (parent/child rows in one database)
- **Database automations** — and what triggers/actions are offered
- **Linked database views** (embedding a filtered view on another page)

**If a feature is missing or gated behind a plan, say which.** I'd rather design around a real
limit than propose something you can't build.

---

## OUTPUT

JSON for §2–§3 and §6, plain prose for §5, screenshots attached and referenced by filename.

**Never guess a value.** If a filter is complex or a property type is unclear, put it in an
`ambiguous` field and describe what you saw.
