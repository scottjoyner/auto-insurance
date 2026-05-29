#!/usr/bin/env python3
"""Outbox publisher for Phase 1/2 services.

Supported services:
- quote: quote_events table with published_at column
- policy: policy_events table currently emitted without published_at tracking

Supported publishers:
- stdout
- jsonl
- kafka
- sns
- pubsub
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from insurance_events.publisher import EventPublisher, JsonlPublisher, StdoutPublisher


def _json_value(value: Any) -> Any:
    return json.loads(value) if isinstance(value, str) else value


def fetch_quote_events(conn: sqlite3.Connection, limit: int) -> list[dict]:
    rows = conn.execute(
        "SELECT event_id, event_type, aggregate_id, aggregate_type, actor_id, payload, created_at "
        "FROM quote_events WHERE published_at IS NULL ORDER BY created_at LIMIT ?",
        (limit,),
    ).fetchall()
    return [
        {
            "event_id": row[0],
            "event_type": row[1],
            "aggregate_id": row[2],
            "aggregate_type": row[3],
            "actor_id": row[4],
            "payload": _json_value(row[5]),
            "created_at": row[6],
        }
        for row in rows
    ]


def mark_quote_events_published(conn: sqlite3.Connection, events: list[dict]) -> None:
    now = datetime.utcnow().isoformat()
    for event in events:
        conn.execute("UPDATE quote_events SET published_at = ? WHERE event_id = ?", (now, event["event_id"]))
    conn.commit()


def fetch_policy_events(conn: sqlite3.Connection, limit: int) -> list[dict]:
    rows = conn.execute(
        "SELECT event_id, event_type, aggregate_id, actor_id, payload, created_at "
        "FROM policy_events ORDER BY created_at LIMIT ?",
        (limit,),
    ).fetchall()
    return [
        {
            "event_id": row[0],
            "event_type": row[1],
            "aggregate_id": row[2],
            "actor_id": row[3],
            "payload": _json_value(row[4]),
            "created_at": row[5],
        }
        for row in rows
    ]


def build_publisher(args: argparse.Namespace) -> EventPublisher:
    if args.publisher == "stdout":
        return StdoutPublisher()
    if args.publisher == "jsonl":
        if not args.output:
            raise SystemExit("--output is required for jsonl publisher")
        return JsonlPublisher(args.output)
    if args.publisher == "kafka":
        from insurance_events.adapters import KafkaPublisher

        if not args.kafka_bootstrap_servers or not args.kafka_topic:
            raise SystemExit("--kafka-bootstrap-servers and --kafka-topic are required for kafka publisher")
        return KafkaPublisher(args.kafka_bootstrap_servers, args.kafka_topic)
    if args.publisher == "sns":
        from insurance_events.adapters import SnsPublisher

        if not args.sns_topic_arn:
            raise SystemExit("--sns-topic-arn is required for sns publisher")
        return SnsPublisher(args.sns_topic_arn, region_name=args.aws_region)
    if args.publisher == "pubsub":
        from insurance_events.adapters import PubSubPublisher

        if not args.pubsub_topic_path:
            raise SystemExit("--pubsub-topic-path is required for pubsub publisher")
        return PubSubPublisher(args.pubsub_topic_path)
    raise SystemExit(f"Unsupported publisher: {args.publisher}")


def publish_events(conn: sqlite3.Connection, service: str, limit: int, publisher: EventPublisher, mark_published: bool = True) -> int:
    if service == "quote":
        events = fetch_quote_events(conn, limit)
    else:
        events = fetch_policy_events(conn, limit)
    for event in events:
        publisher.publish(event)
    if service == "quote" and mark_published:
        mark_quote_events_published(conn, events)
    return len(events)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--service", required=True, choices=["quote", "policy"])
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--publisher", choices=["stdout", "jsonl", "kafka", "sns", "pubsub"], default="stdout")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-mark-published", action="store_true")
    parser.add_argument("--kafka-bootstrap-servers")
    parser.add_argument("--kafka-topic")
    parser.add_argument("--sns-topic-arn")
    parser.add_argument("--aws-region")
    parser.add_argument("--pubsub-topic-path")
    args = parser.parse_args()

    publisher = build_publisher(args)
    with sqlite3.connect(args.database) as conn:
        count = publish_events(conn, args.service, args.limit, publisher, mark_published=not args.no_mark_published)
    print(f"Published {count} {args.service} events using {args.publisher} publisher")


if __name__ == "__main__":
    main()
