"""FastAPI application for the Quote Service."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from insurance_observability import CorrelationIdMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from insurance_security.fastapi import ActorContext, Role, require_roles
from quote_service.config.settings import settings
from quote_service.domain.models import QuoteStatus
from quote_service.engine.explainability import QuoteExplainability
from quote_service.engine.quote_engine import QuoteEngine
from quote_service.integrations.customer_validation import validate_actor_customer
from quote_service.security.ownership import require_quote_access, scoped_quote_query, stamp_quote_owner
from quote_service.storage.database import create_schema, get_session
from quote_service.storage.orm import QuoteRecord
from quote_service.storage.quote_repository import QuoteRepository

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Quote Service",
    description="Insurance quote generation, recalculation, and explainability",
    version="0.1.0",
)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

_engine: QuoteEngine | None = None


@app.on_event("startup")
def startup_event():
    if settings.auto_create_schema:
        create_schema()
    if _engine is None:
        init_engine(settings.default_product_yaml)


def get_engine() -> QuoteEngine:
    global _engine
    if _engine is None:
        raise RuntimeError("QuoteEngine not initialized. Call init_engine() first.")
    return _engine


def init_engine(product_yaml_path: str) -> None:
    global _engine
    _engine = QuoteEngine(product_yaml_path)


def get_quote_repository(session: Session = Depends(get_session)) -> QuoteRepository:
    return QuoteRepository(session)


def validate_customer_if_enabled(actor: ActorContext) -> None:
    if not settings.validate_customer:
        return
    validate_actor_customer(
        actor=actor,
        customer_service_url=settings.customer_service_url,
        bearer_token=f"dev:{actor.actor_id}:{','.join(sorted(actor.roles))}:{actor.tenant_id or ''}:{actor.customer_id or ''}",
        timeout=settings.customer_validation_timeout_seconds,
    )


quote_write_actor = require_roles(Role.CUSTOMER, Role.AGENT, Role.UNDERWRITER_L1)
quote_read_actor = require_roles(Role.CUSTOMER, Role.AGENT, Role.UNDERWRITER_L1, Role.UNDERWRITER_L2)
quote_accept_actor = require_roles(Role.AGENT, Role.UNDERWRITER_L1, Role.UNDERWRITER_L2)


class QuoteRequest(BaseModel):
    applicant_data: dict[str, Any] = Field(description="Applicant data")
    product_id: str = Field(default="", description="Product ID")
    product_version: str = Field(default="", description="Product version")
    jurisdiction: str = Field(default="", description="Jurisdiction code")
    validity_days: int = Field(default=30, ge=1, le=365, description="Quote validity in days")


class QuoteResponse(BaseModel):
    quote_id: str
    product_id: str
    product_version: str
    jurisdiction: str
    status: str
    total_premium: float
    coverages: dict[str, float]
    reason_codes: list[str]
    surcharges_applied: list[str]
    discounts_applied: list[str]
    bind_eligible: bool
    referral_flag: str
    referral_reason: str
    expires_at: str
    created_at: str
    rating_result_hash: str
    input_snapshot_hash: str
    ai_confidence_score: float | None = None


class RecalculateRequest(BaseModel):
    updated_applicant_data: dict[str, Any] = Field(description="Updated applicant data")
    reason: str = Field(default="", description="Reason for recalculation")


class RecalculateResponse(BaseModel):
    quote_id: str
    previous_premium: float
    new_premium: float
    premium_change: float
    premium_change_pct: float
    changed_factors: list[str]
    new_surcharges: list[str]
    new_discounts: list[str]
    new_reason_codes: list[str]
    new_bind_eligible: bool
    new_referral_flag: str
    recalculation_hash: str


class ExplainResponse(BaseModel):
    quote_id: str
    summary: dict[str, Any]
    premium_breakdown: dict[str, Any]
    factor_analysis: dict[str, Any]
    eligibility: dict[str, Any]
    referral: dict[str, Any]
    audit_trail: dict[str, Any]
    text_explanation: str


def _record_to_response(repository: QuoteRepository, record: QuoteRecord) -> QuoteResponse:
    return QuoteResponse(**repository._to_domain(record).to_dict())


@app.post("/quotes", response_model=QuoteResponse)
def create_quote(
    req: QuoteRequest,
    actor: ActorContext = Depends(quote_write_actor),
    repository: QuoteRepository = Depends(get_quote_repository),
):
    validate_customer_if_enabled(actor)
    engine = get_engine()
    quote = engine.generate_quote(
        applicant_data=req.applicant_data,
        product_id=req.product_id or None,
        product_version=req.product_version or None,
        jurisdiction=req.jurisdiction or None,
        validity_days=req.validity_days,
    )
    quote._applicant_data = dict(req.applicant_data)
    persisted = repository.save(quote, actor_id=actor.actor_id)
    stamp_quote_owner(repository.session, str(persisted.quote_id), actor)
    logger.info("Quote generated by actor=%s quote_id=%s", actor.actor_id, persisted.quote_id)
    return QuoteResponse(**persisted.to_dict())


@app.get("/quotes", response_model=list[QuoteResponse])
def list_quotes(
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    actor: ActorContext = Depends(quote_read_actor),
    repository: QuoteRepository = Depends(get_quote_repository),
):
    parsed_status = QuoteStatus(status) if status else None
    query = scoped_quote_query(repository.session, actor).order_by(QuoteRecord.created_at.desc())
    if parsed_status is not None:
        query = query.filter(QuoteRecord.status == str(parsed_status))
    return [_record_to_response(repository, record) for record in query.limit(limit).all()]


@app.get("/quotes/{quote_id}", response_model=QuoteResponse)
def get_quote(
    quote_id: str,
    actor: ActorContext = Depends(quote_read_actor),
    repository: QuoteRepository = Depends(get_quote_repository),
):
    require_quote_access(repository.session, quote_id, actor)
    quote = repository.get(quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    return QuoteResponse(**quote.to_dict())


@app.post("/quotes/{quote_id}/accept", response_model=QuoteResponse)
def accept_quote(
    quote_id: str,
    actor: ActorContext = Depends(quote_accept_actor),
    repository: QuoteRepository = Depends(get_quote_repository),
):
    require_quote_access(repository.session, quote_id, actor)
    quote = repository.get(quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    if not quote.bind_eligible:
        raise HTTPException(status_code=409, detail="Quote is not bind eligible")
    accepted = repository.accept(quote_id, actor_id=actor.actor_id)
    if accepted is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    if accepted.status == QuoteStatus.EXPIRED:
        raise HTTPException(status_code=409, detail="Quote expired before acceptance")
    return QuoteResponse(**accepted.to_dict())


@app.post("/quotes/{quote_id}/recalculate", response_model=RecalculateResponse)
def recalculate_quote(
    quote_id: str,
    req: RecalculateRequest,
    actor: ActorContext = Depends(require_roles(Role.AGENT, Role.UNDERWRITER_L1, Role.UNDERWRITER_L2)),
    repository: QuoteRepository = Depends(get_quote_repository),
):
    require_quote_access(repository.session, quote_id, actor)
    existing = repository.get(quote_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Quote not found")

    engine = get_engine()
    from quote_service.domain.models import QuoteRecalculationRequest

    recalc_req = QuoteRecalculationRequest(
        quote_id=UUID(quote_id),
        updated_applicant_data=req.updated_applicant_data,
        reason=req.reason,
    )
    result = engine.recalculate_quote(recalc_req)
    result.previous_premium = existing.total_premium
    result.premium_change = result.new_premium - existing.total_premium
    result.premium_change_pct = (result.premium_change / existing.total_premium) * 100 if existing.total_premium else 0.0
    logger.info("Quote recalculated by actor=%s quote_id=%s", actor.actor_id, quote_id)
    return RecalculateResponse(**result.__dict__)


@app.get("/quotes/{quote_id}/explain", response_model=ExplainResponse)
def explain_quote(
    quote_id: str,
    actor: ActorContext = Depends(quote_read_actor),
    repository: QuoteRepository = Depends(get_quote_repository),
):
    require_quote_access(repository.session, quote_id, actor)
    quote = repository.get(quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    report = QuoteExplainability.explain(quote)
    report["text_explanation"] = QuoteExplainability.explain_text(quote)
    return ExplainResponse(**report)


@app.get("/quotes/{quote_id}/health")
def quote_health(
    quote_id: str,
    actor: ActorContext = Depends(quote_read_actor),
    repository: QuoteRepository = Depends(get_quote_repository),
):
    require_quote_access(repository.session, quote_id, actor)
    quote = repository.get(quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    return {
        "quote_id": str(quote.quote_id),
        "status": quote.status,
        "is_expired": quote.is_expired(),
        "expires_at": quote.expires_at.isoformat(),
        "bind_eligible": quote.bind_eligible,
    }


@app.get("/health")
def health():
    return {
        "service": "quote-service",
        "status": "healthy",
        "engine_initialized": _engine is not None,
        "auth_required": settings.require_auth,
        "persistence": "sqlalchemy",
        "customer_validation_enabled": settings.validate_customer,
    }
