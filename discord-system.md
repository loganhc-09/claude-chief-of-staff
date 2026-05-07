# Discord System

How to turn a Discord server into a two-way interface for your AI chief of staff — messaging, approval gates, memory mining, and fact extraction.

## Why Discord?

Most AI chief of staff setups are terminal-only. You open Claude Code, do work, close it. But the best chiefs of staff are reachable — you can message them from your phone, forward them context, and get things done without opening a laptop.

Discord works well for this because:

- **Always-on bot** via WebSocket (no HTTP server or tunnel needed)
- **Channels as workflows** — separate spaces for briefings, approvals, content, etc.
- **Reactions as input** — approve/reject/edit with emoji
- **Mobile-first** — message your AI from anywhere
- **Rich formatting** — code blocks, embeds, threads
- **Free** — no per-message costs

## Architecture

```
Discord Server
├── #briefing          ← Morning briefings posted here
├── #approvals         ← Content drafts waiting for ✅/❌
├── #content           ← Approved content ready to publish
├── #general           ← Open conversation with Claude
└── #logs              ← System events, errors, audit trail

Discord Bot (discord_bot.py)
  ├── Listens for DMs and channel messages
  ├── Routes to Claude Code CLI (--project-dir for full CLAUDE.md context)
  ├── Handles approval reactions (✅ → route to target, ❌ → drop)
  └── Runs as launchd service (always on)

Supporting Scripts
  ├── discord_send.py      → Fire-and-forget message sending
  ├── discord_approve.py   → Post to #approvals with reaction gates
  ├── discord_memory.py    → Query layer on Discord message history
  └── extract_discord_facts.py → Mine conversations for facts
```

## The Bot (discord_bot.py)

The core bot connects to Discord's gateway WebSocket and routes messages to Claude Code:

### Key Features

- **Authorized user only** — only responds to your Discord user ID
- **Project directory context** — runs Claude Code with `--project-dir` so it has full CLAUDE.md, memory files, and tool access
- **Audit logging** — every interaction logged to `~/.discord-bot/audit.log`
- **Channel routing** — different behavior per channel

### Setup

```bash
# 1. Create a Discord bot at https://discord.com/developers/applications
# 2. Enable Message Content Intent
# 3. Invite to your server with appropriate permissions

# 4. Create .env.discord in your scripts directory
cat > ~/Scripts/.env.discord << 'EOF'
DISCORD_TOKEN=your_bot_token
AUTHORIZED_USER_ID=your_discord_user_id
GUILD_ID=your_server_id
PROJECT_DIR=/Users/you/your-project
CHANNEL_APPROVALS=approval_channel_id
EOF

# 5. Install dependencies
pip install discord.py python-dotenv

# 6. Test it
python3 ~/Scripts/discord_bot.py
```

### Keep It Running (launchd)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.chiefofstaff.discord-bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/you/Scripts/discord_bot.py</string>
    </array>
    <key>KeepAlive</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>10</integer>
    <key>StandardOutPath</key>
    <string>/Users/you/.discord-bot/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/you/.discord-bot/launchd.log</string>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.chiefofstaff.discord-bot.plist
```

## Sending Messages (discord_send.py)

A lightweight utility for fire-and-forget messaging — used by cron jobs, scripts, and other tools:

```bash
# DM yourself
python3 ~/Scripts/discord_send.py "Meeting with Sarah in 30 minutes"

# Post to a channel
python3 ~/Scripts/discord_send.py --channel briefing "☀️ Morning briefing ready"

# Pipe content
cat briefing.md | python3 ~/Scripts/discord_send.py --stdin --channel briefing
```

This is the output layer for your overnight pipeline. Briefing generated at 6am → posted to #briefing → you read it on your phone over coffee.

## Approval Gates (discord_approve.py)

The approval system creates a human-in-the-loop checkpoint for outbound content. Cron jobs and background agents draft content, but nothing goes out without your explicit approval.

### How It Works

```
Background agent generates a LinkedIn draft
    ↓
discord_approve.py posts preview to #approvals
    ↓
You see it on your phone:
  ┌─────────────────────────────────────┐
  │ 📋 LinkedIn Draft                   │
  │                                     │
  │ [preview of the post]               │
  │                                     │
  │ React: ✅ approve | ❌ reject | ✏️ edit │
  └─────────────────────────────────────┘
    ↓
✅ → Post routed to #content (or published directly)
❌ → Dropped, logged
✏️ → Note posted that you'll edit manually
```

### Usage

```bash
# Submit content for approval
python3 ~/Scripts/discord_approve.py \
  --target content \
  --label "LinkedIn Draft" \
  "Here's the draft post text..."

# From a pipe (cron jobs)
python3 ~/Scripts/discord_approve.py \
  --target content \
  --label "TikTok Script" \
  --stdin < script.txt

# With custom timeout
python3 ~/Scripts/discord_approve.py \
  --target content \
  --label "Tweet" \
  --timeout 3600 \
  "draft tweet text"
