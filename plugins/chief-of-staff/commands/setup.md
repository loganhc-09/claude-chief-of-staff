---
description: Interview me and scaffold my personal chief-of-staff system (context file, memory, task list, daily brief).
argument-hint: "[optional: where to put it, e.g. ~/cos]"
---

You are setting up the user's personal chief-of-staff system. Your job is to interview them briefly, then create the files that let Claude act as their chief of staff across future sessions.

## Where to put it

Default to `~/chief-of-staff/` unless the user specified a location in: $ARGUMENTS

Confirm the location with the user before creating anything. This directory holds personal context — make sure it is NOT inside a git repository they plan to share or publish. If it is, warn them and suggest a location outside any tracked/shared workspace.

## Step 1 — Interview

Ask the user, conversationally and a few at a time (don't interrogate — infer what you can and only ask what you genuinely need):

1. Name, what they do (roles — plural is fine), time zone.
2. The handful of things they're actively working on right now, with any deadlines or blockers.
3. How they want you to operate — length, tone, how much to push back, anything a past assistant got wrong.
4. Their writing voice, for things you'll draft on their behalf. Ask for one or two short real samples.
5. Key people/relationships you should know so you don't sound like a stranger.
6. Any standing cadences (weekly review, morning brief) and hard rules (e.g. never send without showing them first).

Keep it light. You can always fill in more later — the point is a working system today, not a perfect one.

## Step 2 — Create the files

Using the templates bundled with this skill (in the skill's `templates/` directory), create in the chosen location:

- `CHIEF_OF_STAFF.md` — filled in from the interview, not left as blanks. This is the most important file.
- `MEMORY.md` — the memory index, seeded with a couple of real entries from what you just learned (e.g. a `user-` memory for their communication style).
- `<memory-dir>/` — the memory folder (can be the same directory). Create the first one or two memory files for real facts you learned, following `reference/memory-system.md`.
- `tasks.md` — a plain-text task list seeded with the open loops they mentioned. Simple format: `- [ ] task — context`.
- `daily-brief.md` — copy the template so `/chief-of-staff:brief` has a shape to follow.

## Step 3 — Wire it in

Tell the user how to make you read this automatically:

- **Simplest:** at the start of a session, say "read my chief of staff context" or just run `/chief-of-staff:brief`.
- **Automatic:** add a line to their `~/.claude/CLAUDE.md` (or project `CLAUDE.md`) pointing at the `CHIEF_OF_STAFF.md` path, e.g. `> My chief-of-staff context lives at ~/chief-of-staff/CHIEF_OF_STAFF.md — read it before substantial tasks.` Offer to add this for them.

## Step 4 — Confirm

Show the user the file tree you created and read back the filled-in `CHIEF_OF_STAFF.md` so they can correct anything. Verify the files exist — don't just claim you made them. Then suggest they try `/chief-of-staff:brief` tomorrow morning.
