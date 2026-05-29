"""Repository adapter for durable quote persistence."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from quote_service.domain.models import Quote, QuoteStatus, ReferralFlag
from quote_service.storage.orm import QuoteRecord


class QuoteRepository:
    """SQLAlchemy-backed quote repository."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, quote: Quote, actor_id: str = "system") -> Quote:
        record = self.session.get(QuoteRecord, str(quote.quote_id))
        if record is None:
            record = QuoteRecord(quote_id=str(quote.quote_id), created_by_actor_id=actor_id)
            self.session.add(record)
        self._apply_quote(record, quote, actor_id)
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

    def update(self, quote: Quote, actor_id: str = "system") -> Quote:
        return self.save(quote, actor_id=actor_id)

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
