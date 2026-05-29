import json

from insurance_events.publisher import JsonlPublisher


def test_jsonl_publisher_writes_event(tmp_path):
    output = tmp_path / "events.jsonl"
    publisher = JsonlPublisher(output)
    publisher.publish({"event_id": "evt-1", "event_type": "QuoteCreated"})

    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["event_id"] == "evt-1"
