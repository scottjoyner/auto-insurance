"""Policy service API - FastAPI application for policy lifecycle management."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from policy_service.config.settings import settings
from policy_service.domain.models import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
    BindMethod,
    BindRequest,
    BindRequestInput,
    BindRequestOutput,
    PolicyDocumentType,
    PolicyResponse,
    PolicyState,
)
from policy_service.engine.policy_engine import PolicyEngine
from policy_service.storage.policy_store import store

logger = logging.getLogger(__name__)

app = FastAPI(title="Policy Service", version="0.1.0")
engine = PolicyEngine()


# ---------------------------------------------------------------------------
# API models
# ---------------------------------------------------------------------------


class BindRequestInputAPI(BaseModel):
    """API input for bind request."""
    quote_id: UUID
    effective_date: datetime
    expiration_date: datetime
    bind_method: BindMethod = BindMethod.HUMAN_APPROVAL
    ai_confidence: float = 0.0


class ApprovalDecisionAPI(BaseModel):
    """API input for approval decision."""
    approval_status: str
    approver: str
    comments: str = ""


class PolicyQuery(BaseModel):
    """API input for policy query."""
    state: PolicyState | None = None


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@app.post("/policies/bind", response_model=BindRequestOutput)
async def create_bind_request(input_data: BindRequestInputAPI) -> BindRequestOutput:
    """Create a bind request from a quote."""
    # Get quote data (in MVP, we simulate this)
    quote_data = {
        "policy_holder_name": "John Doe",
        "policy_holder_address": "123 Main St, Sample, NC",
        "policy_holder_phone": "555-1234",
        "policy_holder_email": "john@example.com",
        "driver_license": "DL123456",
        "date_of_birth": "1990-01-01",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_year": 2023,
        "vehicle_vin": "1HGBH41JXMN109186",
        "license_plate": "ABC123",
        "vehicle_state": "NC",
        "vehicle_mileage": 15000,
        "vehicle_primary_use": "commute",
        "garage_location": "123 Main St, Sample, NC",
        "coverages": [
            {"type": "liability", "limit": 50000, "deductible": 500, "premium": 500.0},
            {"type": "collision", "limit": 25000, "deductible": 500, "premium": 400.0},
            {"type": "comprehensive", "limit": 25000, "deductible": 500, "premium": 200.0},
        ],
        "total_premium": 1100.0,
    }

    bind_request = engine.create_bind_request(input_data, quote_data)

    # Create approval request
    approval_request = engine.create_approval_request(bind_request, settings.approval_request_expiry_hours)

    return BindRequestOutput(
        bind_request=bind_request,
        approval_request=approval_request,
        message="Bind request created. Approval required.",
    )


@app.post("/policies/{policy_id}/approve")
async def approve_bind_request(
    policy_id: UUID,
    decision: ApprovalDecisionAPI,
) -> dict[str, Any]:
    """Process a human approval decision for a bind request."""
    # Get the bind request from store (in MVP, we simulate this)
    approval_request = ApprovalRequest(
        bind_request=BindRequest(
            quote_id=UUID("00000000-0000-0000-0000-000000000000"),
            policy_id=policy_id,
            policy_holder=None,  # type: ignore
            vehicle=None,  # type: ignore
            coverages=[],
            total_premium=0.0,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow(),
            bind_method=BindMethod.HUMAN_APPROVAL,
        ),
        approval_status=ApprovalStatus.PENDING,
    )

    approval_decision = ApprovalDecision(
        approval_status=decision.approval_status,
        approver=decision.approver,
        comments=decision.comments,
    )

    result = engine.process_approval(approval_request, approval_decision)

    if result["success"] and decision.approval_status == "approved":
        # Create policy in store
        policy = store.create_policy(
            policy_id=policy_id,
            state=PolicyState.ACTIVE,
            policy_holder=approval_request.bind_request.policy_holder,
            vehicle=approval_request.bind_request.vehicle,
            coverages=approval_request.bind_request.coverages,
            total_premium=approval_request.bind_request.total_premium,
            effective_date=approval_request.bind_request.effective_date,
            expiration_date=approval_request.bind_request.expiration_date,
        )
        return {"success": True, "message": "Policy bound successfully", "policy": policy}

    return result


@app.post("/policies/{policy_id}/transition")
async def transition_policy_state(
    policy_id: UUID,
    target_state: str,
) -> dict[str, Any]:
    """Transition a policy to a new state."""
    current_policy = store.get_policy(policy_id)
    if not current_policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    current_state = PolicyState(current_policy["state"])
    target = PolicyState(target_state)

    result = engine.transition_state(current_state, target, policy_id)

    if result["success"]:
        store.update_policy_state(policy_id, target)
        if result["audit_packet"]:
            store.add_audit_packet(policy_id, result["audit_packet"])
        return {"success": True, "new_state": target, "audit_packet": result["audit_packet"]}

    raise HTTPException(status_code=400, detail=result.get("message", "Transition failed"))


@app.get("/policies/{policy_id}")
async def get_policy(policy_id: UUID) -> dict[str, Any]:
    """Get a policy by ID."""
    policy = store.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    packets = store.get_audit_packets(policy_id)
    documents = store.get_documents(policy_id)

    return {
        **policy,
        "audit_packets": [p.to_dict() for p in packets],
        "documents": documents,
    }


@app.get("/policies")
async def list_policies(state: PolicyState | None = None) -> list[dict[str, Any]]:
    """List policies, optionally filtered by state."""
    return store.list_policies(state)


@app.post("/policies/{policy_id}/documents")
async def add_policy_document(
    policy_id: UUID,
    doc_type: PolicyDocumentType,
    content: str,
    metadata: dict[str, Any] = {},
) -> dict[str, Any]:
    """Add a policy document."""
    policy = store.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    doc = store.add_document(
        policy_id=policy_id,
        doc_type=doc_type,
        content=content,
        metadata=metadata,
    )
    return doc


@app.get("/policies/{policy_id}/documents")
async def get_policy_documents(policy_id: UUID) -> list[dict[str, Any]]:
    """Get all documents for a policy."""
    policy = store.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    return store.get_documents(policy_id)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "policy-service"}
