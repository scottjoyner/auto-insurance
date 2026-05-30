"""Claims service API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from insurance_documents import render_adverse_action_notice
from insurance_observability import CorrelationIdMiddleware
from insurance_security.fastapi import ActorContext, Role, require_roles
from insurance_security.settings import validate_security_settings
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from claims_service.config import settings
from claims_service.database import create_schema, get_session
from claims_service.integrations.customer_validation import validate_actor_customer
from claims_service.models import ClaimRecord
from claims_service.repository import ClaimsRepository

app = FastAPI(title="Claims Service", version="0.1.0")
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.on_event("startup")
def startup_event():
    validate_security_settings()
    if settings.auto_create_schema:
        create_schema()


def get_repository(session: Session = Depends(get_session)) -> ClaimsRepository:
    return ClaimsRepository(session)


def validate_customer_if_enabled(actor: ActorContext) -> None:
    if not settings.validate_customer:
        return
    validate_actor_customer(
        actor=actor,
        customer_service_url=settings.customer_service_url,
        bearer_token=f"dev:{actor.actor_id}:{','.join(sorted(actor.roles))}:{actor.tenant_id or ''}:{actor.customer_id or ''}",
        timeout=settings.customer_validation_timeout_seconds,
    )


claim_write_actor = require_roles(Role.CUSTOMER, Role.AGENT, Role.CLAIMS_MANAGER, Role.SYSTEM)
claim_read_actor = require_roles(Role.CUSTOMER, Role.AGENT, Role.CLAIMS_MANAGER, Role.SYSTEM)
claim_manager_actor = require_roles(Role.CLAIMS_MANAGER, Role.SYSTEM)


class FNOLRequest(BaseModel):
    policy_id: str
    loss_type: str
    loss_date: datetime
    loss_location: str = ""
    description: str = ""
    police_report_indicator: bool = False
    injuries_indicator: bool = False
    preferred_contact_method: str = "email"
    additional_data: dict[str, Any] = Field(default_factory=dict)


class EvidenceRequest(BaseModel):
    evidence_type: str
    source: str = "customer"
    uri: str = ""
    checksum: str = ""
    visibility: str = "internal"


class ReserveRequest(BaseModel):
    amount: float = Field(gt=0)
    reason: str = ""


class DenialReviewRequest(BaseModel):
    reason: str
    customer_name: str = "Customer"
    jurisdiction: str = "UNKNOWN"
    reason_codes: list[str] = Field(default_factory=list)


class ClaimResponse(BaseModel):
    claim_id: str
    tenant_id: str | None = None
    customer_id: str | None = None
    policy_id: str
    status: str
    severity: str
    queue: str
    loss_type: str
    loss_date: str
    loss_location: str
    description: str
    injuries_indicator: bool
    police_report_indicator: bool
    created_at: str


class EvidenceResponse(BaseModel):
    evidence_id: str
    claim_id: str
    evidence_type: str
    source: str
    uri: str
    checksum: str
    visibility: str
    uploaded_at: str


class ReserveResponse(BaseModel):
    id: int
    claim_id: str
    amount: float
    reason: str
    status: str
    recommended_by_actor_id: str
    approved_by_actor_id: str | None = None


class DenialReviewResponse(BaseModel):
    claim: ClaimResponse
    adverse_action_notice_draft: str


def _claim_response(record: ClaimRecord) -> ClaimResponse:
    return ClaimResponse(
        claim_id=record.claim_id,
        tenant_id=record.tenant_id,
        customer_id=record.customer_id,
        policy_id=record.policy_id,
        status=record.status,
        severity=record.severity,
        queue=record.queue,
        loss_type=record.loss_type,
        loss_date=record.loss_date.isoformat(),
        loss_location=record.loss_location,
        description=record.description,
        injuries_indicator=record.injuries_indicator,
        police_report_indicator=record.police_report_indicator,
        created_at=record.created_at.isoformat(),
    )


def _require_claim_access(record: ClaimRecord | None, actor: ActorContext) -> ClaimRecord:
    if record is None:
        raise HTTPException(status_code=404, detail="Claim not found")
    if not actor.can_access_customer(record.customer_id, record.tenant_id):
        raise HTTPException(status_code=403, detail="Claim access denied")
    return record


@app.post("/claims/fnol", response_model=ClaimResponse)
def create_fnol(
    request: FNOLRequest,
    actor: ActorContext = Depends(claim_write_actor),
    repository: ClaimsRepository = Depends(get_repository),
):
    validate_customer_if_enabled(actor)
    claim = repository.create_fnol(
        policy_id=request.policy_id,
        tenant_id=actor.tenant_id,
        customer_id=actor.customer_id,
        loss_type=request.loss_type,
        loss_date=request.loss_date,
        loss_location=request.loss_location,
        description=request.description,
        police_report_indicator=request.police_report_indicator,
        injuries_indicator=request.injuries_indicator,
        preferred_contact_method=request.preferred_contact_method,
        fnol_payload=request.model_dump(mode="json"),
        actor_id=actor.actor_id,
    )
    return _claim_response(claim)


@app.get("/claims", response_model=list[ClaimResponse])
def list_claims(
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    actor: ActorContext = Depends(claim_read_actor),
    repository: ClaimsRepository = Depends(get_repository),
):
    tenant_id = None if actor.is_privileged() else actor.tenant_id
    customer_id = None if actor.is_privileged() else actor.customer_id
    records = repository.list(tenant_id=tenant_id, customer_id=customer_id, status=status, limit=limit)
    return [_claim_response(record) for record in records]


@app.get("/claims/{claim_id}", response_model=ClaimResponse)
def get_claim(
    claim_id: str,
    actor: ActorContext = Depends(claim_read_actor),
    repository: ClaimsRepository = Depends(get_repository),
):
    record = _require_claim_access(repository.get(claim_id), actor)
    return _claim_response(record)


@app.post("/claims/{claim_id}/evidence", response_model=EvidenceResponse)
def add_evidence(
    claim_id: str,
    request: EvidenceRequest,
    actor: ActorContext = Depends(claim_write_actor),
    repository: ClaimsRepository = Depends(get_repository),
):
    _require_claim_access(repository.get(claim_id), actor)
    evidence = repository.add_evidence(
        claim_id=claim_id,
        evidence_type=request.evidence_type,
        source=request.source,
        uri=request.uri,
        checksum=request.checksum,
        visibility=request.visibility,
        actor_id=actor.actor_id,
    )
    return EvidenceResponse(
        evidence_id=evidence.evidence_id,
        claim_id=evidence.claim_id,
        evidence_type=evidence.evidence_type,
        source=evidence.source,
        uri=evidence.uri,
        checksum=evidence.checksum,
        visibility=evidence.visibility,
        uploaded_at=evidence.uploaded_at.isoformat(),
    )


@app.post("/claims/{claim_id}/reserves", response_model=ReserveResponse)
def recommend_reserve(
    claim_id: str,
    request: ReserveRequest,
    actor: ActorContext = Depends(require_roles(Role.AGENT, Role.CLAIMS_MANAGER, Role.SYSTEM)),
    repository: ClaimsRepository = Depends(get_repository),
):
    _require_claim_access(repository.get(claim_id), actor)
    reserve = repository.recommend_reserve(claim_id=claim_id, amount=request.amount, reason=request.reason, actor_id=actor.actor_id)
    return ReserveResponse(
        id=reserve.id,
        claim_id=reserve.claim_id,
        amount=reserve.amount,
        reason=reserve.reason,
        status=reserve.status,
        recommended_by_actor_id=reserve.recommended_by_actor_id,
        approved_by_actor_id=reserve.approved_by_actor_id,
    )


@app.post("/claims/reserves/{reserve_id}/approve", response_model=ReserveResponse)
def approve_reserve(
    reserve_id: int,
    actor: ActorContext = Depends(claim_manager_actor),
    repository: ClaimsRepository = Depends(get_repository),
):
    reserve = repository.approve_reserve(reserve_id=reserve_id, actor_id=actor.actor_id)
    if reserve is None:
        raise HTTPException(status_code=404, detail="Reserve not found")
    _require_claim_access(repository.get(reserve.claim_id), actor)
    return ReserveResponse(
        id=reserve.id,
        claim_id=reserve.claim_id,
        amount=reserve.amount,
        reason=reserve.reason,
        status=reserve.status,
        recommended_by_actor_id=reserve.recommended_by_actor_id,
        approved_by_actor_id=reserve.approved_by_actor_id,
    )


@app.post("/claims/{claim_id}/denial-review", response_model=DenialReviewResponse)
def request_denial_review(
    claim_id: str,
    request: DenialReviewRequest,
    actor: ActorContext = Depends(claim_manager_actor),
    repository: ClaimsRepository = Depends(get_repository),
):
    claim = _require_claim_access(repository.get(claim_id), actor)
    updated = repository.mark_denial_review(claim_id=claim.claim_id, reason=request.reason, actor_id=actor.actor_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Claim not found")
    reason_codes = request.reason_codes or ["claim_denial_pending_manager_review"]
    notice = render_adverse_action_notice(
        customer_name=request.customer_name,
        quote_id=claim.claim_id,
        jurisdiction=request.jurisdiction,
        reason_codes=reason_codes,
        details={"claim_id": claim.claim_id, "reason": request.reason},
    )
    return DenialReviewResponse(claim=_claim_response(updated), adverse_action_notice_draft=notice)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "claims-service",
        "persistence": "sqlalchemy",
        "customer_validation_enabled": settings.validate_customer,
    }
