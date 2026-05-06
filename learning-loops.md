# Learning Loops

How to build feedback-driven learning systems that get smarter over time — from a curated reading pipeline to an automated content intelligence scout.

## The Idea

Most AI setups are static: you configure them once and they do the same thing forever. Learning loops are different — they observe what you engage with, adjust what they surface, and compound over time.

Three systems, each serving a different purpose:

```
Reading System (reading.py)
  → Curated articles/content ranked by your interests
  → Learns from your engagement: read, discussed, skipped
  → Gets better at predicting what you'll find valuable

Content Scout (content_scout.py)
  → Automated intelligence pipeline across YouTube + newsletters
  → AI extraction + novelty scoring + cross-source clustering
  → Surfaces signals you need to KNOW, not just read

Discussion Queue (memory/discussion-queue.md)
  → Topics worth riffing on, turning into content, or thinking about
  → Connects external signals to your intellectual threads
  → Bridges input (learning) and output (content creation)
```

---

## 1. Reading System

A daily reading list ranked by relevance, scored by quality, and trained by your feedback.

### Architecture

```
Sources (RSS, HN, newsletters, manual adds)
    ↓ collect (daily via launchd, 5am)
Raw items (deduplicated, scored)
    ↓ score (pillar relevance × source trust × recency × novelty)
Ranked queue (SQLite)
    ↓ surface (top pick, spin, suggest-by-time)
You read / discuss / skip
    ↓ feedback (logged to SQLite)
Preference model updates
    ↓ learn (adjusts source weights, pillar affinity)
Better recommendations tomorrow
```

### Key Commands

```bash
python3 ~/Scripts/reading.py collect              # Run all feeds, fill the queue
python3 ~/Scripts/reading.py top [--json]          # Today's #1 pick
python3 ~/Scripts/reading.py spin [--json]         # Random from top 10
python3 ~/Scripts/reading.py queue [--limit 10]    # Full ranked queue
python3 ~/Scripts/reading.py suggest --minutes 30  # Best fit for a time slot
python3 ~/Scripts/reading.py feedback <id> read|discussed|skipped [note]
python3 ~/Scripts/reading.py stats                 # Source scores, pillar weights
python3 ~/Scripts/reading.py learn                 # Recalculate preferences
python3 ~/Scripts/reading.py streak                # Reading streak
python3 ~/Scripts/reading.py add <url> --title "T" # Manually add a URL
```

### Conversational Integration

The reading system works best when integrated into conversation:

1. **User says "let's read"** → Surface #1 pick with a pitch (why this, why now)
2. **Discussion** → Talk through the article, connect it to existing threads
3. **"Spin"** → Random pick from top 10 for variety
4. **Feedback** → Log engagement, which trains the model

This turns reading from a passive backlog into an active learning session with a coach.

### Scoring Model

Each item gets a composite score from multiple signals:

| Signal | Weight | What It Measures |
|--------|--------|-----------------|
| Pillar relevance | High | How closely it maps to your intellectual threads |
| Source trust | Medium | Track record of this source (learned from feedback) |
| Recency | Medium | Newer content scores higher |
| Novelty | Medium | Does this say something you haven't seen before? |
| Engagement history | Low | Similar items you've engaged with |

The `learn` command recalculates weights based on your feedback history. Sources that consistently produce items you discuss get boosted. Sources you skip get downweighted. Over time, the queue reflects *your* taste, not a generic algorithm.

### POV Pillars

The system scores relevance against your defined intellectual threads (POV pillars). For example:

```python
POV_PILLARS = {
    "cognitive_surrender": {
        "keywords": ["deskilling", "automation complacency", "skill atrophy", ...],
    },
    "career_ip": {
        "keywords": ["data portability", "worker data", "portable equity", ...],
    },
    "context_engineering": {
        "keywords": ["prompt engineering", "RAG", "context window", ...],
    },
    # ... your intellectual threads
}
```

Items matching multiple pillars score higher — cross-cutting ideas are more valuable than single-thread ones.

### Feed Configuration

Managed via `~/.reading/config.json`:

```json
{
  "feeds": {
    "hn": {"enabled": true, "type": "hackernews", "min_score": 100},
    "stratechery": {"enabled": true, "type": "rss", "url": "https://..."},
    "one_useful_thing": {"enabled": true, "type": "rss", "url": "https://..."}
  },
  "collection_schedule": "daily",
  "max_queue_size": 50,
  "auto_learn_interval": 7
}
```

---

## 2. Content Scout

An automated intelligence pipeline that monitors external sources and surfaces novel signals — what you need to *know*, not just what's interesting to *read*.

### Architecture

```
Sources (15+ YouTube channels, 8+ newsletters)
    ↓ collect (5:15am daily via launchd)
Raw content (~/Vault/60-Memory/scout/raw/)
    ↓ extract (Haiku — key claims, novelty scoring)
Signals (SQLite: content_scout_signals)
    ↓ cluster (Sonnet — cross-source pattern matching)
Intelligence brief (~/Vault/60-Memory/scout/briefs/)
```

### Key Commands

