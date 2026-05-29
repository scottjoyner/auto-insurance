"""Claims service ORM models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from claims_service.database import Base


class ClaimRecord(Base):
    __tablename__ = "claims"

    claim_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    customer_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    policy_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="open", index=True)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="low", index=True)
    queue: Mapped[str] = mapped_column(String(64), nullable=False, default="New FNOL", index=True)
    loss_type: Mapped[str] = mapped_column(String(64), nullable=False)
    loss_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    loss_location: Mapped[str] = mapped_column(Text, nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    police_report_indicator: Mapped[bool] = mapped_column(nullable=False, default=False)
    injuries_indicator: Mapped[bool] = mapped_column(nullable=False, default=False)
    preferred_contact_method: Mapped[str] = mapped_column(String(64), nullable=False, default="email")
    fnol_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_by_actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ClaimEvidenceRecord(Base):
    __tablename__ = "claim_evidence"

    evidence_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    claim_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False, default="customer")
    uri: Mapped[str] = mapped_column(Text, nullable=False, default="")
    checksum: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    visibility: Mapped[str] = mapped_column(String(64), nullable=False, default="internal")
    uploaded_by_actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ClaimNoteRecord(Base):
    __tablename__ = "claim_notes"

    note_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    claim_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    note_type: Mapped[str] = mapped_column(String(64), nullable=False, default="adjuster")
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ClaimStatusHistoryRecord(Base):
    __tablename__ = "claim_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    claim_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    from_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    to_status: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False, default="")
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ClaimReserveHistoryRecord(Base):
    __tablename__ = "claim_reserve_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    claim_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False, default="")
    recommended_by_actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    approved_by_actor_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="pending_approval")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ClaimEventRecord(Base):
    __tablename__ = "claim_events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
