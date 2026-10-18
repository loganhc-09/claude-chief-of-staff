# Claude Code Chief of Staff

How I turned Claude Code into a persistent AI chief of staff: the full architecture, from CLAUDE.md to scheduled background scripts.

Built with Claude Code by [@loganinthefuture](https://www.tiktok.com/@loganinthefuture). **Last updated October 2026** ([what changed](CHANGELOG.md)).

---

## Install it as a plugin

The core of this is installable in one command. In Claude Code:

```
/plugin marketplace add loganhc-09/claude-chief-of-staff
/plugin install chief-of-staff@chief-of-staff
```

Restart Claude Code, then run `/chief-of-staff:setup`. It interviews you and scaffolds your own persistent memory + daily-brief system. No coding required. The plugin lives in [`plugins/chief-of-staff/`](plugins/chief-of-staff/), and everything it creates is plain Markdown on your machine.

---

## The Three Layers

Most people are already at Layers 1 and 2. The unlock is Layer 3.

**Layer 1: Knowledge (Vault).** A markdown vault Claude Code reads and writes. Start with the [`examples/CLAUDE.md`](examples/CLAUDE.md) template. That's the smallest viable version of this entire system, and it works the moment you drop it in a folder you `claude` from.

**Layer 2: Active (you + Claude Code).** Live work, live decisions. Already running if you have Claude Code installed.

**Layer 3: Autonomous (scheduled jobs on the same Mac).** Background scripts that pull email, calendar, and meeting transcripts, process them, and send me what matters. They run as `launchd` jobs on my one laptop. Results reach me by email, and the rare urgent thing comes as an iMessage. See [`architecture.md`](architecture.md) and [`notifications.md`](notifications.md).

> **What changed:** this used to say "an old laptop on my desk, posting to Discord." I retired the second machine in July and Discord in September, because I'd stopped looking at either. One machine and one inbox turned out to be the version I actually keep using. More in [what broke](#what-broke-and-what-i-changed).

**Cost:** I run on Claude Max ($200/month). Most of this works on Max 5x ($100/month) too. See [getting-started.md](getting-started.md#before-you-start-picking-your-plan-and-keeping-costs-down) for the plan breakdown and cost-reduction habits.

---

## What This Is

Most people use Claude Code for one-shot tasks. Write this email. Fix this bug. Explain this code. That's useful, but it's like hiring a brilliant contractor and only giving them 15-minute jobs.

This repo is the architecture for a **persistent operational layer** that remembers your context, runs in the background, and compounds over time. Morning briefings generated before you wake up. Meeting transcripts processed into facts and follow-ups overnight. Commitments tracked and surfaced when they're overdue.

## Architecture Overview

```
DATA SOURCES
  Calendar · Email · Meeting Transcripts · Analytics · Notes
  YouTube channels · Newsletters · RSS feeds
                          ↓
SCHEDULING LAYER
  launchd jobs (one Mac) · Session hooks · Content scout (daily)
  Staleness watchdog (checks every job is still producing)
                          ↓
PROCESSING
  Transcript extraction · Email triage · Briefing generation
  Follow-up tracking · Content pipeline · Data analysis
  Reading curation · Signal extraction · Cross-source clustering
                          ↓
KNOWLEDGE STORE
  SQLite memory (facts, knowledge profile, milestones)
  Semantic search (QMD) · Follow-up queue · Decision log
  Meeting archive · Position documents · Network map
  Reading preferences · Source trust scores · POV pillars
                          ↓
OUTPUTS
  Morning briefings · Draft messages · Reminders
  Content drafts · Intelligence briefs · Reading recommendations
  Email digest (default) · iMessage (urgent only, ≤1/day)
```

See **[architecture.md](architecture.md)** for the full system diagram, data flows, memory layout, and scheduling config.

## The Handoff Model

The key design decision: not everything needs human involvement at every step. Three modes of work, explicit about where AI hands off to you.

**Automated:** Process transcripts, sync data, generate briefings, flag overdue items. AI owns it.

**Approval-gated:** Draft replies for you to review. Triage inbox for you to prioritize. Surface follow-ups for you to act on. AI preps, you decide.

**Human only:** Send messages, publish content, make judgment calls, strategic decisions. Never automated.

Most AI setups try to do everything or nothing. This one is explicit about where the handoff happens.

## What Broke (and What I Changed)

I've been running this daily for almost a year. The architecture held up. Some of my assumptions didn't.

- **Alerts go where you already look.** My watchdog caught a dead job and posted about it 24 mornings in a row. I never saw it, because it was one line in a list that hadn't changed in weeks. Then I stopped opening Discord at all. Now there are two lanes: an email digest, and iMessage for the one thing a day (at most) that can't wait.
- **Silent failure is the default.** When I switched transcription tools in May, the trigger for meeting processing lived in the old tool's sync script. Nothing got processed for five months and nothing complained. Every scheduled job now reports its own failures, and a watchdog checks that each job is *producing*, not just loaded. → [notifications.md](notifications.md)
- **"Done" in the database isn't done.** One bad batch update marked about 250 tasks complete in six seconds. One of them was something I hadn't done. Before trusting a status, check one system downstream (the sent folder, the calendar, the transcript).
- **Measure your memory.** I assumed retrieval was fine for five months. When I finally benchmarked it, the right fact landed in the top 5 results less than half the time. Now that number is the baseline to beat. → [memory-system.md](memory-system.md)
- **It sprawls.** By September I had 199 scripts and 52 scheduled jobs, and a chunk of them were reporting to a channel nobody read. I paused or archived the dead weight. A smaller system you trust beats a big one you don't.
- **Keep personal context out of git.** Personal context files ended up inside a git-tracked folder once. Nothing went public, but now that material lives outside any repo by rule.

## What's In Here

### Core Architecture
| File | What It Is |
|------|-----------|
| [architecture.md](architecture.md) | Full system diagram, data flows, memory layout, scheduling |
| [getting-started.md](getting-started.md) | Progressive build guide, Day 1 to Month 3+ |
| [examples/CLAUDE.md](examples/CLAUDE.md) | Template for your own chief of staff config |
| [examples/scripts/briefing.py](examples/scripts/briefing.py) | Morning briefing generator |
| [examples/scripts/meeting_processor.py](examples/scripts/meeting_processor.py) | Transcript → facts + follow-ups pipeline |

### Deep Dives
| File | What It Is |
|------|-----------|
| [memory-system.md](memory-system.md) | SQLite memory database, extraction protocol, effort tracking, semantic search |
| [learning-loops.md](learning-loops.md) | Reading system, content scout, discussion queue: feedback-driven learning |
| [notifications.md](notifications.md) | **New.** Email + urgent lanes, failure escalation, the staleness watchdog |
| [CHANGELOG.md](CHANGELOG.md) | **New.** What changed and why |
| [archive/](archive/) | The retired Discord setup, kept for reference |

## Working Components

This repo is the architecture. Code for some of the pieces lives in standalone repos you can fork:

| Repo | What It Is | Where It Fits |
|------|-----------|---------------|
| [loop-closer](https://github.com/loganhc-09/loop-closer) | Brain dump in, swipeable task deck out. [Try it in the browser](https://loganhc-09.github.io/loop-closer/). | The "I can't start" moment. Works in Claude Code, Cursor, and claude.ai. |
| [task-tinder](https://github.com/loganhc-09/task-tinder) | Swipe-based task triage with metacognition capture | The approval-gated interface. You decide, the system learns your methods. |
| [reading-scout](https://github.com/loganhc-09/reading-scout) | Personal reading agent that learns from your conversations | The learning-loops layer. [More here](learning-loops.md). |

## Daily Surface

Most of the system runs in the background, but day-to-day I open a local web dashboard at `localhost:8091` (loopback only, bound to `127.0.0.1`, not exposed to your LAN). It's a small Python server that pulls from the SQLite memory and queue tables and renders task triage, overnight signals + reading, and a day-prep panel.

The full dashboard is custom to my workflow and not in this repo. The Task Tinder swipe UI is open source at [task-tinder](https://github.com/loganhc-09/task-tinder). Fork that, point it at your own task store, and you have the most-used surface.

## Getting Started

You don't build this in a weekend. You build it one layer at a time.

1. **Day 0:** Pick your plan + skim cost-reduction habits ([details](getting-started.md#before-you-start-picking-your-plan-and-keeping-costs-down)), 5 minutes
2. **Day 1:** Create your CLAUDE.md (10 minutes)
3. **Week 1:** Add memory files for persistence across sessions
4. **Week 2:** Morning briefing routine (manual first, then scripted)
5. **Month 1:** Scheduled scripts + SQLite memory database
6. **Month 2:** One notification lane you actually check + failure alerts
7. **Month 2:** Learning loops: reading system + content scout
8. **Month 3+:** The full stack, everything connected, and a regular pass to cut what you stopped using

See **[getting-started.md](getting-started.md)** for the full walkthrough.

## Design Principles

- **Clarity beats code.** The bottleneck is never technical. It's knowing what you want.
- **Progressive complexity.** Each layer works on its own before you add the next one.
- **Close loops, don't open them.** Every automation should end with a verifiable outcome.
- **Human-in-the-loop by design.** Prep is automated. Decisions are not.
- **Memory is architecture.** If the AI doesn't remember yesterday, it can't help with tomorrow.
- **Verify or it didn't happen.** A job that's loaded isn't a job that's working. A task marked done isn't a task that got done.
- **Filter aggressively.** The value is in what you *don't* see. Most content doesn't clear the bar.

## About

Made by [Logan Currie](https://logancurrie.com) with Claude Code. I write about building with AI on [Substack](https://loganinthefuture.substack.com/).

## License

MIT. Use it, adapt it, build on it.
