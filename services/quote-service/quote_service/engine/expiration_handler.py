"""Quote expiration handler - manages quote lifecycle and expiration."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from quote_service.domain.models import Quote, QuoteStatus
from quote_service.storage.quote_store import store

logger = logging.getLogger(__name__)


class QuoteExpirationHandler:
    """Handles quote expiration checks and notifications."""

    def __init__(self, check_interval: int = 300, batch_size: int = 100):
        self.check_interval = check_interval
        self.batch_size = batch_size

    def check_and_expire(self) -> int:
        """Check for expired quotes and mark them. Returns count expired."""
        count = store.cleanup_expired()
        if count:
            logger.info("Expired %d quotes", count)
        return count

    def extend_quote(self, quote_id, new_expires_at: datetime | None = None) -> bool:
        """Extend a quote's expiration date."""
        quote = store.get(quote_id)
        if quote is None:
            return False
        if quote.status == QuoteStatus.EXPIRED:
            return False

        if new_expires_at is None:
            new_expires_at = datetime.utcnow() + timedelta(days=30)

        quote.expires_at = new_expires_at
        store.update(quote)
        logger.info("Extended quote %s to %s", quote_id, new_expires_at.isoformat())
        return True

    def get_active_quotes(self) -> list[Quote]:
        """Get all non-expired, non-withdrawn quotes."""
        all_quotes = store.get_all()
        now = datetime.utcnow()
        return [
            q for q in all_quotes
            if q.status not in (QuoteStatus.EXPIRED, QuoteStatus.WITHDRAWN)
            and q.expires_at > now
        ]

    def get_quote_details(self, quote_id) -> dict[str, Any] | None:
        """Get detailed info about a specific quote."""
        quote = store.get(quote_id)
        if quote is None:
            return None

        return {
            "quote_id": str(quote.quote_id),
            "status": quote.status,
            "total_premium": quote.total_premium,
            "expires_at": quote.expires_at.isoformat(),
            "is_expired": quote.is_expired(),
            "time_remaining_seconds": max(
                0, (quote.expires_at - datetime.utcnow()).total_seconds()
            ),
            "coverages": quote.coverages,
            "reason_codes": quote.reason_codes,
            "bind_eligible": quote.bind_eligible,
            "referral_flag": quote.referral_flag,
        }
