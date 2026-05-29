"""ORM models for policy bind workflow persistence."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from policy_service.storage.database import Base


class BindRequestRecord(Base):
    """Bind request prepared from an accepted quote."""

    __tablename__ = "bind_requests"

    bind_request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    customer_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    quote_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    policy_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    request_key: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending_approval", index=True)
    bind_method: Mapped[str] = mapped_column(String(64), nullable=False, default="human_approval")
    total_premium: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    effective_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expiration_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    quote_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    risk_assessment_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_by_actor_id: Mapped[str] = mapped_column(String(128), nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ApprovalRecord(Base):
    """Human approval record for a bind request."""

    __tablename__ = "bind_approvals"

    approval_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bind_request_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    approver_actor_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    comments: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class PolicyRecord(Base):
    """Issued policy record."""

    __tablename__ = "policies"

    policy_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    customer_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    quote_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    bind_request_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)
    total_premium: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    effective_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expiration_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    bind_packet: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    bound_by_actor_id: Mapped[str] = mapped_column(String(128), nullable=False, default="system")
    bound_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class PolicyEventRecord(Base):
    """Policy lifecycle event outbox."""

    __tablename__ = "policy_events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False, default="system")
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
