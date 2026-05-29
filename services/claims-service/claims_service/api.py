"""Claims service API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from insurance_observability import CorrelationIdMiddleware
from insurance_security.fastapi import ActorContext, Role, require_roles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from claims_service.config import settings
from claims_service.database import create_schema, get_session
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
    if settings.auto_create_schema:
        create_schema()


def get_repository(session: Session = Depends(get_session)) -> ClaimsRepository:
    return ClaimsRepository(session)


claim_write_actor = require_roles(Role.CUSTOMER, Role.AGENT, Role.CLAIMS_MANAGER, Role.SYSTEM)
claim_read_actor = require_roles(Role.CUSTOMER, Role.AGENT, Role.CLAIMS_MANAGER, Role.SYSTEM)


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


@app.get("/health")
def health():
    return {"status": "healthy", "service": "claims-service", "persistence": "sqlalchemy"}
