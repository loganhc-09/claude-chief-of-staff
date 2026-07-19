# The Memory System

A chief of staff who forgets everything between conversations isn't a chief of staff. This is a simple, durable, file-based memory the user owns in plain text — no database, no lock-in. `/cos:setup` creates it; this file documents the convention so you can read and write it consistently.

## Layout

```
<memory-dir>/
  MEMORY.md            # the index — one line per memory, loaded every session
  user-<slug>.md       # who the user is: role, preferences, working style
  project-<slug>.md    # ongoing work, goals, constraints
  feedback-<slug>.md   # corrections and confirmed ways of working
  reference-<slug>.md  # pointers to external resources (URLs, docs, accounts)
```

One fact per file. Small files beat one giant file — they're easier to update, prune, and recall precisely.

## File format

Each memory file has YAML frontmatter and a short body:

```markdown
---
name: <short-kebab-case-slug>
description: <one-line summary — used to decide relevance during recall>
type: user | feedback | project | reference
---

<The fact. For feedback and project entries, follow with:>
**Why:** <the reason it matters>
**How to apply:** <what to do differently>

<Link related memories inline with [[their-name]].>
```

## The index

`MEMORY.md` is the single file loaded into context at the start of every session. It is an *index only* — one line per memory, pointing to the detail file:

```markdown
- [Prefers short replies](user-communication-style.md) — lead with the answer, no preamble
- [Q3 launch](project-q3-launch.md) — ships Sept 15; legal review is the blocker
```

Never put memory *content* in `MEMORY.md`. It's a table of contents, not the book. If it grows past what fits comfortably in context, that's the signal to prune or consolidate.

## The four types

- **user** — who they are: role, expertise, preferences, working style, how they want you to operate.
- **feedback** — guidance on how you should work, both corrections and confirmed approaches. Always include the *why* — a rule without a reason gets misapplied. This is the most valuable type; it's how you stop repeating mistakes.
- **project** — ongoing work, goals, constraints not derivable from anywhere else. Convert relative dates ("next week") to absolute ones before saving.
- **reference** — pointers to external resources: URLs, dashboards, account names, docs.

## When to write

- The user corrects your behavior → write a `feedback-` memory immediately.
- The user states a durable preference → `user-` or `feedback-`.
- You learn a load-bearing fact about ongoing work → `project-`.
- The user points you at a resource you'll need again → `reference-`.

Before saving, check for an existing file that already covers it — update rather than duplicate. Delete memories that turn out to be wrong.

## When to read

At the start of any substantial task, read `MEMORY.md`, then open the specific files whose one-line descriptions look relevant. Recalled memories reflect what was true *when written* — if one names a file, account, or deadline, sanity-check it still holds before relying on it.

## What not to store

- Anything already recorded elsewhere the user controls (their calendar, their repo, their docs) — store a pointer instead.
- Secrets, passwords, API keys — never. Point to where they live, don't copy them.
- One-off details that only matter to the current conversation.

## Privacy

This memory lives on the user's machine in plain text and is theirs. If you ever help them share, publish, or commit their setup, the memory directory and their `CHIEF_OF_STAFF.md` must be excluded — they contain personal context that should never end up in a public or shared location. Treat that as a hard rule.
