# Archive

Things I used to run and don't anymore. Kept here because people still link to them, and because the patterns might fit your setup even though they stopped fitting mine.

## Discord (retired September 2026)

From March to September 2026 a Discord server was my mobile interface to the system: an always-on bot, an approvals channel for drafts, and an overnight job that mined conversations for facts.

**Why I retired it:** I stopped opening Discord. By early September the bot hadn't handled a message from me in two weeks, and the alerts it posted went unseen. A two-way interface only works if you actually look at it.

**What replaced it:** an email digest, plus iMessage for the rare urgent thing. See [notifications.md](../notifications.md).

**What's here:**
- [discord-system.md](discord-system.md): the original guide (bot, channel design, approval gates, fact extraction)
- [scripts/discord_bot.py](scripts/discord_bot.py) and [scripts/discord_send.py](scripts/discord_send.py): the example scripts

**If you want to try it anyway:** it works fine as a pattern. The security notes in [SECURITY.md](../SECURITY.md) still apply. Treat the bot token like shell access.

## The second machine (retired July 2026)

Layer 3 used to run on an old laptop on my desk, so the scheduled jobs never slept. I retired it in July and moved the jobs worth keeping onto my main Mac. One machine meant one place to debug, one set of permissions, and one fewer thing to keep in sync.
