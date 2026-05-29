"""Policy service API for persisted bind workflow."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from insurance_security.fastapi import ActorContext, Role, require_roles
from policy_service.compliance import evaluate_bind_request
from policy_service.config.settings import settings
from policy_service.storage.database import create_schema, get_session
from policy_service.storage.policy_repository import PolicyRepository

app = FastAPI(title="Policy Service", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "Idempotency-Key"],
)


@app.on_event("startup")
def startup_event():
    if settings.auto_create_schema:
        create_schema()


def get_repository(session: Session = Depends(get_session)) -> PolicyRepository:
    return PolicyRepository(session)


bind_actor = require_roles(Role.AGENT, Role.UNDERWRITER_L1, Role.UNDERWRITER_L2)
approval_actor = require_roles(Role.UNDERWRITER_L1, Role.UNDERWRITER_L2)
read_actor = require_roles(Role.AGENT, Role.UNDERWRITER_L1, Role.UNDERWRITER_L2)


class BindRequestInputAPI(BaseModel):
    quote_id: UUID
    effective_date: datetime
    expiration_date: datetime
    quote_snapshot: dict[str, Any] = Field(default_factory=dict)
    risk_assessment_snapshot: dict[str, Any] = Field(default_factory=dict)
    bind_method: str = "human_approval"
    request_key: str | None = None


class ApprovalDecisionAPI(BaseModel):
    approval_status: str
    comments: str = ""


class BindRequestResponse(BaseModel):
    bind_request_id: str
    quote_id: str
    policy_id: str
    status: str
    total_premium: float
    effective_date: str
    expiration_date: str
    request_key: str | None = None


class PolicyResponse(BaseModel):
    policy_id: str
    quote_id: str
    bind_request_id: str
    state: str
    total_premium: float
    effective_date: str
    expiration_date: str
    bound_by_actor_id: str
    bound_at: str


def _bind_response(record) -> BindRequestResponse:
    return BindRequestResponse(
        bind_request_id=record.bind_request_id,
        quote_id=record.quote_id,
        policy_id=record.policy_id,
        status=record.status,
        total_premium=record.total_premium,
        effective_date=record.effective_date.isoformat(),
        expiration_date=record.expiration_date.isoformat(),
        request_key=record.request_key,
    )


def _policy_response(record) -> PolicyResponse:
    return PolicyResponse(
        policy_id=record.policy_id,
        quote_id=record.quote_id,
        bind_request_id=record.bind_request_id,
        state=record.state,
        total_premium=record.total_premium,
        effective_date=record.effective_date.isoformat(),
        expiration_date=record.expiration_date.isoformat(),
        bound_by_actor_id=record.bound_by_actor_id,
        bound_at=record.bound_at.isoformat(),
    )


def _resolve_request_key(input_data: BindRequestInputAPI, header_key: str | None) -> str | None:
    return input_data.request_key or header_key


def _ensure_bind_compliance(input_data: BindRequestInputAPI) -> None:
    decision = evaluate_bind_request(input_data.quote_snapshot, input_data.risk_assessment_snapshot)
    if not decision.allowed:
        raise HTTPException(status_code=409, detail={"reason_codes": decision.reason_codes, "details": decision.details})


@app.post("/bind-requests", response_model=BindRequestResponse)
def create_bind_request(
    input_data: BindRequestInputAPI,
    actor: ActorContext = Depends(bind_actor),
    repository: PolicyRepository = Depends(get_repository),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> BindRequestResponse:
    """Create a persisted bind request from an accepted quote snapshot."""
    if input_data.expiration_date <= input_data.effective_date:
        raise HTTPException(status_code=400, detail="expiration_date must be after effective_date")
    _ensure_bind_compliance(input_data)
    record = repository.create_bind_request(
        quote_id=input_data.quote_id,
        effective_date=input_data.effective_date,
        expiration_date=input_data.expiration_date,
        quote_snapshot=input_data.quote_snapshot,
        risk_assessment_snapshot=input_data.risk_assessment_snapshot,
        actor_id=actor.actor_id,
        bind_method=input_data.bind_method,
        request_key=_resolve_request_key(input_data, idempotency_key),
    )
    return _bind_response(record)


@app.get("/bind-requests/{bind_request_id}", response_model=BindRequestResponse)
def get_bind_request(
    bind_request_id: UUID,
    actor: ActorContext = Depends(read_actor),
    repository: PolicyRepository = Depends(get_repository),
) -> BindRequestResponse:
    _ = actor
    record = repository.get_bind_request(bind_request_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Bind request not found")
    return _bind_response(record)


@app.post("/bind-requests/{bind_request_id}/approve", response_model=PolicyResponse)
def approve_bind_request(
    bind_request_id: UUID,
    decision: ApprovalDecisionAPI,
    actor: ActorContext = Depends(approval_actor),
    repository: PolicyRepository = Depends(get_repository),
) -> PolicyResponse:
    if decision.approval_status != "approved":
        rejected = repository.reject_bind_request(bind_request_id, actor_id=actor.actor_id, comments=decision.comments)
        if rejected is None:
            raise HTTPException(status_code=404, detail="Bind request not found")
        raise HTTPException(status_code=409, detail="Bind request rejected")
    policy = repository.approve_bind_request(bind_request_id, actor_id=actor.actor_id, comments=decision.comments)
    if policy is None:
        raise HTTPException(status_code=404, detail="Bind request not found or not approvable")
    return _policy_response(policy)


@app.post("/policies/bind", response_model=BindRequestResponse)
def compatibility_create_bind_request(
    input_data: BindRequestInputAPI,
    actor: ActorContext = Depends(bind_actor),
    repository: PolicyRepository = Depends(get_repository),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> BindRequestResponse:
    """Compatibility endpoint for earlier docs; delegates to bind request creation."""
    if input_data.expiration_date <= input_data.effective_date:
        raise HTTPException(status_code=400, detail="expiration_date must be after effective_date")
    _ensure_bind_compliance(input_data)
    record = repository.create_bind_request(
        quote_id=input_data.quote_id,
        effective_date=input_data.effective_date,
        expiration_date=input_data.expiration_date,
        quote_snapshot=input_data.quote_snapshot,
        risk_assessment_snapshot=input_data.risk_assessment_snapshot,
        actor_id=actor.actor_id,
        bind_method=input_data.bind_method,
        request_key=_resolve_request_key(input_data, idempotency_key),
    )
    return _bind_response(record)


@app.get("/policies/{policy_id}", response_model=PolicyResponse)
def get_policy(
    policy_id: UUID,
    actor: ActorContext = Depends(read_actor),
    repository: PolicyRepository = Depends(get_repository),
) -> PolicyResponse:
    _ = actor
    policy = repository.get_policy(policy_id)
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return _policy_response(policy)


@app.get("/policies", response_model=list[PolicyResponse])
def list_policies(
    state: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    actor: ActorContext = Depends(read_actor),
    repository: PolicyRepository = Depends(get_repository),
) -> list[PolicyResponse]:
    _ = actor
    return [_policy_response(policy) for policy in repository.list_policies(state=state, limit=limit)]


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "policy-service", "persistence": "sqlalchemy"}
