#!/usr/bin/env python3
"""
Discord send utility — fire-and-forget messaging for cron jobs and scripts.

Usage:
    python3 discord_send.py "message"                     # DM yourself
    python3 discord_send.py --channel briefing "message"   # Post to #briefing
    python3 discord_send.py --stdin                        # Read from pipe
    echo "hello" | python3 discord_send.py --stdin --channel briefing

Environment (.env.discord):
    DISCORD_TOKEN=your_bot_token
    GUILD_ID=your_server_id
    AUTHORIZED_USER_ID=your_discord_user_id
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env.discord")

TOKEN = os.environ.get("DISCORD_TOKEN", "")
GUILD_ID = os.environ.get("GUILD_ID", "")
USER_ID = os.environ.get("AUTHORIZED_USER_ID", "")
API = "https://discord.com/api/v10"
MAX_LEN = 1900


def _req(method, path, data=None):
    """Make a Discord API request."""
    url = API + path
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "ChiefOfStaff-Discord/1.0",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers)
    req.method = method
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _chunk(text):
    """Split into Discord-safe chunks."""
    if len(text) <= MAX_LEN:
        return [text]
    chunks = []
    while text:
        if len(text) <= MAX_LEN:
            chunks.append(text)
            break
        idx = text.rfind("\n", 0, MAX_LEN)
        if idx == -1:
            idx = MAX_LEN
        chunks.append(text[:idx])
        text = text[idx:].lstrip("\n")
    return chunks


def send_dm(text):
    """Send a DM to the authorized user."""
    dm = _req("POST", "/users/@me/channels", {"recipient_id": USER_ID})
    for chunk in _chunk(text):
        _req("POST", f"/channels/{dm['id']}/messages", {"content": chunk})
    print(f"DM sent ({len(text)} chars)")


def send_channel(channel_name, text):
    """Send to a named channel in the guild."""
    channels = _req("GET", f"/guilds/{GUILD_ID}/channels")
    match = [c for c in channels if c["name"] == channel_name.lstrip("#")]
    if not match:
        print(f"Channel '{channel_name}' not found", file=sys.stderr)
        sys.exit(1)
    channel_id = match[0]["id"]
    for chunk in _chunk(text):
        _req("POST", f"/channels/{channel_id}/messages", {"content": chunk})
    print(f"Posted to #{channel_name} ({len(text)} chars)")


def main():
    parser = argparse.ArgumentParser(description="Send Discord messages")
    parser.add_argument("message", nargs="?", help="Message to send")
    parser.add_argument("--channel", help="Channel name (default: DM)")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    args = parser.parse_args()

    if args.stdin:
        text = sys.stdin.read().strip()
    elif args.message:
        text = args.message
    else:
        print("Provide a message or use --stdin", file=sys.stderr)
        sys.exit(1)

    if not text:
        print("Empty message", file=sys.stderr)
        sys.exit(1)

    if args.channel:
        send_channel(args.channel, text)
    else:
        send_dm(text)


if __name__ == "__main__":
    main()
