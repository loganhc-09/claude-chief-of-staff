# Claude Code Chief of Staff

How I turned Claude Code into a persistent AI chief of staff — the full architecture, from CLAUDE.md to scheduled background scripts.

Built with Claude Code by [@loganinthefuture](https://www.tiktok.com/@loganinthefuture)

## What This Is

Most people use Claude Code for one-shot tasks. Write this email. Fix this bug. Explain this code. That's useful — but it's like hiring a brilliant contractor and only giving them 15-minute jobs.

This repo is the architecture for something different: a **persistent operational layer** that remembers your context, runs in the background, and compounds over time. Morning briefings generated before you wake up. Meeting transcripts processed into facts and follow-ups overnight. Commitments tracked and surfaced when they're overdue.

It's the difference between "I use AI sometimes" and "AI is part of how I operate."

## Architecture Overview

```
DATA SOURCES
  Calendar · Email · Meeting Transcripts · Analytics · Notes
                          ↓
SCHEDULING LAYER
  launchd/cron jobs · Session hooks · Reminder scripts
                          ↓
PROCESSING
  Transcript extraction · Email triage · Briefing generation
  Follow-up tracking · Content pipeline · Data analysis
                          ↓
KNOWLEDGE STORE
  Facts database · Follow-up queue · Decision log
  Meeting archive · Position documents · Network map
                          ↓
OUTPUTS
  Morning briefings · Draft messages · Reminders
  Content drafts · Dashboard updates · Research summaries
```

See **[architecture.md](architecture.md)** for the full system diagram, data flows, memory layout, and scheduling config.

## The Three Work Tiers

The key design decision: not everything needs human involvement at every step.

**Tier 1 — Claude owns entirely:** Process transcripts, sync data, generate briefings, flag overdue items.

**Tier 2 — Claude preps, you decide:** Draft replies for you to review. Triage inbox for you to prioritize. Surface follow-ups for you to act on.

**Tier 3 — Human only:** Send messages, publish content, make judgment calls, strategic decisions.

Most AI setups try to do everything or nothing. This one is explicit about the handoff points.

## What's In Here

| File | What It Is |
|------|-----------|
| [architecture.md](architecture.md) | Full system diagram, data flows, memory layout, scheduling |
| [getting-started.md](getting-started.md) | Progressive build guide — Day 1 to Month 3+ |
| [examples/CLAUDE.md](examples/CLAUDE.md) | Template for your own chief of staff config |
| [examples/scripts/briefing.py](examples/scripts/briefing.py) | Morning briefing generator |
| [examples/scripts/meeting_processor.py](examples/scripts/meeting_processor.py) | Transcript → facts + follow-ups pipeline |

## Getting Started

You don't build this in a weekend. You build it one layer at a time.

1. **Day 1:** Create your CLAUDE.md (10 minutes)
2. **Week 1:** Add memory files for persistence across sessions
3. **Week 2:** Morning briefing routine (manual first, then scripted)
4. **Month 1:** Scheduled scripts running in the background
5. **Month 2+:** The full stack — everything connected

See **[getting-started.md](getting-started.md)** for the full walkthrough.

## Design Principles

- **Clarity beats code.** The bottleneck is never technical — it's knowing what you want.
- **Progressive complexity.** Each layer works on its own before you add the next one.
- **Close loops, don't open them.** Every automation should end with a verifiable outcome.
- **Human-in-the-loop by design.** Prep is automated. Decisions are not.
- **Memory is architecture.** If the AI doesn't remember yesterday, it can't help with tomorrow.

## About

Made by [Logan Currie](https://logancurrie.com) with Claude Code.

Part of my series on building personal AI operating systems — [Captain's Log on Substack](https://loganinthefuture.substack.com/).

## License

MIT — use it, adapt it, build on it.
