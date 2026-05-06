# Memory System

How to give Claude Code persistent memory across sessions — from simple markdown files to a full SQLite knowledge base with semantic search.

## The Problem

Claude Code starts every session blank. Close the terminal and everything is gone. For a chief of staff that needs to remember your last 50 meetings, track 30 open commitments, and know that "Sarah" means your cofounder (not the client's Sarah) — this is a dealbreaker.

The memory system solves this with three layers:

```
Layer 1: Markdown Memory Files
  → Simple, human-readable, always available
  → CLAUDE.md + memory/ directory

Layer 2: SQLite Database (memory.db)
  → Structured facts with provenance and confidence
  → Full-text search, categories, time decay
  → CLI tool for quick add/retrieve

Layer 3: Semantic Search
  → "What did we discuss about pricing?"
  → Finds context even without exact keywords
  → QMD or embedding-based search
```

## Layer 1: Markdown Memory Files

The simplest layer. Create a `memory/` directory in your project and add structured markdown files:

```
memory/
├── profile.md              # Who you are, how you work, key people
├── active-projects.md      # Current work streams and status
├── people-to-track.md      # Network, relationships, context
├── content-pipeline.md     # Ideas → drafts → published
└── decisions-log.md        # Key decisions with rationale
```

Claude reads these at session start. Update them during sessions. They persist because they're just files on disk.

**Key principle:** Memory files should be updated by Claude during sessions, not just by you. Tell Claude: "Update the decisions log with what we decided today."

## Layer 2: SQLite Memory Database

For anything beyond simple notes, use a structured database. A single `memory.db` file with these core tables:

```sql
CREATE TABLE facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,              -- "Series A target is $5M"
    source TEXT,                         -- "call with Sarah, 2026-01-15"
    category TEXT DEFAULT 'general',     -- work, ideas, network, content, scouting
    confidence REAL DEFAULT 0.8,         -- Degrades over time
    provenance TEXT,                     -- How it was captured
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP                 -- Some facts have a shelf life
);

-- Full-text search (this is what makes retrieval fast)
CREATE VIRTUAL TABLE facts_fts USING fts5(content, source, category);

-- Milestones: wins and completions worth celebrating
CREATE TABLE milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge profile: what you know and care about
CREATE TABLE knowledge_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL,
    level TEXT,                          -- novice, intermediate, expert
    interests TEXT,                       -- Specific sub-topics
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### The CLI Wrapper (memory.py)

Build a CLI tool that Claude can call directly:

```bash
# Add a fact
python3 ~/Scripts/memory.py add "An indie founder argues agent-native economy will rebuild every SaaS category" \
  --source "twitter-thread-2026-03-01" \
  --category ideas \
  --confidence 0.9

# Search memory
python3 ~/Scripts/memory.py retrieve "agent economy"

# Get session context (injected at session start)
python3 ~/Scripts/memory.py context

# Knowledge profile
python3 ~/Scripts/memory.py knowledge

# Stats
python3 ~/Scripts/memory.py stats
```

The `context` command is the key integration point — it outputs a summary of recent facts, open follow-ups, and relevant context that gets injected into the session start hook.

### Fact Quality Rules

Not all facts are equal. Quality rules prevent the database from becoming noise:

- **Confidence scoring**: Facts from direct conversation get 0.9+. Facts from forwarded articles get 0.7-0.8. Inferred facts get 0.5-0.6.
- **Time decay**: Confidence degrades over time. A fact from 6 months ago is less reliable than one from yesterday.
- **Atomic facts**: One idea per fact. "Sarah is exploring Series A and also mentioned she's hiring a CTO" is two facts, not one.
- **Attribution**: Always capture who said it, when, and where. Facts without provenance are hard to trust later.

## Memory Extraction Protocol

When information arrives via messaging (iMessage, Discord, Telegram), extract facts in real-time. Images and screenshots get deleted from staging — extract during the session or lose it.

### What to Extract (1-3 facts per message)

| Input Type | Category | Example Extraction |
|-----------|----------|-------------------|
| Article links/threads | ideas | Key thesis + author |
| Screenshots of people/companies | network | Name + role + relevance |
| Work updates | work | Status change + context |
| Content ideas | content | Hook + angle + platform |
| AI/agent architecture content | scouting | Technique + who built it |

### How to Extract Well

Good extraction captures the thesis with attribution:

```
✅ "An indie founder argues agent-native economy will rebuild every SaaS
   category for machine-to-machine"

❌ "Saw a thread on agent-native economy"
```

The first is a searchable, reusable fact. The second tells you nothing without going back to the original.

### Background Extraction

Configure Claude to extract silently — respond to the message conversationally first, then run the memory add command without announcing it. Memory extraction is infrastructure, not conversation.

## Effort Tracking

The memory system can also track how you work — not just what you know:

```
When user starts a task:
  → Log the start time

When user returns:
  → Calculate elapsed time
  → Every 3rd task: "How'd that feel? Harder or easier than expected?"

Over time:
  → Refine time estimates (what you think takes 2 min but actually takes 20)
  → Identify avoidance patterns
```

### Avoidance Pattern Diagnosis

Track which tasks sit longest. Diagnose the root:

| Pattern | Signal | Root Cause |
|---------|--------|-----------|
| **Head** | "I don't know where to start" | Strategic uncertainty — unclear direction |
| **Heart** | Keeps postponing despite knowing how | Emotional charge — anxiety, conflict, vulnerability |
| **Hand** | "I need to figure out how to..." | Capability gap — needs help or tooling |

Different roots need different interventions. Head problems need clarity, not motivation. Heart problems need acknowledgment, not task breakdowns. Hand problems need pairing or delegation, not deadlines.

## Layer 3: Semantic Search

Full-text search finds exact matches. Semantic search finds *related* context — things that are conceptually connected but use different words.

### QMD (Quick Markdown Search)

[QMD](https://github.com/jasonjmcghee/qmd) indexes your files and provides semantic search:

```bash
# Search across vault, memory, sessions
qmd search "pricing strategy for enterprise" -n 5

# List indexed collections
qmd collection list

# Re-index after adding new files
qmd update
```

### Hybrid Search Strategy

Best results come from combining both:

```
Query: "What's the status of the product launch?"

Keyword (FTS5) results:
  → "Product launch date moved to March 15"
  → "Launch checklist reviewed in Monday standup"

Semantic results:
  → "Marketing assets need final approval before go-live"
  → "Beta feedback summary — 3 blockers remaining"

Combined → Full picture
```

**Rule of thumb**: Use semantic search first for broad context, keyword search second for specific facts. QMD for exploration, FTS5 for precision.

## Integration Points

The memory system connects to everything else:

| System | How It Uses Memory |
|--------|-------------------|
| Morning briefing | Reads recent facts, overdue follow-ups, context |
| Meeting processing | Writes extracted facts, commitments, relationship notes |
| Content scout | Writes signals, reads knowledge profile for relevance scoring |
| Reading system | Reads interests for recommendation scoring |
| Discord/messaging | Writes real-time extractions from conversations |
| Session hooks | Reads at start (context injection), writes at end (session export) |

## Getting Started

1. **Day 1**: Create `memory/` directory with a profile and active projects file
2. **Week 1**: Build `memory.py` CLI (ask Claude to build it based on the schema above)
3. **Week 2**: Add memory extraction to your messaging workflow
4. **Month 1**: Add semantic search layer (QMD or embeddings)
5. **Ongoing**: The system gets smarter as facts accumulate — review and prune monthly
