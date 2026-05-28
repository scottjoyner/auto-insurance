"""Risk appetite service API."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from risk_appetite_service.domain.models import RiskAppetitePolicy, RiskDecision
from risk_appetite_service.engine.risk_engine import RiskAppetiteEngine

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Risk Appetite Service",
    description="Risk appetite policy evaluation for insurance quotes",
    version="0.1.0",
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


# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------


class RiskAssessmentRequest(BaseModel):
    """Request for a risk appetite assessment."""
    quote_id: str = Field(description="Quote to assess")
    quote_data: dict[str, Any] = Field(
        description="Quote data (premium, coverages, applicant info)"
    )
    portfolio_state: dict[str, Any] = Field(
        description="Current portfolio state for concentration checks"
    )


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response."""
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
    """Request to update the risk appetite policy."""
    policy_data: dict[str, Any] = Field(
        description="New policy configuration"
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/assess", response_model=RiskAssessmentResponse)
def assess_risk(req: RiskAssessmentRequest):
    """Run a risk appetite assessment on a quote."""
    engine = get_engine()

    try:
        assessment = engine.assess(
            quote_id=UUID(req.quote_id),
            quote_data=req.quote_data,
            portfolio_state=req.portfolio_state,
        )
    except Exception as e:
        logger.error("Risk assessment failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    return RiskAssessmentResponse(**assessment.to_dict())


@app.post("/policy/update")
def update_policy(req: PolicyUpdateRequest):
    """Update the risk appetite policy."""
    global _engine, _policy
    try:
        new_policy = RiskAppetitePolicy.from_dict(req.policy_data)
        _engine = RiskAppetiteEngine(new_policy)
        _policy = new_policy
        return {
            "status": "updated",
            "version": new_policy.version,
            "effective_date": new_policy.effective_date,
            "num_categories": len(new_policy.categories),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid policy: {e}")


@app.get("/policy")
def get_policy():
    """Get the current risk appetite policy."""
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
    """Service health check."""
    return {
        "service": "risk-appetite-service",
        "status": "healthy",
        "engine_initialized": _engine is not None,
    }