```

### Why This Matters

This is the Tier 2 handoff point from the [architecture](architecture.md). Claude preps, you decide. Without approval gates, you either:
- Don't automate content (too risky) → miss the compound effect
- Automate without review (too dangerous) → publish garbage

Approval gates give you the best of both: AI does the heavy lifting, you make the call with a single emoji tap.

## Discord Memory (discord_memory.py)

Your Discord conversations contain valuable context — decisions, commitments, content ideas, relationship signals. The memory layer makes this searchable:

```bash
# Full-text search across all Discord messages
python3 ~/Scripts/discord_memory.py search "podcast guest list"

# Recent messages from a specific channel
python3 ~/Scripts/discord_memory.py channel content 7

# Episode/project prep — pull cross-source context
python3 ~/Scripts/discord_memory.py context "product launch" 14

# Open commitments from recent conversations
python3 ~/Scripts/discord_memory.py commitments 7

# Cross-reference a date or topic across calendar, email, and Discord
python3 ~/Scripts/discord_memory.py cross-ref "april 15"
```

### Data Source: Discrawl

Discord message history is synced to a local SQLite database using [Discrawl](https://github.com/steipete/discrawl) or a similar Discord archiver:

```
~/.discrawl/discrawl.db
├── messages     → All message content with timestamps
├── channels     → Channel metadata
├── members      → User info and display names
└── message_fts  → Full-text search index
```

### Cross-Referencing

The real power is cross-referencing Discord context with your other data sources:

```
"What happened around April 15?"

Discord:   Logan discussed Q2 content calendar in #content
Calendar:  Meeting with Sarah at 2pm, team standup at 10am
Email:     Invoice from contractor, newsletter draft review
Memory:    Decided to pivot TikTok strategy to long-form
```

This gives your AI chief of staff a complete picture when prepping for meetings or follow-ups.

## Fact Extraction (extract_discord_facts.py)

Conversations contain latent knowledge. The extraction script mines Discord history for facts worth persisting to the memory database:

### What It Extracts

| Pattern | Category | Example |
|---------|----------|---------|
| Decisions | work | "Going with Stripe over Square for payments" |
| Commitments | follow-up | "I'll send the deck by Friday" |
| Insights | ideas | "The real blocker is trust, not technology" |
| Content ideas | content | "Could be a good TikTok hook: 'Every SaaS category...'" |

### How It Works

```bash
# Extract from today's messages
python3 ~/Scripts/extract_discord_facts.py

# Last 3 days
python3 ~/Scripts/extract_discord_facts.py --days 3

# Preview without writing to DB
python3 ~/Scripts/extract_discord_facts.py --dry-run
```

The script runs as part of the overnight prep pipeline, ensuring that Discord conversations are captured before the next morning's briefing.

### Extraction Rules

- Minimum message length of ~40 characters (skip "ok", "got it", "lol")
- Pattern matching for decisions, commitments, insights, and content ideas
- Skip bot messages and system messages
- Facts are deduplicated against existing memory entries
- Each fact gets source attribution: `discord-#channel-YYYY-MM-DD`

## Channel Design

How you structure your Discord server matters. Here's a practical layout:

| Channel | Purpose | Who Posts |
|---------|---------|----------|
| `#general` | Open conversation with Claude | You + Bot |
| `#briefing` | Morning briefings, daily summaries | Bot (automated) |
| `#approvals` | Content/action approval queue | Bot (automated) |
| `#content` | Approved content, drafts, ideas | Bot (approved items) |
| `#logs` | System events, errors, audit | Bot (automated) |
| `#reading` | Reading recommendations, discussions | Bot + You |

### Principle: Channels as Workflows

Each channel represents a *workflow state*, not a topic. Content moves through channels:

```
Idea generated → #general (discussion)
Draft created → #approvals (review)
Approved → #content (ready to publish)
```

This gives you a visual pipeline of what's in progress, what's waiting for you, and what's done.

## Integration with Chief of Staff

The Discord system plugs into the broader architecture:

```
Overnight Pipeline
  ├── content_scout.py → generates intelligence brief
  ├── briefing.py → generates morning briefing
  ├── extract_discord_facts.py → mines yesterday's conversations
  └── discord_send.py → posts briefing to #briefing

Morning (you check Discord on phone)
  ├── Read briefing in #briefing
  ├── Review approvals in #approvals (✅/❌)
  └── DM Claude with quick tasks

During Day
  ├── Message Claude via DM or #general
  ├── Claude has full CLAUDE.md context
  └── Results posted back to Discord

Evening
  ├── Content drafts posted to #approvals
  └── Overnight pipeline starts again
```

## Getting Started

1. **Day 1**: Create Discord server + bot. Get `discord_send.py` working.
2. **Week 1**: Set up `discord_bot.py` with basic Claude Code routing.
3. **Week 2**: Add approval gates (`discord_approve.py`) for content workflow.
4. **Month 1**: Add Discrawl sync + `discord_memory.py` for searchable history.
5. **Month 1**: Add `extract_discord_facts.py` to overnight pipeline.
6. **Month 2+**: Refine channel structure, add more automated workflows.

## Security Notes

- **Authorized user only**: The bot should *only* respond to your Discord user ID. No one else should be able to trigger Claude Code through your bot.
- **Audit everything**: Log every interaction, every approval, every command.
- **No credentials in messages**: Never send API keys, passwords, or tokens through Discord.
- **Bot token security**: Keep your `.env.discord` file out of version control.
