#!/usr/bin/env python3
"""
Memory system CLI — persistent knowledge base for Claude Code.

Stores facts, milestones, and knowledge profile in SQLite with FTS5 search.
Designed to be called by Claude Code during sessions for real-time knowledge capture.

Usage:
    python3 ~/Scripts/memory.py add "FACT" --source SRC --category CAT --confidence 0.9
    python3 ~/Scripts/memory.py retrieve "query"
    python3 ~/Scripts/memory.py context          # Session context injection
    python3 ~/Scripts/memory.py knowledge         # Knowledge profile
    python3 ~/Scripts/memory.py stats             # Memory system stats
    python3 ~/Scripts/memory.py milestone "WIN"   # Log an achievement
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ============================================
# Configuration — adjust these paths
# ============================================
DB_PATH = os.path.expanduser("~/Vault/60-Memory/memory.db")


def get_db():
    """Connect to memory database, creating tables if needed."""
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row

    # Core tables
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            source TEXT,
            category TEXT DEFAULT 'general',
            confidence REAL DEFAULT 0.8,
            provenance TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS knowledge_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            level TEXT,
            interests TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts
            USING fts5(content, source, category, content=facts, content_rowid=id);
    """)

    # Keep FTS in sync
    conn.executescript("""
        CREATE TRIGGER IF NOT EXISTS facts_ai AFTER INSERT ON facts BEGIN
            INSERT INTO facts_fts(rowid, content, source, category)
            VALUES (new.id, new.content, new.source, new.category);
        END;
        CREATE TRIGGER IF NOT EXISTS facts_ad AFTER DELETE ON facts BEGIN
            INSERT INTO facts_fts(facts_fts, rowid, content, source, category)
            VALUES('delete', old.id, old.content, old.source, old.category);
        END;
    """)

    return conn


def add_fact(content, source=None, category="general", confidence=0.8, provenance=None):
    """Add a fact to memory."""
    conn = get_db()
    conn.execute(
        "INSERT INTO facts (content, source, category, confidence, provenance) VALUES (?, ?, ?, ?, ?)",
        (content, source, category, confidence, provenance),
    )
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    print(f"Added fact (#{count}): {content[:80]}...")
    conn.close()


def retrieve(query, limit=10):
    """Search memory using FTS5."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT f.content, f.source, f.category, f.confidence, f.created_at,
               rank
        FROM facts_fts fts
        JOIN facts f ON fts.rowid = f.id
        WHERE facts_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        """,
        (query, limit),
    ).fetchall()
    conn.close()

    if not rows:
        print(f"No results for: {query}")
        return

    for row in rows:
        conf = f"[{row['confidence']:.1f}]" if row["confidence"] else ""
        src = f" ({row['source']})" if row["source"] else ""
        cat = f" [{row['category']}]" if row["category"] else ""
        print(f"  {conf}{cat} {row['content']}{src}")


def context():
    """Output session context — recent facts and stats for briefing injection."""
    conn = get_db()

    # Recent facts (last 7 days)
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    recent = conn.execute(
        "SELECT content, category, source FROM facts WHERE created_at > ? ORDER BY created_at DESC LIMIT 15",
        (week_ago,),
    ).fetchall()

    # Recent milestones
    milestones = conn.execute(
        "SELECT content, created_at FROM milestones ORDER BY created_at DESC LIMIT 5"
    ).fetchall()

    # Stats
    total = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    categories = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM facts GROUP BY category ORDER BY cnt DESC"
    ).fetchall()

    conn.close()

    print("=== MEMORY CONTEXT ===")
    print(f"\nTotal facts: {total}")

    if recent:
        print(f"\nRecent ({len(recent)} facts, last 7 days):")
        for r in recent:
            cat = f"[{r['category']}]" if r["category"] else ""
            print(f"  {cat} {r['content'][:100]}")

    if milestones:
        print(f"\nRecent wins:")
        for m in milestones:
            print(f"  🎯 {m['content']}")

    if categories:
        print(f"\nCategories: {', '.join(f'{c[0]}({c[1]})' for c in categories)}")


def stats():
    """Print memory system statistics."""
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    categories = conn.execute(
        "SELECT category, COUNT(*) FROM facts GROUP BY category ORDER BY COUNT(*) DESC"
    ).fetchall()
    recent_week = conn.execute(
        "SELECT COUNT(*) FROM facts WHERE created_at > datetime('now', '-7 days')"
    ).fetchone()[0]
    milestones_count = conn.execute("SELECT COUNT(*) FROM milestones").fetchone()[0]
    conn.close()

    print(f"Total facts: {total}")
    print(f"Added this week: {recent_week}")
    print(f"Milestones: {milestones_count}")
    print(f"\nBy category:")
    for cat, count in categories:
        print(f"  {cat}: {count}")


def add_milestone(content, category=None):
    """Log a milestone/achievement."""
    conn = get_db()
    conn.execute(
        "INSERT INTO milestones (content, category) VALUES (?, ?)",
        (content, category),
    )
    conn.commit()
    conn.close()
    print(f"🎯 Milestone logged: {content}")


def main():
    parser = argparse.ArgumentParser(description="Memory system CLI")
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add a fact")
    p_add.add_argument("content", help="The fact to store")
    p_add.add_argument("--source", "-s", help="Where this came from")
    p_add.add_argument("--category", "-c", default="general", help="Category")
    p_add.add_argument("--confidence", type=float, default=0.8, help="Confidence 0-1")
    p_add.add_argument("--provenance", "-p", help="How it was captured")

    # retrieve
    p_ret = sub.add_parser("retrieve", help="Search memory")
    p_ret.add_argument("query", help="Search query")
    p_ret.add_argument("--limit", "-n", type=int, default=10)

    # context
    sub.add_parser("context", help="Session context injection")

    # stats
    sub.add_parser("stats", help="Memory statistics")

    # knowledge
    sub.add_parser("knowledge", help="Knowledge profile")

    # milestone
    p_mile = sub.add_parser("milestone", help="Log a milestone")
    p_mile.add_argument("content", help="The achievement")
    p_mile.add_argument("--category", "-c", help="Category")

    args = parser.parse_args()

    if args.command == "add":
        add_fact(args.content, args.source, args.category, args.confidence, args.provenance)
    elif args.command == "retrieve":
        retrieve(args.query, args.limit)
    elif args.command == "context":
        context()
    elif args.command == "stats":
        stats()
    elif args.command == "knowledge":
        context()  # Same output for now
    elif args.command == "milestone":
        add_milestone(args.content, args.category)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
