"""Blockchain gateway FastAPI application.

Provides endpoints for other services to:
- Commit policies to the blockchain
- Record audit events
- Query on-chain state
- Manage the outbox
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from blockchain_gateway.config.settings import settings
from blockchain_gateway.gateway import (
    BlockchainGateway,
    BlockchainGatewayError,
    PolicyStatus,
    AuditEventType,
)
from blockchain_gateway.outbox import OutboxStore, OutboxEntry
from blockchain_gateway.signer_policy import (
    SignerPolicyManager,
    SignerPolicyError,
    PolicyAction,
)
from blockchain_gateway.reconciliation import Reconciler
import json

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Blockchain Gateway",
    version="0.1.0",
    description="Wraps PolicyRegistry and AuditEventRegistry contracts with outbox pattern.",
)

# Initialize components
gateway = BlockchainGateway(
    rpc_url=settings.rpc_url,
    policy_registry_address=settings.policy_registry_address,
    audit_event_registry_address=settings.audit_event_registry_address,
    signer_address="",  # Set from env or config
    signer_private_key=settings.signer_private_key,
)

outbox_store = OutboxStore(settings.outbox_db_path)
signer_policy = SignerPolicyManager()
reconciler: Reconciler | None = None  # Set during startup


# ---------------------------------------------------------------------------
# API models
# ---------------------------------------------------------------------------


class CommitPolicyRequest(BaseModel):
    """Request to commit a policy to the blockchain."""
    policy_id: str
    commitment_hash: str
    status: str = "PENDING"  # PENDING, ACTIVE, ENDORSEMENT, CANCELLED, EXPIRED


class RecordEventRequest(BaseModel):
    """Request to record an audit event on the blockchain."""
    event_type: str  # BIND, ENDORSEMENT, CANCELLATION, RENEWAL, CLAIM_FILING, CLAIM_SETTLEMENT
    policy_id: str
    commitment_hash: str


class UpdateStatusRequest(BaseModel):
    """Request to update a policy status."""
    policy_id: str
    status: str  # PENDING, ACTIVE, ENDORSEMENT, CANCELLED, EXPIRED


class PolicyResponse(BaseModel):
    """Policy record from on-chain."""
    policy_id: str
    commitment_hash: str
    status: str
    committed_at: int
    committed_by: str


class OutboxStatsResponse(BaseModel):
    """Outbox statistics."""
    pending: int
    submitted: int
    committed: int
    failed: int


class ReconciliationReportResponse(BaseModel):
    """Reconciliation report."""
    timestamp: str
    window_hours: int
    local_events_count: int
    chain_events_count: int
    missing_from_chain: list[str]
    missing_from_local: list[str]
    hash_mismatches: list[str]
    discrepancies: list[str]
    is_clean: bool


# ---------------------------------------------------------------------------
# Event listeners (for polling outbox)
# ---------------------------------------------------------------------------


def _poll_outbox_and_submit():
    """Background task: poll outbox and submit pending entries."""
    import time

    while True:
        try:
            pending = outbox_store.get_pending_entries(limit=10)
            if not pending:
                time.sleep(settings.outbox_poll_interval_seconds)
                continue

            for entry in pending:
                try:
                    payload = json.loads(entry.payload)
                    if entry.contract == "audit_event_registry":
                        tx_hash = gateway.record_event(
                            event_type=AuditEventType[entry.event_type],
                            policy_id=payload["policy_id"],
                            commitment_hash=payload["commitment_hash"],
                        )
                        outbox_store.mark_submitted(entry.id, tx_hash)
                        logger.info("Outbox entry submitted: %s tx=%s", entry.id, tx_hash)
                    else:
                        status_map = {
                            "PENDING": PolicyStatus.PENDING,
                            "ACTIVE": PolicyStatus.ACTIVE,
                            "ENDORSEMENT": PolicyStatus.ENDORSEMENT,
                            "CANCELLED": PolicyStatus.CANCELLED,
                            "EXPIRED": PolicyStatus.EXPIRED,
                        }
                        status = status_map.get(entry.method, PolicyStatus.PENDING)
                        tx_hash = gateway.commit_policy(
                            policy_id=payload["policy_id"],
                            commitment_hash=payload["commitment_hash"],
                            status=status,
                        )
                        outbox_store.mark_submitted(entry.id, tx_hash)
                        logger.info("Outbox entry submitted: %s tx=%s", entry.id, tx_hash)

                except BlockchainGatewayError as e:
                    outbox_store.mark_failed(entry.id, str(e))
                    logger.error("Outbox entry failed: %s error=%s", entry.id, e)
                except Exception as e:
                    outbox_store.mark_failed(entry.id, str(e))
                    logger.error("Outbox entry error: %s error=%s", entry.id, e)

        except Exception as e:
            logger.error("Outbox poll error: %s", e)

        time.sleep(settings.outbox_poll_interval_seconds)


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@app.post("/policies/commit")
async def api_commit_policy(request: CommitPolicyRequest) -> dict[str, Any]:
    """Commit a policy to the blockchain (direct, no outbox)."""
    signer_addr = gateway.signer_address
    if not signer_addr:
        raise HTTPException(status_code=500, detail="Signer not configured")
    try:
        signer_policy.enforce(signer_addr, PolicyAction.COMMIT_POLICY)
    except SignerPolicyError as e:
        raise HTTPException(status_code=403, detail=str(e))

    try:
        status_map = {
            "PENDING": PolicyStatus.PENDING,
            "ACTIVE": PolicyStatus.ACTIVE,
            "ENDORSEMENT": PolicyStatus.ENDORSEMENT,
            "CANCELLED": PolicyStatus.CANCELLED,
            "EXPIRED": PolicyStatus.EXPIRED,
        }
        status = status_map.get(request.status, PolicyStatus.PENDING)
        tx_hash = gateway.commit_policy(
            policy_id=request.policy_id,
            commitment_hash=request.commitment_hash,
            status=status,
        )
        return {"success": True, "tx_hash": tx_hash, "policy_id": request.policy_id}
    except BlockchainGatewayError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/policies/{policy_id}/status")
async def api_update_policy_status(
    policy_id: str, request: UpdateStatusRequest
) -> dict[str, Any]:
    """Update a policy's status on the blockchain."""
    signer_addr = gateway.signer_address
    if not signer_addr:
        raise HTTPException(status_code=500, detail="Signer not configured")
    try:
        signer_policy.enforce(signer_addr, PolicyAction.UPDATE_STATUS)
    except SignerPolicyError as e:
        raise HTTPException(status_code=403, detail=str(e))

    try:
        status_map = {
            "PENDING": PolicyStatus.PENDING,
            "ACTIVE": PolicyStatus.ACTIVE,
            "ENDORSEMENT": PolicyStatus.ENDORSEMENT,
            "CANCELLED": PolicyStatus.CANCELLED,
            "EXPIRED": PolicyStatus.EXPIRED,
        }
        status = status_map.get(request.status, PolicyStatus.PENDING)
        tx_hash = gateway.update_policy_status(
            policy_id=policy_id,
            new_status=status,
        )
        return {"success": True, "tx_hash": tx_hash, "policy_id": policy_id}
    except BlockchainGatewayError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/events/record")
