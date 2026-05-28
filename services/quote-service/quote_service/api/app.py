"""FastAPI application for the Quote Service."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from quote_service.engine.explainability import QuoteExplainability
from quote_service.engine.quote_engine import QuoteEngine

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Quote Service",
    description="Insurance quote generation, recalculation, and explainability",
    version="0.1.0",
)

# Global engine instance - would be configured via settings in production
_engine: QuoteEngine | None = None


def get_engine() -> QuoteEngine:
    global _engine
    if _engine is None:
        raise RuntimeError("QuoteEngine not initialized. Call init_engine() first.")
    return _engine


def init_engine(product_yaml_path: str) -> None:
    global _engine
    _engine = QuoteEngine(product_yaml_path)


# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------


class QuoteRequest(BaseModel):
    """Request to generate a new quote."""
    applicant_data: dict[str, Any] = Field(
        description="Applicant data (age, vehicle_year, coverage_type, etc.)"
    )
    product_id: str = Field(default="", description="Product ID (defaults to engine default)")
    product_version: str = Field(default="", description="Product version")
    jurisdiction: str = Field(default="", description="Jurisdiction code")
    validity_days: int = Field(default=30, ge=1, le=365, description="Quote validity in days")


class QuoteResponse(BaseModel):
    """Quote generation response."""
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
    """Request to recalculate an existing quote."""
    quote_id: str
    updated_applicant_data: dict[str, Any] = Field(
        description="Updated applicant data"
    )
    reason: str = Field(default="", description="Reason for recalculation")


class RecalculateResponse(BaseModel):
    """Recalculation response."""
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
    """Quote explainability report."""
    quote_id: str
    summary: dict[str, Any]
    premium_breakdown: dict[str, Any]
    factor_analysis: dict[str, Any]
    eligibility: dict[str, Any]
    referral: dict[str, Any]
    audit_trail: dict[str, Any]
    text_explanation: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/quotes", response_model=QuoteResponse)
def create_quote(req: QuoteRequest):
    """Generate a new insurance quote."""
    engine = get_engine()

    # Generate quote
    quote = engine.generate_quote(
        applicant_data=req.applicant_data,
        product_id=req.product_id or None,
        product_version=req.product_version or None,
        jurisdiction=req.jurisdiction or None,
        validity_days=req.validity_days,
    )

    return QuoteResponse(**quote.to_dict())


@app.post("/quotes/{quote_id}/recalculate", response_model=RecalculateResponse)
def recalculate_quote(quote_id: str, req: RecalculateRequest):
    """Recalculate a quote with updated applicant data."""
    engine = get_engine()

    request = engine.__class__.__dict__.get("_recalc_req")  # placeholder
    # In practice, we'd load the original quote from storage
    # For now, just demonstrate the recalculation flow
    from quote_service.domain.models import QuoteRecalculationRequest

    recalc_req = QuoteRecalculationRequest(
        quote_id=UUID(quote_id),
        updated_applicant_data=req.updated_applicant_data,
        reason=req.reason,
    )

    result = engine.recalculate_quote(recalc_req)
    return RecalculateResponse(**result.__dict__)


@app.get("/quotes/{quote_id}/explain", response_model=ExplainResponse)
def explain_quote(quote_id: str):
    """Get an explainability report for a quote."""
    engine = get_engine()
    # In practice, load quote from storage
    raise HTTPException(
        status_code=501,
        detail="Quote storage not implemented. Use generate_quote() directly.",
    )


@app.get("/quotes/{quote_id}/health")
def quote_health(quote_id: str):
    """Check if a quote is still valid (not expired)."""
    # In practice, load quote from storage
    raise HTTPException(
        status_code=501,
        detail="Quote storage not implemented.",
    )


@app.get("/health")
def health():
    """Service health check."""
    return {
        "service": "quote-service",
        "status": "healthy",
        "engine_initialized": _engine is not None,
    }
