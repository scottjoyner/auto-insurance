import sqlite3

from insurance_events.publisher import JsonlPublisher
from scripts.publish_outbox_events import publish_events


def test_publish_quote_events_marks_published(tmp_path):
    database = tmp_path / "events.db"
    output = tmp_path / "events.jsonl"
    conn = sqlite3.connect(database)
    conn.execute(
        "CREATE TABLE quote_events (event_id TEXT PRIMARY KEY, event_type TEXT, aggregate_id TEXT, aggregate_type TEXT, actor_id TEXT, payload TEXT, published_at TEXT, created_at TEXT)"
    )
    conn.execute(
        "INSERT INTO quote_events(event_id, event_type, aggregate_id, aggregate_type, actor_id, payload, created_at) VALUES ('evt-1', 'QuoteCreated', 'quote-1', 'quote', 'actor-1', '{\"x\": 1}', '2026-01-01')"
    )
    conn.commit()

    count = publish_events(conn, "quote", 10, JsonlPublisher(output))

    assert count == 1
    assert "QuoteCreated" in output.read_text(encoding="utf-8")
    published_at = conn.execute("SELECT published_at FROM quote_events WHERE event_id = 'evt-1'").fetchone()[0]
    assert published_at is not None


def test_publish_policy_events_to_jsonl(tmp_path):
    database = tmp_path / "events.db"
    output = tmp_path / "events.jsonl"
    conn = sqlite3.connect(database)
    conn.execute(
        "CREATE TABLE policy_events (event_id TEXT PRIMARY KEY, event_type TEXT, aggregate_id TEXT, actor_id TEXT, payload TEXT, created_at TEXT)"
    )
    conn.execute(
        "INSERT INTO policy_events(event_id, event_type, aggregate_id, actor_id, payload, created_at) VALUES ('evt-1', 'PolicyBound', 'policy-1', 'actor-1', '{\"x\": 1}', '2026-01-01')"
    )
    conn.commit()

    count = publish_events(conn, "policy", 10, JsonlPublisher(output))

    assert count == 1
    assert "PolicyBound" in output.read_text(encoding="utf-8")
