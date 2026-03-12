"""
Morning Briefing Generator
===========================
Generates a daily briefing with calendar events, priority tasks,
and overdue follow-ups.

This is a starter template — adapt it to your data sources and preferences.

Requirements:
    pip install google-auth google-auth-oauthlib google-api-python-client

Setup:
    1. Create a Google Cloud project with Calendar API enabled
    2. Download OAuth credentials to ~/.credentials/google_credentials.json
    3. Run once manually to complete the OAuth flow
    4. Schedule with launchd or cron (see architecture.md)
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# === CONFIGURATION ===
# Adjust these paths to match your setup

VAULT_PATH = Path.home() / "Vault"  # or wherever your knowledge store lives
FOLLOW_UPS_PATH = VAULT_PATH / "70-queues" / "follow-ups.md"
BRIEFING_OUTPUT = VAULT_PATH / "00-inbox" / "daily-briefing.md"
CREDENTIALS_PATH = Path.home() / ".credentials" / "google_credentials.json"
TOKEN_PATH = Path.home() / ".credentials" / "google_token.json"

# Google Calendar IDs to check
CALENDAR_IDS = [
    "primary",
    # "work@yourcompany.com",  # Add additional calendars here
]


def get_calendar_events():
    """Fetch today's events from Google Calendar."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

        creds = None
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_PATH), SCOPES
                )
                creds = flow.run_local_server(port=0)
            TOKEN_PATH.write_text(creds.to_json())

        service = build("calendar", "v3", credentials=creds)

        now = datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0).isoformat() + "Z"
        end_of_day = now.replace(hour=23, minute=59, second=59).isoformat() + "Z"

        all_events = []
        for cal_id in CALENDAR_IDS:
            result = (
                service.events()
                .list(
                    calendarId=cal_id,
                    timeMin=start_of_day,
                    timeMax=end_of_day,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            all_events.extend(result.get("items", []))

        # Sort by start time
        all_events.sort(key=lambda e: e["start"].get("dateTime", e["start"].get("date", "")))
        return all_events

    except Exception as e:
        return [{"error": str(e)}]


def get_follow_ups():
    """Read open follow-ups from the queue file."""
    if not FOLLOW_UPS_PATH.exists():
        return []

    follow_ups = []
    for line in FOLLOW_UPS_PATH.read_text().splitlines():
        line = line.strip()
        if line.startswith("- [ ]"):
            follow_ups.append(line[6:])  # Strip the checkbox
    return follow_ups


def classify_follow_up(item):
    """Simple overdue detection based on date mentions."""
    today = datetime.now()
    # Look for date patterns in the follow-up text
    # This is basic — enhance with dateutil.parser for production use
    if "overdue" in item.lower() or "past due" in item.lower():
        return "overdue"
    return "open"


def generate_briefing():
    """Generate the morning briefing."""
    today = datetime.now().strftime("%A, %B %d, %Y")
    lines = [f"# Morning Briefing — {today}\n"]

    # Calendar
    lines.append("## Today's Schedule\n")
    events = get_calendar_events()
    if not events:
        lines.append("No events scheduled today.\n")
    elif "error" in events[0]:
        lines.append(f"Could not fetch calendar: {events[0]['error']}\n")
    else:
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date", ""))
            summary = event.get("summary", "No title")
            if "T" in start:
                # Parse time from ISO format
                time_str = datetime.fromisoformat(start.replace("Z", "+00:00")).strftime(
                    "%I:%M %p"
                )
                lines.append(f"- **{time_str}** — {summary}")
            else:
                lines.append(f"- **All day** — {summary}")
        lines.append("")

    # Follow-ups
    lines.append("## Open Follow-ups\n")
    follow_ups = get_follow_ups()
    if not follow_ups:
        lines.append("No open follow-ups. Nice.\n")
    else:
        overdue = [f for f in follow_ups if classify_follow_up(f) == "overdue"]
        open_items = [f for f in follow_ups if classify_follow_up(f) == "open"]

        if overdue:
            lines.append("### Overdue")
            for item in overdue:
                lines.append(f"- {item}")
            lines.append("")

        if open_items:
            lines.append("### Open")
            for item in open_items[:10]:  # Cap at 10 to avoid overwhelm
                lines.append(f"- {item}")
            if len(open_items) > 10:
                lines.append(f"- ...and {len(open_items) - 10} more")
            lines.append("")

    # Suggested priorities
    lines.append("## Suggested Priorities\n")
    lines.append("*Based on overdue items and today's schedule:*\n")

    priorities = []
    if overdue:
        priorities.append(f"1. **Clear overdue items** — {len(overdue)} items need attention")
    if events and "error" not in events[0]:
        next_event = events[0]
        time_str = next_event["start"].get("dateTime", "today")
        priorities.append(f"2. **Prep for {next_event.get('summary', 'next meeting')}**")
    if not priorities:
        priorities.append("1. No urgent items — use this for deep work")

    lines.extend(priorities)
    lines.append("\n---\n*Generated at " + datetime.now().strftime("%I:%M %p") + "*")

    return "\n".join(lines)


if __name__ == "__main__":
    briefing = generate_briefing()

    # Write to file
    BRIEFING_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    BRIEFING_OUTPUT.write_text(briefing)

    # Also print to stdout (useful for session hooks)
    print(briefing)
