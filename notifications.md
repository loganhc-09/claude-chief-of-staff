# Notifications and Failure Handling

How the system reaches me, and how I find out when part of it breaks.

This replaced my old Discord setup in September 2026 ([archive](archive/)). The short version of why: I stopped opening Discord, and everything the system said there went unread.

---

## The problem this solves

A background system has two jobs that are easy to forget about:

1. **Getting the right thing in front of you.** Not everything. The right thing, somewhere you already look.
2. **Telling you when it's broken.** A scheduled job that fails where you can't see it is worse than no job, because you'll assume it's working.

I got both wrong for a while. Two stories:

- **The alert nobody read.** My watchdog noticed a weekly job had stopped running. It posted that alert every morning for 24 days straight. I never saw it. It was one line in a list of 5 to 8 items, and the other items had been sitting there for weeks. A recurring alert with a list that never changes turns into wallpaper.
- **The failure nobody reported.** In May I switched meeting-transcription tools. The step that kicked off meeting processing lived inside the old tool's sync script, and the new one never had it. Transcripts kept arriving. None of them got processed for five months, and nothing complained, because nothing was checking.

## Two lanes

Everything the system wants to tell me goes through one small script (`notify.py`) with two lanes:

| Lane | Channel | What goes here | Budget |
|------|---------|----------------|--------|
| **digest** | Email | The default. Briefings, weekly summaries, failure alerts, anything that can be batched. | No limit, but batch it |
| **urgent** | iMessage | Something dated in the next 48 hours with an unmet dependency, or an item that sat through two digests untouched. | ≤1 per day. If it fires more, the rule is broken |

Pick lanes you already check. For me that's my inbox and my texts. For you it might be Slack. The channel matters less than this rule: **the system only talks where you're already looking.**

Keep a third, silent lane too: an append-only log file. It's for grep, not for reading.

## Every job reports its own failures

Every scheduled script wraps its main function in one shared helper:

```python
from escalate import run_guarded

if __name__ == "__main__":
    run_guarded(main, "meeting-sync")
```

`run_guarded` catches any exception, sends a failure alert through the digest lane, and exits nonzero so the scheduler's logs see it too. Three rules make it safe to use everywhere:

- **It never raises.** If the alert itself fails, it falls back to stderr. A broken notification pipe can't take the job down with it.
- **It's rate-limited per script** (I use one alert per 6 hours), so a job that fails every 15 minutes doesn't flood you.
- **It's the easy path.** One import and one line. If the right thing takes effort, half your scripts won't do it.

## The staleness watchdog

Escalation catches crashes. It can't catch a job that never runs, because a job that never runs never raises. That needs a second check.

`staleness_watchdog.py` runs every morning and checks **outputs, not schedulers.** For each job it knows which file or database row that job should have updated, and how old that's allowed to get. Then it flags anything past its threshold.

It's built to catch the three ways a scheduled job dies:

1. **Quiet crash.** The job runs and fails. (Escalation usually catches this too. The watchdog is the backup.)
2. **Stopped firing.** The job is loaded but never runs, or runs and produces nothing. "Loaded" in `launchctl list` tells you nothing about this.
3. **Disable and forget.** You turn a job off "for now." The watchdog flags any disabled job older than 14 days, so every pause gets a decision: delete it or bring it back.

Two things I learned the hard way:

- **Wire the watchdog to the thing you actually read.** Mine originally posted to Discord while my session-start health check said "all systems healthy" for a month. Now the session-start check reads the watchdog's results directly.
- **Escalate by how stale, not by whether.** Anything stale past 2× its own threshold becomes a hard blocker at session start. Everything else stays a warning. If everything blocks, you learn to ignore the blocker.

## A check at the start of every session

The first thing every session runs is a short preflight script. It prints one line per subsystem: are the scheduled jobs loaded, did the watchdog pass, is email syncing, is the memory index under its size cap. Only a real problem blocks. Everything else is a warning.

It takes a few seconds and it's the reason I find problems in days instead of months.

## If you're building this

Start smaller than this:

1. Pick your one digest channel. Send yourself one test message from a script.
2. Write a 20-line `run_guarded` helper and use it in your first scheduled job.
3. When you have three or more jobs, add a watchdog that checks one output file per job.

You can ask Claude Code to build each of these from this page.
