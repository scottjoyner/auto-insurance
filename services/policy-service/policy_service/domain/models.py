"""Policy service domain models - policy lifecycle, audit packets, bind flow."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class PolicyState(StrEnum):
    """Policy lifecycle states."""
    DRAFT = "draft"
    PENDING_BIND = "pending_bind"
    ACTIVE = "active"
    ENDORSEMENT = "endorsement"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class PolicyTransition(StrEnum):
    """Valid policy transitions."""
    DRAFT_TO_PENDING_BIND = "draft_to_pending_bind"
    PENDING_BIND_TO_ACTIVE = "pending_bind_to_active"
    ACTIVE_TO_ENDORSEMENT = "active_to_endorsement"
    ACTIVE_TO_CANCELLED = "active_to_cancelled"
    ACTIVE_TO_EXPIRED = "active_to_expired"
    ENDORSEMENT_TO_ACTIVE = "endorsement_to_active"
    CANCELLED_TO_DRAFT = "cancelled_to_draft"


class ApprovalStatus(StrEnum):
    """Human approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class AuditEventType(StrEnum):
    """Types of audit events."""
    BIND = "bind"
    ENDORSEMENT = "endorsement"
    CANCELLATION = "cancellation"
    RENEWAL = "renewal"
    CLAIM_FILING = "claim_filing"
    CLAIM_SETTLEMENT = "claim_settlement"


class BindMethod(StrEnum):
    """Methods of binding a policy."""
    HUMAN_APPROVAL = "human_approval"
    AI_PREPARED = "ai_prepared"
    AUTOMATED = "automated"


class PolicyDocumentType(StrEnum):
    """Types of policy documents."""
    POLICY_DECLARATION = "policy_declaration"
    INSURANCE_CERTIFICATE = "insurance_certificate"
    ENDORSEMENT = "endorsement"
    CANCELLATION_NOTICE = "cancellation_notice"
    RENEWAL_NOTICE = "renewal_notice"


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


@dataclass
class Coverage:
    """Insurance coverage."""
    type: str
    limit: float
    deductible: float
    premium: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "limit": self.limit,
            "deductible": self.deductible,
            "premium": self.premium,
            "metadata": self.metadata,
        }


@dataclass
class PolicyHolder:
    """Policy holder information."""
    name: str
    address: str
    phone: str
    email: str
    driver_license: str
    date_of_birth: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "driver_license": self.driver_license,
            "date_of_birth": self.date_of_birth,
            "metadata": self.metadata,
        }


@dataclass
class VehicleInfo:
    """Vehicle information."""
    make: str
    model: str
    year: int
    vin: str
    license_plate: str
    state: str
    mileage: int
    primary_use: str
    garage_location: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "vin": self.vin,
            "license_plate": self.license_plate,
            "state": self.state,
            "mileage": self.mileage,
            "primary_use": self.primary_use,
            "garage_location": self.garage_location,
        }


@dataclass
class AuditPacket:
    """Audit packet for blockchain commitment."""
    event_type: AuditEventType
    policy_id: UUID
    commitment_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "policy_id": str(self.policy_id),
            "commitment_hash": self.commitment_hash,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    def to_on_chain_record(self) -> dict[str, Any]:
        """Format for blockchain PolicyRegistry contract."""
        return {
            "policy_id": str(self.policy_id),
            "commitment_hash": self.commitment_hash,
            "status": self.event_type,
            "committed_at": self.created_at.isoformat(),
        }


@dataclass
class BindRequest:
    """Bind request for human approval."""
    quote_id: UUID
    policy_id: UUID
    policy_holder: PolicyHolder
    vehicle: VehicleInfo
    coverages: list[Coverage]
    total_premium: float
    effective_date: datetime
    expiration_date: datetime
    bind_method: BindMethod
    ai_confidence: float = 0.0
    reason_codes: list[str] = field(default_factory=list)
    limits_applied: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "quote_id": str(self.quote_id),
            "policy_id": str(self.policy_id),
            "policy_holder": self.policy_holder.to_dict(),
            "vehicle": self.vehicle.to_dict(),
            "coverages": [c.to_dict() for c in self.coverages],
            "total_premium": self.total_premium,
            "effective_date": self.effective_date.isoformat(),
            "expiration_date": self.expiration_date.isoformat(),
            "bind_method": self.bind_method,
            "ai_confidence": self.ai_confidence,
            "reason_codes": self.reason_codes,
            "limits_applied": self.limits_applied,
        }


@dataclass
class ApprovalRequest:
    """Human approval request."""
    bind_request: BindRequest
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    approver: str = ""
    comments: str = ""
    approved_at: datetime | None = None
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))

    def to_dict(self) -> dict[str, Any]:
        return {
            "bind_request": self.bind_request.to_dict(),
            "approval_status": self.approval_status,
            "approver": self.approver,
            "comments": self.comments,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "expires_at": self.expires_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Pydantic models for API
# ---------------------------------------------------------------------------


class PolicyStateTransition(BaseModel):
    """Valid state transitions."""
    from_state: PolicyState
    to_state: PolicyState
    requires_approval: bool = False
    description: str = ""


class PolicyLifecycle(BaseModel):
    """Policy lifecycle definition."""
    states: list[PolicyStateTransition] = field(default_factory=list)

    def get_valid_transitions(self, state: PolicyState) -> list[PolicyState]:
        """Get valid transitions from a state."""
        return [t.to_state for t in self.states if t.from_state == state]

    def is_valid_transition(self, from_state: PolicyState, to_state: PolicyState) -> bool:
        """Check if a transition is valid."""
        return any(
            t.from_state == from_state and t.to_state == to_state
            for t in self.states
        )


class PolicyDocument(BaseModel):
    """Policy document."""
    type: PolicyDocumentType
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BindRequestInput(BaseModel):
    """Input for bind request."""
    quote_id: UUID
    effective_date: datetime
    expiration_date: datetime
    bind_method: BindMethod = BindMethod.HUMAN_APPROVAL
    ai_confidence: float = 0.0


class ApprovalDecision(BaseModel):
    """Human approval decision."""
    approval_status: ApprovalStatus
    approver: str
    comments: str = ""


class PolicyTransitionError(Exception):
    """Raised when an invalid policy state transition is attempted."""

    def __init__(self, message: str, from_state: PolicyState | None = None, to_state: PolicyState | None = None):
        self.message = message
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(message)


class BindRequestOutput(BaseModel):
    """Output for bind request."""
    bind_request: BindRequest
    approval_request: ApprovalRequest | None = None
    message: str = ""


class PolicyResponse(BaseModel):
    """Policy API response."""
    policy_id: UUID
    state: PolicyState
    policy_holder: PolicyHolder
    vehicle: VehicleInfo
    coverages: list[Coverage]
    total_premium: float
    effective_date: datetime
    expiration_date: datetime
    bind_date: datetime | None = None
    cancellation_date: datetime | None = None
    bind_method: BindMethod | None = None
    audit_packets: list[AuditPacket] = field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
