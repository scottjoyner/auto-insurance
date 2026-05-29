"""Risk appetite service API."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from insurance_security.fastapi import ActorContext, Role, require_roles
from risk_appetite_service.config.settings import settings
from risk_appetite_service.domain.models import RiskAppetitePolicy
from risk_appetite_service.engine.risk_engine import RiskAppetiteEngine

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Risk Appetite Service",
    description="Risk appetite policy evaluation for insurance quotes",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

_engine: RiskAppetiteEngine | None = None
_policy: RiskAppetitePolicy | None = None


def get_engine() -> RiskAppetiteEngine:
    if _engine is None:
        raise RuntimeError("RiskAppetiteEngine not initialized.")
    return _engine


def init_engine(policy: RiskAppetitePolicy) -> None:
    global _engine, _policy
    _engine = RiskAppetiteEngine(policy)
    _policy = policy


assess_actor = require_roles(Role.AGENT, Role.UNDERWRITER_L1, Role.UNDERWRITER_L2, Role.SYSTEM)
policy_actor = require_roles(Role.UNDERWRITER_L1, Role.UNDERWRITER_L2, Role.SYSTEM)
policy_admin_actor = require_roles(Role.UNDERWRITER_L2, Role.ADMIN, Role.SYSTEM)


class RiskAssessmentRequest(BaseModel):
    quote_id: str = Field(description="Quote to assess")
    quote_data: dict[str, Any] = Field(description="Quote data")
    portfolio_state: dict[str, Any] = Field(description="Portfolio state")


class RiskAssessmentResponse(BaseModel):
    assessment_id: str
    quote_id: str
    decision: str
    risk_score: float
    risk_level: str
    triggered_rules: list[str]
    category_breakdown: dict[str, float]
    exposure_concentration: dict[str, Any]
    capital_impact: dict[str, Any]
    reinsurance_impact: dict[str, Any]
    limits_applied: dict[str, Any]
    reason_codes: list[str]
    assessed_at: str


class PolicyUpdateRequest(BaseModel):
    policy_data: dict[str, Any] = Field(description="New policy configuration")


@app.post("/assess", response_model=RiskAssessmentResponse)
def assess_risk(req: RiskAssessmentRequest, actor: ActorContext = Depends(assess_actor)):
    engine = get_engine()
    try:
        assessment = engine.assess(
            quote_id=UUID(req.quote_id),
            quote_data=req.quote_data,
            portfolio_state=req.portfolio_state,
        )
    except Exception as e:
        logger.error("Risk assessment failed: %s", e)
        raise HTTPException(status_code=500, detail="Risk assessment failed") from e

    logger.info("Risk assessment completed actor=%s quote_id=%s", actor.actor_id, req.quote_id)
    return RiskAssessmentResponse(**assessment.to_dict())


@app.post("/policy/update")
def update_policy(req: PolicyUpdateRequest, actor: ActorContext = Depends(policy_admin_actor)):
    if not settings.enable_runtime_policy_update:
        raise HTTPException(status_code=403, detail="Runtime policy changes are disabled")

    global _engine, _policy
    try:
        new_policy = RiskAppetitePolicy.from_dict(req.policy_data)
        _engine = RiskAppetiteEngine(new_policy)
        _policy = new_policy
        logger.warning("Risk policy changed actor=%s version=%s", actor.actor_id, new_policy.version)
        return {
            "status": "updated",
            "version": new_policy.version,
            "effective_date": new_policy.effective_date,
            "num_categories": len(new_policy.categories),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid policy") from e


@app.get("/policy")
def get_policy(actor: ActorContext = Depends(policy_actor)):
    _ = actor
    if _policy is None:
        raise HTTPException(status_code=503, detail="Policy not initialized")
    return {
        "version": _policy.version,
        "effective_date": _policy.effective_date,
        "categories": {
            k: {
                "name": v.name,
                "threshold_pct": v.threshold_pct,
                "warning_pct": v.warning_pct,
                "action": v.action_on_threshold,
            }
            for k, v in _policy.categories.items()
        },
        "capital_requirements": _policy.capital_requirements,
        "reinsurance": _policy.reinsurance,
    }


@app.get("/health")
def health():
    return {
        "service": "risk-appetite-service",
        "status": "healthy",
        "engine_initialized": _engine is not None,
        "auth_required": settings.require_auth,
        "runtime_policy_update_enabled": settings.enable_runtime_policy_update,
    }
