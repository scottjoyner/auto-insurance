"""Event publisher abstractions.

The production implementation can add Kafka/SNS/PubSub adapters behind the same
interface. The Phase 2 implementation includes stdout and JSONL publishers so
outbox draining can be exercised safely in CI and local deployments.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
import json
from typing import Any


class EventPublisher(ABC):
    """Abstract event publisher boundary."""

    @abstractmethod
    def publish(self, event: dict[str, Any]) -> None:
        """Publish one normalized event."""


class StdoutPublisher(EventPublisher):
    """Publisher that emits JSON to stdout."""

    def publish(self, event: dict[str, Any]) -> None:
        print(json.dumps(event, sort_keys=True))


class JsonlPublisher(EventPublisher):
    """Publisher that appends events to a JSONL file."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def publish(self, event: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
