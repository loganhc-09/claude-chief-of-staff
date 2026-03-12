# Getting Started

You don't build a chief of staff system in a weekend. You build it one layer at a time, each one useful on its own, each one making the next one better.

Here's the progression, from "10 minutes tonight" to "full operational stack."

---

## Phase 1: The Foundation (Day 1 — 10 minutes)

### Create your CLAUDE.md

This is the single highest-leverage thing you can do with Claude Code. Create a file called `CLAUDE.md` in your project folder:

```markdown
# About Me
[Your name] — [what you do in one sentence]

# Key Context
- My main focus right now is...
- I communicate via [channels]
- My voice is [casual/professional/direct/warm]

# How I Work
- Strongest at: [your superpower]
- Weakest at: [your gap]
- When drafting messages, match my voice: [2-3 style notes]
```

That's it. Even 5 lines dramatically improves every Claude interaction going forward. Add to it over time whenever Claude gets something wrong or misses context.

**Keep it tight.** CLAUDE.md loads into every session's context window — every line costs tokens. A focused 100-200 line file beats a sprawling 2,000 line one. If it's getting long, move reference material into separate memory files and keep the core instructions lean.

See [examples/CLAUDE.md](examples/CLAUDE.md) for a full template.

**What you'll notice:** Claude stops feeling generic. It starts using your terminology, matching your tone, remembering your priorities. This is the "oh, this is different" moment.

---

## Phase 2: Memory (Week 1 — 30 minutes)

### Add persistent memory files

Claude Code has an auto-memory directory at `~/.claude/projects/[your-project]/memory/`. Files here persist across sessions.

Create a `MEMORY.md` in that directory:

```markdown
# Memory

## Active Projects
- [Project A]: [status, key contacts, next steps]
- [Project B]: [status, key contacts, next steps]

## Open Follow-ups
- [ ] Reply to Sarah about the proposal (due Friday)
- [ ] Send deck to investor group (no deadline, but overdue)
- [ ] Schedule Q2 planning with team

## Decisions Made
- 2024-01-15: Decided to focus on B2B over B2C for Q1
- 2024-01-10: Chose Stripe over Square for payments
```

**Key principle:** Memory files should be updated by Claude during sessions, not just by you. Tell Claude: "Update MEMORY.md with what we decided today." Make it part of the workflow.

**What you'll notice:** Sessions stop with "where were we?" Claude opens with "Last time we decided X, and you still need to follow up on Y."

---

## Phase 3: The Morning Briefing (Week 2 — 1 hour)

### Start with manual, then automate

Before writing any code, do it manually for a few days. Start each Claude session with:

```
Here's my calendar for today: [paste it]
Here's my task list: [paste it]

Give me a morning briefing: what's on my plate, what's most important,
and what I should tackle first given my schedule.
```

After a few days, you'll know exactly what you want in the briefing. Then ask Claude to build it:

```
Build me a Python script that:
1. Reads my Google Calendar for today
2. Checks my follow-ups file for anything overdue
3. Generates a morning briefing with priorities

Use the Google Calendar API. I'll set up credentials.
```

See [examples/scripts/briefing.py](examples/scripts/briefing.py) for a starter template.

**What you'll notice:** You stop starting the day in reactive mode. The briefing tells you what matters before your inbox does.

---

## Phase 4: Meeting Processing (Month 1 — 2 hours)

### Extract value from conversations automatically

If you use a meeting transcription tool (Granola, Otter, Fireflies, etc.), you're sitting on a goldmine of unprocessed context. Ask Claude to build a pipeline that:

1. Fetches new transcripts
2. Extracts facts, commitments, and follow-ups
3. Stores them in your knowledge store

```
Build me a script that:
1. Reads meeting transcripts from [source]
2. For each transcript, extracts:
   - Key facts (who said what, decisions made)
   - Follow-up items (who committed to what, by when)
   - Relationship notes (new contacts, role changes)
3. Appends facts to facts.jsonl
4. Adds follow-ups to follow-ups.md
```

See [examples/scripts/meeting_processor.py](examples/scripts/meeting_processor.py) for the pattern.

**What you'll notice:** Three weeks in, Claude casually mentions "Sarah mentioned she's exploring Series A in your call on the 12th — want to follow up?" That's the compound effect.

---

## Phase 5: Background Automation (Month 2 — 1 hour)

### Schedule scripts to run without you

Take your working scripts and schedule them:

**macOS (launchd):**
```bash
# Create a plist file for each scheduled job
# See architecture.md for full examples

# Load it
launchctl load ~/Library/LaunchAgents/com.chiefofstaff.meeting-sync.plist

# Verify it's running
launchctl list | grep chiefofstaff
```

**Linux (cron):**
```bash
crontab -e

# Add your jobs
0 * * * * /usr/bin/python3 ~/Scripts/meeting_sync.py
0 7 * * * /usr/bin/python3 ~/Scripts/briefing.py
0 9 * * 1 /usr/bin/python3 ~/Scripts/weekly_reminder.py
```

**What you'll notice:** Things happen without you asking. Meetings get processed overnight. Your briefing is ready before you open your laptop. Follow-ups surface before they're overdue.

---

## Phase 6: Session Hooks (Month 2 — 30 minutes)

### Make Claude Code self-aware

Add hooks in `~/.claude/settings.json` so Claude automatically gets context at session start and saves context at session end:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "command": "python3 ~/Scripts/briefing.py",
        "timeout": 30
      }
    ],
    "SessionEnd": [
      {
        "command": "python3 ~/Scripts/session_export.py",
        "timeout": 15
      }
    ]
  }
}
```

Now every session opens with a briefing and closes with a record of what happened.

---

## Phase 7: The Full Stack (Month 3+)

### Everything connects

At this point, you have:
- **CLAUDE.md** telling Claude who you are and how you work
- **Memory files** tracking context across sessions
- **Morning briefings** generated automatically
- **Meeting processing** extracting facts and follow-ups in the background
- **Scheduled jobs** keeping everything current
- **Session hooks** ensuring every conversation is informed and recorded

Now you can add:
- **Content pipelines** — ideas → outlines → drafts → published
- **Analytics dashboards** — platform metrics pulled and summarized weekly
- **Network management** — relationship cadence tracking and reconnection nudges
- **MCP connectors** — direct integrations with email, calendar, Slack, databases

Each addition compounds on the foundation. The briefing gets richer. The follow-ups get smarter. The drafts get more informed.

---

## Common Mistakes

1. **Building it all at once.** The system works because each layer is proven before the next one is added. Resist the urge to scaffold the whole thing in a weekend.

2. **Neglecting CLAUDE.md.** It's the foundation. If Claude keeps getting things wrong, the fix is almost always a CLAUDE.md update, not a better prompt.

3. **Automating before you understand.** Do things manually for a few days before scripting them. You need to know what "good" looks like before you can automate it.

4. **Treating memory as a dump.** Memory files should be curated, not appended to forever. Periodically review and prune. Outdated context is worse than no context.

5. **Skipping the follow-up tracker.** This is the unglamorous workhorse of the system. Most of the value comes from "you said you'd do X and it's been 5 days" — not from fancy dashboards.
