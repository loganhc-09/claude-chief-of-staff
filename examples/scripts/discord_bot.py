#!/usr/bin/env python3
"""
Discord Bot — Claude Code CLI orchestration layer.

Listens for DMs and channel messages via Discord gateway WebSocket,
routes them to Claude Code CLI with full CLAUDE.md context.
No HTTP server or tunnel required.

Requirements:
    pip install discord.py python-dotenv

Setup:
    1. Create bot at https://discord.com/developers/applications
    2. Enable Message Content Intent
    3. Create .env.discord with your tokens (see below)
    4. Run: python3 discord_bot.py

Environment (.env.discord):
    DISCORD_TOKEN=your_bot_token
    AUTHORIZED_USER_ID=your_discord_user_id
    GUILD_ID=your_server_id
    PROJECT_DIR=/path/to/your/project
    CHANNEL_APPROVALS=approval_channel_id
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv(Path(__file__).parent / ".env.discord")

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")
AUTHORIZED_USER_ID = os.environ.get("AUTHORIZED_USER_ID", "")
GUILD_ID = os.environ.get("GUILD_ID", "")
PROJECT_DIR = os.environ.get("PROJECT_DIR", str(Path.home() / "Desktop" / "Claude Code"))

# Logging
LOG_DIR = Path.home() / ".discord-bot"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("discord_bot")

# Audit log
AUDIT_LOG = LOG_DIR / "audit.log"

# ---------------------------------------------------------------------------
# Bot setup
# ---------------------------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)


def audit(action: str, detail: str = ""):
    """Append to audit log."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(AUDIT_LOG, "a") as f:
        f.write(f"{ts} | {action} | {detail}\n")


def is_authorized(user_id: int) -> bool:
    """Only respond to the authorized user."""
    return str(user_id) == AUTHORIZED_USER_ID


async def run_claude(prompt: str, timeout: int = 120) -> str:
    """Run Claude Code CLI with project context and return the response."""
    cmd = [
        "claude",
        "--print",
        "--project-dir", PROJECT_DIR,
        prompt,
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
        result = stdout.decode("utf-8", errors="replace").strip()
        if not result and stderr:
            result = f"[Error] {stderr.decode('utf-8', errors='replace')[:500]}"
        return result or "[No response from Claude]"
    except asyncio.TimeoutError:
        return "[Timeout — Claude took too long to respond]"
    except Exception as e:
        return f"[Error running Claude: {e}]"


def chunk_message(text: str, limit: int = 1900) -> list[str]:
    """Split text into Discord-safe chunks."""
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        # Try to break at newline
        idx = text.rfind("\n", 0, limit)
        if idx == -1:
            idx = limit
        chunks.append(text[:idx])
        text = text[idx:].lstrip("\n")
    return chunks


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------
@bot.event
async def on_ready():
    logger.info(f"Bot connected as {bot.user}")
    audit("CONNECTED", f"Bot ready: {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    # Ignore own messages
    if message.author == bot.user:
        return

    # Authorization check
    if not is_authorized(message.author.id):
        return

    # Skip bot commands prefix
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    # Log the interaction
    channel_name = getattr(message.channel, "name", "DM")
    audit("MESSAGE", f"#{channel_name}: {message.content[:100]}")

    # Show typing indicator while Claude thinks
    async with message.channel.typing():
        response = await run_claude(message.content)

    # Send response in chunks
    for chunk in chunk_message(response):
        await message.channel.send(chunk)

    audit("RESPONSE", f"#{channel_name}: {response[:100]}")


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    """Handle approval reactions on bot messages."""
    if not is_authorized(user.id):
        return
    if reaction.message.author != bot.user:
        return

    emoji = str(reaction.emoji)

    # Check if this is an approval message (has the approval embed marker)
    if not reaction.message.embeds:
        return

    embed = reaction.message.embeds[0]
    if not embed.footer or "approval-id:" not in (embed.footer.text or ""):
        return

    if emoji == "✅":
        audit("APPROVED", f"Message {reaction.message.id}")
        await reaction.message.channel.send("✅ Approved — routing to target channel.")
        # TODO: Route to target channel based on approval metadata
    elif emoji == "❌":
        audit("REJECTED", f"Message {reaction.message.id}")
        await reaction.message.channel.send("❌ Rejected — dropped.")
    elif emoji == "✏️":
        audit("EDIT_REQUESTED", f"Message {reaction.message.id}")
        await reaction.message.channel.send("✏️ Noted — you'll edit manually.")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("ERROR: Set DISCORD_TOKEN in .env.discord", file=sys.stderr)
        sys.exit(1)
    if not AUTHORIZED_USER_ID:
        print("ERROR: Set AUTHORIZED_USER_ID in .env.discord", file=sys.stderr)
        sys.exit(1)

    bot.run(DISCORD_TOKEN)
