# Changelog

## October 2026

The docs had drifted from how I actually run this. This update brings them back in line.

- **Retired Discord.** All Discord docs and scripts moved to [archive/](archive/). Output now reaches me by email digest, with iMessage only for the rare urgent item.
- **One machine.** Layer 3 runs as launchd jobs on my main Mac. The "old laptop on my desk" is retired.
- **New: [notifications.md](notifications.md).** Two notification lanes, failure escalation, and the staleness watchdog that checks every job is still producing.
- **New: "What broke" in the README.** Six lessons from almost a year of daily use.
- **Scheduling tips** in [architecture.md](architecture.md): route every job through one wrapper script, and why a Python upgrade can break macOS permissions for scheduled jobs without telling you.
- **getting-started.md:** two habits to adopt before scheduling anything, three new common mistakes.
- **Working Components:** added [loop-closer](https://github.com/loganhc-09/loop-closer).
- Meeting transcription examples now list Quill (what I switched to in May 2026).

## July 2026

- **Installable plugin.** `/plugin marketplace add loganhc-09/claude-chief-of-staff`, then `/chief-of-staff:setup` interviews you and scaffolds your own memory + daily-brief system.

## May 2026

- The Handoff Model (renamed from "three work tiers"), cost guidance, a References section, and hardening of the example scripts against prompt injection.

## March 2026

- Initial release: architecture, getting-started guide, memory system, learning loops, Discord system.
