"""Optional broker-backed event publisher adapters.

These adapters use lazy imports so the base package remains lightweight in local
CI. Install the corresponding SDKs in production images before enabling them.
"""

from __future__ import annotations

import json
from typing import Any

from insurance_events.publisher import EventPublisher


class KafkaPublisher(EventPublisher):
    """Kafka publisher using confluent-kafka when installed."""

    def __init__(self, bootstrap_servers: str, topic: str):
        try:
            from confluent_kafka import Producer
        except ImportError as exc:
            raise RuntimeError("Install confluent-kafka to use KafkaPublisher") from exc
        self.topic = topic
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})

    def publish(self, event: dict[str, Any]) -> None:
        self.producer.produce(self.topic, json.dumps(event).encode("utf-8"), key=str(event.get("aggregate_id", event.get("event_id", ""))))
        self.producer.flush()


class SnsPublisher(EventPublisher):
    """AWS SNS publisher using boto3 when installed."""

    def __init__(self, topic_arn: str, region_name: str | None = None):
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError("Install boto3 to use SnsPublisher") from exc
        self.topic_arn = topic_arn
        self.client = boto3.client("sns", region_name=region_name)

    def publish(self, event: dict[str, Any]) -> None:
        self.client.publish(
            TopicArn=self.topic_arn,
            Message=json.dumps(event, sort_keys=True),
            MessageAttributes={"event_type": {"DataType": "String", "StringValue": str(event.get("event_type", "unknown"))}},
        )


class PubSubPublisher(EventPublisher):
    """Google Pub/Sub publisher using google-cloud-pubsub when installed."""

    def __init__(self, topic_path: str):
        try:
            from google.cloud import pubsub_v1
        except ImportError as exc:
            raise RuntimeError("Install google-cloud-pubsub to use PubSubPublisher") from exc
        self.topic_path = topic_path
        self.publisher = pubsub_v1.PublisherClient()

    def publish(self, event: dict[str, Any]) -> None:
        future = self.publisher.publish(self.topic_path, json.dumps(event, sort_keys=True).encode("utf-8"))
        future.result(timeout=10)
