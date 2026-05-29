"""Repository adapter for durable quote persistence."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.orm import Session

from quote_service.domain.models import Quote, QuoteStatus, ReferralFlag
from quote_service.storage.orm import (
    QuoteEventRecord,
    QuoteRatingTraceRecord,
    QuoteRecord,
    QuoteStatusHistoryRecord,
    QuoteVersionRecord,
)


class QuoteRepository:
    """SQLAlchemy-backed quote repository."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, quote: Quote, actor_id: str = "system", reason: str = "created") -> Quote:
        record = self.session.get(QuoteRecord, str(quote.quote_id))
        previous_status = record.status if record is not None else None
        is_new = record is None
        if record is None:
            record = QuoteRecord(quote_id=str(quote.quote_id), created_by_actor_id=actor_id)
            self.session.add(record)

        self._apply_quote(record, quote, actor_id)
        self.session.flush()

        self._append_version(quote, actor_id=actor_id, reason=reason)
        self._append_rating_trace(quote)
        if is_new or previous_status != str(quote.status):
            self._append_status_history(quote, previous_status, actor_id=actor_id, reason=reason)
        self._append_event(
            event_type="QuoteCreated" if is_new else "QuoteUpdated",
            quote=quote,
            actor_id=actor_id,
            payload={"reason": reason, "status": str(quote.status), "total_premium": quote.total_premium},
        )

        self.session.commit()
        self.session.refresh(record)
        return self._to_domain(record)

    def get(self, quote_id: UUID | str) -> Quote | None:
        record = self.session.get(QuoteRecord, str(quote_id))
        if record is None:
            return None
        return self._to_domain(record)

    def list(self, status: QuoteStatus | None = None, limit: int = 100) -> list[Quote]:
        query = self.session.query(QuoteRecord).order_by(QuoteRecord.created_at.desc())
        if status is not None:
            query = query.filter(QuoteRecord.status == str(status))
        return [self._to_domain(record) for record in query.limit(limit).all()]

    def accept(self, quote_id: UUID | str, actor_id: str, reason: str = "accepted") -> Quote | None:
        quote = self.get(quote_id)
        if quote is None:
            return None
        if quote.is_expired():
            quote.mark_expired()
            self.save(quote, actor_id=actor_id, reason="expired_before_acceptance")
            return quote
        quote.mark_converted()
        quote.accepted_at = datetime.utcnow()
        return self.save(quote, actor_id=actor_id, reason=reason)

    def update(self, quote: Quote, actor_id: str = "system") -> Quote:
        return self.save(quote, actor_id=actor_id, reason="updated")

    def _append_version(self, quote: Quote, actor_id: str, reason: str) -> None:
        current_max = (
            self.session.query(func.max(QuoteVersionRecord.version_number))
            .filter(QuoteVersionRecord.quote_id == str(quote.quote_id))
            .scalar()
            or 0
        )
        self.session.add(
            QuoteVersionRecord(
                quote_id=str(quote.quote_id),
                version_number=int(current_max) + 1,
                reason=reason,
                quote_snapshot=quote.to_dict(),
                input_snapshot_hash=quote.input_snapshot_hash,
                rating_result_hash=quote.rating_result_hash,
                created_by_actor_id=actor_id,
            )
        )

    def _append_status_history(self, quote: Quote, previous_status: str | None, actor_id: str, reason: str) -> None:
        self.session.add(
            QuoteStatusHistoryRecord(
                quote_id=str(quote.quote_id),
                from_status=previous_status,
                to_status=str(quote.status),
                reason=reason,
                actor_id=actor_id,
            )
        )

    def _append_rating_trace(self, quote: Quote) -> None:
        self.session.add(
            QuoteRatingTraceRecord(
                quote_id=str(quote.quote_id),
                rating_result_hash=quote.rating_result_hash,
                input_snapshot_hash=quote.input_snapshot_hash,
                trace={
                    "coverages": quote.coverages,
                    "surcharges_applied": quote.surcharges_applied,
                    "discounts_applied": quote.discounts_applied,
                    "reason_codes": quote.reason_codes,
                    "total_premium": quote.total_premium,
                },
            )
        )

    def _append_event(self, event_type: str, quote: Quote, actor_id: str, payload: dict) -> None:
        self.session.add(
            QuoteEventRecord(
                event_id=str(uuid4()),
                event_type=event_type,
                aggregate_id=str(quote.quote_id),
                aggregate_type="quote",
                actor_id=actor_id,
                payload=payload,
            )
        )

    def _apply_quote(self, record: QuoteRecord, quote: Quote, actor_id: str) -> None:
        record.product_id = quote.product_id
        record.product_version = quote.product_version
        record.jurisdiction = quote.jurisdiction
        record.status = str(quote.status)
        record.total_premium = float(quote.total_premium)
        record.coverages = dict(quote.coverages)
        record.reason_codes = list(quote.reason_codes)
        record.surcharges_applied = list(quote.surcharges_applied)
        record.discounts_applied = list(quote.discounts_applied)
        record.bind_eligible = bool(quote.bind_eligible)
        record.referral_flag = str(quote.referral_flag)
        record.referral_reason = quote.referral_reason
        record.expires_at = quote.expires_at
        record.created_at = quote.created_at
        record.accepted_at = quote.accepted_at
        record.rating_result_hash = quote.rating_result_hash
        record.input_snapshot_hash = quote.input_snapshot_hash
        record.ai_confidence_score = quote.ai_confidence_score
        record.applicant_data = dict(getattr(quote, "_applicant_data", {}) or {})
        record.updated_at = datetime.utcnow()
        if not record.created_by_actor_id:
            record.created_by_actor_id = actor_id

    def _to_domain(self, record: QuoteRecord) -> Quote:
        quote = Quote(
            quote_id=UUID(record.quote_id),
            product_id=record.product_id,
            product_version=record.product_version,
            jurisdiction=record.jurisdiction,
            status=QuoteStatus(record.status),
            total_premium=float(record.total_premium),
            coverages=dict(record.coverages or {}),
            reason_codes=list(record.reason_codes or []),
            surcharges_applied=list(record.surcharges_applied or []),
            discounts_applied=list(record.discounts_applied or []),
            bind_eligible=record.bind_eligible,
            referral_flag=ReferralFlag(record.referral_flag),
            referral_reason=record.referral_reason,
            expires_at=record.expires_at,
            created_at=record.created_at,
            accepted_at=record.accepted_at,
            rating_result_hash=record.rating_result_hash,
            input_snapshot_hash=record.input_snapshot_hash,
            ai_confidence_score=record.ai_confidence_score,
        )
        quote._applicant_data = dict(record.applicant_data or {})
        return quote
