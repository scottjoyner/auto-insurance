#!/usr/bin/env python3
"""Prototype outbox publisher for Phase 1 services.

This script intentionally does not publish to Kafka/SNS yet. It provides a
repeatable boundary for draining outbox tables, marking records as published,
and emitting JSON lines that can be redirected to a file or log collector.

Supported services:
- quote: quote_events table with published_at column
- policy: policy_events table without published_at column; emits events only

Usage:
    python scripts/publish_outbox_events.py --database quote_service.db --service quote
    python scripts/publish_outbox_events.py --database policy_service.db --service policy
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path


def publish_quote_events(conn: sqlite3.Connection, limit: int) -> list[dict]:
    rows = conn.execute(
        "SELECT event_id, event_type, aggregate_id, aggregate_type, actor_id, payload, created_at "
        "FROM quote_events WHERE published_at IS NULL ORDER BY created_at LIMIT ?",
        (limit,),
    ).fetchall()
    events = []
    now = datetime.utcnow().isoformat()
    for row in rows:
        event = {
            "event_id": row[0],
            "event_type": row[1],
            "aggregate_id": row[2],
            "aggregate_type": row[3],
            "actor_id": row[4],
            "payload": json.loads(row[5]) if isinstance(row[5], str) else row[5],
            "created_at": row[6],
        }
        events.append(event)
        conn.execute("UPDATE quote_events SET published_at = ? WHERE event_id = ?", (now, row[0]))
    conn.commit()
    return events


def publish_policy_events(conn: sqlite3.Connection, limit: int) -> list[dict]:
    rows = conn.execute(
        "SELECT event_id, event_type, aggregate_id, actor_id, payload, created_at "
        "FROM policy_events ORDER BY created_at LIMIT ?",
        (limit,),
    ).fetchall()
    events = []
    for row in rows:
        events.append(
            {
                "event_id": row[0],
                "event_type": row[1],
                "aggregate_id": row[2],
                "actor_id": row[3],
                "payload": json.loads(row[4]) if isinstance(row[4], str) else row[4],
                "created_at": row[5],
            }
        )
    return events


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--service", required=True, choices=["quote", "policy"])
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    with sqlite3.connect(args.database) as conn:
        if args.service == "quote":
            events = publish_quote_events(conn, args.limit)
        else:
            events = publish_policy_events(conn, args.limit)

    for event in events:
        print(json.dumps(event, sort_keys=True))


if __name__ == "__main__":
    main()
