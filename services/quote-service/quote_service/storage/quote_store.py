"""Quote storage - in-memory stub for quote persistence."""

from __future__ import annotations

import logging
from datetime import datetime
from threading import Lock
from typing import Any
from uuid import UUID

from quote_service.domain.models import Quote, QuoteStatus

logger = logging.getLogger(__name__)


class QuoteStore:
    """In-memory quote storage (stub for production persistence).

    In production, this would be backed by a database (PostgreSQL, etc.).
    For now, provides a simple dict-based store with thread safety.
    """

    def __init__(self):
        self._quotes: dict[UUID, Quote] = {}
        self._lock = Lock()

    def save(self, quote: Quote) -> None:
        with self._lock:
            self._quotes[quote.quote_id] = quote
        logger.info("Quote saved: %s", quote.quote_id)

    def get(self, quote_id: UUID) -> Quote | None:
        with self._lock:
            return self._quotes.get(quote_id)

    def get_all(self, status: QuoteStatus | None = None) -> list[Quote]:
        with self._lock:
            if status is None:
                return list(self._quotes.values())
            return [q for q in self._quotes.values() if q.status == status]

    def update(self, quote: Quote) -> None:
        with self._lock:
            self._quotes[quote.quote_id] = quote

    def delete(self, quote_id: UUID) -> bool:
        with self._lock:
            return self._quotes.pop(quote_id, None) is not None

    def count(self) -> int:
        with self._lock:
            return len(self._quotes)

    def get_expired_quotes(self) -> list[Quote]:
        """Find all non-expired quotes that are past their expiration."""
        with self._lock:
            now = datetime.utcnow()
            return [
                q for q in self._quotes.values()
                if q.status != QuoteStatus.EXPIRED and q.expires_at < now
            ]

    def cleanup_expired(self) -> int:
        """Mark expired quotes and return count of expired."""
        expired = self.get_expired_quotes()
        count = 0
        with self._lock:
            for q in expired:
                q.mark_expired()
                count += 1
        if count:
            logger.info("Expired %d quotes", count)
        return count


# Global store instance
store = QuoteStore()