async def api_record_event(request: RecordEventRequest) -> dict[str, Any]:
    """Record an audit event on the blockchain (via outbox)."""
    signer_addr = gateway.signer_address
    if not signer_addr:
        raise HTTPException(status_code=500, detail="Signer not configured")
    try:
        signer_policy.enforce(signer_addr, PolicyAction.RECORD_EVENT)
    except SignerPolicyError as e:
        raise HTTPException(status_code=403, detail=str(e))

    # Insert into outbox
    entry = OutboxEntry(
        id=str(UUID(int=hash(request.policy_id + request.event_type))),
        event_type=request.event_type,
        payload=json.dumps({
            "policy_id": request.policy_id,
            "commitment_hash": request.commitment_hash,
        }),
        contract="audit_event_registry",
        method="recordEvent",
        status="pending",
        tx_hash=None,
        retry_count=0,
        last_error=None,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    outbox_store.insert(entry)

    return {
        "success": True,
        "outbox_id": entry.id,
        "policy_id": request.policy_id,
        "message": "Event queued for blockchain submission",
    }


@app.get("/policies/{policy_id}")
async def api_get_policy(policy_id: str) -> dict[str, Any]:
    """Get a policy record from the blockchain."""
    try:
        policy = gateway.get_policy(policy_id)
        return policy.to_dict()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/policies/{policy_id}/status")
async def api_get_policy_status(policy_id: str) -> dict[str, Any]:
    """Get a policy's status from the blockchain."""
    try:
        status = gateway.get_policy_status(policy_id)
        return {"policy_id": policy_id, "status": status.name}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/policies/{policy_id}/events")
async def api_get_policy_events(policy_id: str) -> list[dict[str, Any]]:
    """Get on-chain audit events for a policy."""
    try:
        event_indices = gateway.get_policy_events(policy_id)
        events = []
        for idx in event_indices:
            data = gateway.get_event(idx)
            events.append({
                "index": idx,
                "event_type": data[0],
                "policy_id": data[1],
                "commitment_hash": data[2],
                "committed_at": data[3],
                "committed_by": data[4],
            })
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events/by-type/{event_type}")
async def api_get_events_by_type(event_type: str) -> list[dict[str, Any]]:
    """Get on-chain audit events by event type."""
    try:
        event_indices = gateway.get_events_by_type(event_type)
        events = []
        for idx in event_indices:
            data = gateway.get_event(idx)
            events.append({
                "index": idx,
                "event_type": data[0],
                "policy_id": data[1],
                "commitment_hash": data[2],
                "committed_at": data[3],
                "committed_by": data[4],
            })
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/outbox/stats")
async def api_outbox_stats() -> dict[str, Any]:
    """Get outbox statistics."""
    stats = outbox_store.get_stats()
    return OutboxStatsResponse(**stats).model_dump()


@app.post("/reconcile")
async def api_reconcile(window_hours: int = 24) -> dict[str, Any]:
    """Run reconciliation between local state and blockchain."""
    global reconciler
    if reconciler is None:
        raise HTTPException(
            status_code=503,
            detail="Reconciler not initialized. Set local_store in startup.",
        )
    report = reconciler.reconcile(window_hours=window_hours)
    return report.to_dict()


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    connected = gateway.is_connected()
    chain_id = gateway.get_chain_id() if connected else None
    outbox_stats = outbox_store.get_stats()
    return {
        "status": "healthy" if connected else "degraded",
        "service": "blockchain-gateway",
        "connected": connected,
        "chain_id": chain_id,
        "outbox": outbox_stats,
    }