```bash
python3 ~/Scripts/content_scout.py run                     # Full pipeline
python3 ~/Scripts/content_scout.py collect                  # Pull from feeds
python3 ~/Scripts/content_scout.py extract                  # AI extraction on new items
python3 ~/Scripts/content_scout.py cluster                  # Cross-source clustering
python3 ~/Scripts/content_scout.py brief [--days 3]         # Generate intelligence brief
python3 ~/Scripts/content_scout.py sources                  # Show configured sources
python3 ~/Scripts/content_scout.py stats                    # Collection stats
python3 ~/Scripts/content_scout.py add-channel <id> <name>  # Add YouTube channel
python3 ~/Scripts/content_scout.py add-newsletter <url>     # Add newsletter feed
python3 ~/Scripts/content_scout.py recent [--limit 10]      # Recent high-signal items
python3 ~/Scripts/content_scout.py search <query>           # Search signals
```

### The Extraction Filter

This is what makes the scout useful vs. just another RSS reader. Each item is evaluated by a fast model (Haiku) against five criteria:

| Criterion | Scale | What It Asks |
|-----------|-------|-------------|
| **Novelty** | 1-5 | Does this say something you don't already know? |
| **Demonstrated** | bool | Did someone build/do this, or just theorize? |
| **Contrarian** | bool | Does it challenge consensus? |
| **Thread connections** | list | Which of your intellectual threads does it touch? |
| **Summary** | text | Why it matters for your *learning*, not a content summary |

Items scoring <2 novelty are dropped before clustering. This is aggressive filtering — most content doesn't clear the bar, and that's the point.

### Cross-Source Clustering

The real power: Sonnet finds patterns across sources. Three different people talking about the same emerging idea from different angles? That's a signal worth paying attention to.

Clusters surface as cards in the intelligence brief:

```
🔥 CLUSTER: "Agent-native infrastructure" (novelty: 4.2)
├── [Indie founder thread]: agent economy rebuilds every SaaS category
├── [Academic paper]: market-based scaffolding for agent coordination
└── [VC podcast]: agent payments infrastructure
🛠️ Multiple sources demonstrating → high signal
```

### Scheduling

```xml
<!-- com.logan.content-scout.plist -->
<key>Label</key>
<string>com.logan.content-scout</string>
<key>ProgramArguments</key>
<array>
    <string>/usr/bin/python3</string>
    <string>/Users/you/Scripts/content_scout.py</string>
    <string>run</string>
</array>
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key><integer>5</integer>
    <key>Minute</key><integer>15</integer>
</dict>
```

### Reading vs. Scouting

| | Reading System | Content Scout |
|---|---|---|
| **Purpose** | Articles to read deeply | Signals to be aware of |
| **Input** | RSS feeds, HN, manual adds | YouTube channels, newsletters |
| **Output** | Ranked reading queue | Intelligence briefs with clusters |
| **Interaction** | "Let's read" → discuss → feedback | Morning briefing → skim → flag |
| **Learning** | Your engagement trains the model | Novelty scores calibrate to your knowledge |
| **Cadence** | Active reading sessions | Passive morning scan |

They complement each other. The scout tells you what's happening. The reading system goes deep on what matters.

---

## 3. Discussion Queue

A human-curated buffer between input (learning) and output (content creation). Not everything worth knowing is worth posting about. The discussion queue holds ideas that deserve more thought.

### Structure

```markdown
# Discussion Queue

## 1. Agent-Native Economy ([Indie founder thread])
**Source:** [Indie founder thread]
**Added:** 2026-03-01

> Key quote or thesis...

**Your relevance:** How this connects to your existing threads.

**Possible angles:**
- Substack: "Your agent is your next employee"
- TikTok: "Every SaaS category is about to get rebuilt"
- Discussion topic for community
```

### How Items Enter the Queue

- **From reading sessions**: "This is worth riffing on" → added to queue
- **From content scout**: High-novelty clusters → manually promoted
- **From conversations**: Discord/Slack discussions → extracted and queued
- **From original thinking**: Your own ideas that need development

### How Items Leave the Queue

- **Turned into content**: Becomes a Substack post, TikTok, or thread
- **Discussed**: Covered in a community session or podcast
- **Merged**: Combined with other queue items into a bigger piece
- **Archived**: Still interesting but no longer timely

### The Learning Loop Closed

```
Scout detects signal → Reading system surfaces related articles →
Discussion queue captures your angle → Content creation uses it →
Audience feedback informs your thinking → Updated POV pillars →
Scout recalibrates what "novel" means for you → ...
```

This is the compound effect. Each system feeds the next, and the whole thing gets sharper over time.

---

## Building Your Own

### Start Simple

1. **Week 1**: Create a discussion queue (just a markdown file)
2. **Week 2**: Build reading.py with basic RSS collection and manual scoring
3. **Month 1**: Add feedback loop (engagement tracking → preference learning)
4. **Month 1**: Build content scout with AI extraction
5. **Month 2**: Add cross-source clustering
6. **Month 3+**: Connect to briefing system, content pipeline, community

### Design Principles

- **Filter aggressively.** The value is in what you *don't* see. Most content doesn't clear the bar.
- **Learn from behavior, not preferences.** What you actually engage with matters more than what you say you're interested in.
- **Separate signals from reading.** Knowing about something (scout) is different from understanding it deeply (reading). Different cadences, different systems.
- **Keep the human in the loop.** The discussion queue is manually curated for a reason — not everything worth knowing is worth amplifying.
- **Compound over time.** The system should get measurably better month over month. If it's not, your feedback loop is broken.
