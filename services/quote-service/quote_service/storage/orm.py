"""ORM models for quote persistence."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from quote_service.storage.database import Base


class QuoteRecord(Base):
    """Durable quote record containing the latest quote state."""

    __tablename__ = "quotes"

    quote_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    customer_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
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


class QuoteVersionRecord(Base):
    """Immutable quote version snapshot."""

    __tablename__ = "quote_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quote_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False, default="created")
    quote_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    input_snapshot_hash: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    rating_result_hash: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    created_by_actor_id: Mapped[str] = mapped_column(String(128), nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class QuoteStatusHistoryRecord(Base):
    """Quote lifecycle status transitions."""

    __tablename__ = "quote_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quote_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    from_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_status: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False, default="")
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class QuoteEventRecord(Base):
    """Outbox event for quote lifecycle actions."""

    __tablename__ = "quote_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    aggregate_type: Mapped[str] = mapped_column(String(64), nullable=False, default="quote")
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False, default="system")
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class QuoteRatingTraceRecord(Base):
    """Rating trace snapshot for audit and replay."""

    __tablename__ = "quote_rating_traces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quote_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    rating_result_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    input_snapshot_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    trace: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


Index("ix_quotes_product_status", QuoteRecord.product_id, QuoteRecord.status)
Index("ix_quotes_tenant_customer", QuoteRecord.tenant_id, QuoteRecord.customer_id)
Index("ux_quote_versions_quote_version", QuoteVersionRecord.quote_id, QuoteVersionRecord.version_number, unique=True)
