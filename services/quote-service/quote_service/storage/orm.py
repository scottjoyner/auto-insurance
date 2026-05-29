"""ORM models for quote persistence."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from quote_service.storage.database import Base


class QuoteRecord(Base):
    """Durable quote record.

    This is intentionally a compact P1.1 table. Later passes split rating traces,
    status history, and event outbox into dedicated normalized tables.
    """

    __tablename__ = "quotes"

    quote_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    product_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    product_version: Mapped[str] = mapped_column(String(64), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    total_premium: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    coverages: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    reason_codes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    surcharges_applied: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    discounts_applied: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    bind_eligible: Mapped[bool] = mapped_column(nullable=False, default=False)
    referral_flag: Mapped[str] = mapped_column(String(64), nullable=False, default="none")
    referral_reason: Mapped[str] = mapped_column(Text, nullable=False, default="")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rating_result_hash: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    input_snapshot_hash: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    ai_confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    applicant_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_by_actor_id: Mapped[str] = mapped_column(String(128), nullable=False, default="system")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


Index("ix_quotes_product_status", QuoteRecord.product_id, QuoteRecord.status)
