"""
Meeting Transcript Processor
==============================
Reads meeting transcripts and extracts structured data:
- Key facts (decisions, claims, context)
- Follow-up items (commitments, deadlines)
- Relationship notes (new contacts, role changes)

This is a template showing the extraction pattern. Adapt the
input source to match your transcription tool (Granola, Otter,
Fireflies, etc.).

Requirements:
    pip install anthropic  # For Claude API extraction

Setup:
    export ANTHROPIC_API_KEY=your-key-here
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# === CONFIGURATION ===

VAULT_PATH = Path.home() / "Vault"
MEETINGS_DIR = VAULT_PATH / "00-inbox" / "meetings"
FACTS_PATH = VAULT_PATH / "60-memory" / "facts.jsonl"
FOLLOW_UPS_PATH = VAULT_PATH / "70-queues" / "follow-ups.md"
PROCESSED_LOG = VAULT_PATH / "60-memory" / "processed-meetings.log"

# Where raw transcripts land (adapt to your transcription tool)
RAW_TRANSCRIPTS_DIR = Path.home() / "transcripts"

EXTRACTION_PROMPT = """Analyze this meeting transcript and extract structured data.

Return a JSON object with these fields:

{
  "summary": "2-3 sentence summary of the meeting",
  "facts": [
    {
      "content": "The specific fact or decision",
      "source": "Who said or decided this",
      "context": "Brief context for why this matters"
    }
  ],
  "follow_ups": [
    {
      "owner": "Who committed to this",
      "action": "What they committed to do",
      "deadline": "When (if mentioned), otherwise null",
      "context": "Why this matters"
    }
  ],
  "people": [
    {
      "name": "Person's name",
      "role": "Their role/company if mentioned",
      "note": "Anything notable about them or the relationship"
    }
  ]
}

Be precise. Only extract what's actually in the transcript — don't infer or speculate.
If a section has no items, use an empty array.

Transcript:
"""


def get_unprocessed_transcripts():
    """Find transcripts that haven't been processed yet."""
    if not RAW_TRANSCRIPTS_DIR.exists():
        print(f"Transcript directory not found: {RAW_TRANSCRIPTS_DIR}")
        return []

    # Load processed log
    processed = set()
    if PROCESSED_LOG.exists():
        processed = set(PROCESSED_LOG.read_text().splitlines())

    transcripts = []
    for f in RAW_TRANSCRIPTS_DIR.glob("*.txt"):
        if str(f) not in processed:
            transcripts.append(f)

    # Also check for .md files
    for f in RAW_TRANSCRIPTS_DIR.glob("*.md"):
        if str(f) not in processed:
            transcripts.append(f)

    return sorted(transcripts)


def extract_with_claude(transcript_text):
    """Use Claude API to extract structured data from a transcript."""
    try:
        import anthropic

        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": EXTRACTION_PROMPT + transcript_text,
                }
            ],
        )

        # Parse the JSON response
        response_text = message.content[0].text

        # Handle potential markdown code blocks in response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        return json.loads(response_text)

    except Exception as e:
        print(f"Extraction error: {e}")
        return None


def save_facts(facts, meeting_date, meeting_title):
    """Append extracted facts to the facts.jsonl file."""
    FACTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(FACTS_PATH, "a") as f:
        for fact in facts:
            entry = {
                "content": fact["content"],
                "source": fact.get("source", "unknown"),
                "context": fact.get("context", ""),
                "meeting": meeting_title,
                "date": meeting_date,
                "extracted": datetime.now().isoformat(),
            }
            f.write(json.dumps(entry) + "\n")


def save_follow_ups(follow_ups, meeting_date, meeting_title):
    """Append follow-ups to the queue file."""
    FOLLOW_UPS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(FOLLOW_UPS_PATH, "a") as f:
        f.write(f"\n### From: {meeting_title} ({meeting_date})\n")
        for item in follow_ups:
            deadline = f" (due: {item['deadline']})" if item.get("deadline") else ""
            f.write(f"- [ ] **{item['owner']}**: {item['action']}{deadline}\n")


def save_meeting_summary(extracted, meeting_file, meeting_date):
    """Save the processed meeting summary to the vault."""
    MEETINGS_DIR.mkdir(parents=True, exist_ok=True)

    output_path = MEETINGS_DIR / f"{meeting_date}-{meeting_file.stem}.md"
    lines = [
        f"# {meeting_file.stem}",
        f"**Date:** {meeting_date}",
        f"**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary",
        extracted["summary"],
        "",
    ]

    if extracted["facts"]:
        lines.append("## Key Facts")
        for fact in extracted["facts"]:
            lines.append(f"- {fact['content']} ({fact.get('source', 'unknown')})")
        lines.append("")

    if extracted["follow_ups"]:
        lines.append("## Follow-ups")
        for item in extracted["follow_ups"]:
            deadline = f" — due {item['deadline']}" if item.get("deadline") else ""
            lines.append(f"- [ ] {item['owner']}: {item['action']}{deadline}")
        lines.append("")

    if extracted["people"]:
        lines.append("## People Mentioned")
        for person in extracted["people"]:
            role = f" ({person['role']})" if person.get("role") else ""
            lines.append(f"- **{person['name']}**{role}: {person.get('note', '')}")
        lines.append("")

    output_path.write_text("\n".join(lines))
    return output_path


def mark_processed(file_path):
    """Record that a transcript has been processed."""
    PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_LOG, "a") as f:
        f.write(str(file_path) + "\n")


def process_all():
    """Process all unprocessed transcripts."""
    transcripts = get_unprocessed_transcripts()

    if not transcripts:
        print("No new transcripts to process.")
        return

    print(f"Found {len(transcripts)} unprocessed transcript(s).")

    for transcript_file in transcripts:
        print(f"\nProcessing: {transcript_file.name}")

        transcript_text = transcript_file.read_text()
        if len(transcript_text.strip()) < 100:
            print(f"  Skipping — too short ({len(transcript_text)} chars)")
            mark_processed(transcript_file)
            continue

        # Extract structured data
        extracted = extract_with_claude(transcript_text)
        if not extracted:
            print("  Extraction failed — skipping")
            continue

        # Derive meeting date from filename or use today
        meeting_date = datetime.now().strftime("%Y-%m-%d")

        # Save everything
        if extracted.get("facts"):
            save_facts(extracted["facts"], meeting_date, transcript_file.stem)
            print(f"  Saved {len(extracted['facts'])} facts")

        if extracted.get("follow_ups"):
            save_follow_ups(extracted["follow_ups"], meeting_date, transcript_file.stem)
            print(f"  Saved {len(extracted['follow_ups'])} follow-ups")

        output_path = save_meeting_summary(extracted, transcript_file, meeting_date)
        print(f"  Summary saved to {output_path}")

        mark_processed(transcript_file)

    print("\nDone.")


if __name__ == "__main__":
    process_all()
