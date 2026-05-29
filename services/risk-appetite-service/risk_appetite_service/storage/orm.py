"""ORM models for risk appetite persistence."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from risk_appetite_service.storage.database import Base


class RiskPolicyVersionRecord(Base):
    """Versioned risk appetite policy record."""

    __tablename__ = "risk_policy_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft", index=True)
    effective_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    policy_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    submitted_by_actor_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    approved_by_actor_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    activated_by_actor_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class RiskAssessmentRecord(Base):
    """Persisted risk appetite assessment."""

    __tablename__ = "risk_assessments"

    assessment_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    quote_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    policy_version: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    decision: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False, default="LOW")
    quote_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    portfolio_state: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    assessment_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False, default="system")
    assessed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class RiskPolicyApprovalRecord(Base):
    """Approval action for a policy version."""

    __tablename__ = "risk_policy_approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_version_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
