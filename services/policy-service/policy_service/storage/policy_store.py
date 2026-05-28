"""Policy storage layer - SQLite persistence for policies."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from policy_service.domain.models import (
    AuditPacket,
    Coverage,
    PolicyDocumentType,
    PolicyHolder,
    PolicyState,
    VehicleInfo,
)

logger = logging.getLogger(__name__)


class PolicyStore:
    """In-memory policy store for MVP. Replace with SQLite for production."""

    def __init__(self):
        self._policies: dict[UUID, dict[str, Any]] = {}
        self._audit_packets: dict[UUID, list[AuditPacket]] = {}
        self._documents: dict[UUID, list[dict[str, Any]]] = {}

    def create_policy(
        self,
        policy_id: UUID,
        state: PolicyState,
        policy_holder: PolicyHolder,
        vehicle: VehicleInfo,
        coverages: list[Coverage],
        total_premium: float,
        effective_date: datetime,
        expiration_date: datetime,
    ) -> dict[str, Any]:
        """Create a new policy."""
        policy = {
            "policy_id": str(policy_id),
            "state": state,
            "policy_holder": policy_holder.to_dict(),
            "vehicle": vehicle.to_dict(),
            "coverages": [c.to_dict() for c in coverages],
            "total_premium": total_premium,
            "effective_date": effective_date.isoformat(),
            "expiration_date": expiration_date.isoformat(),
            "bind_date": None,
            "cancellation_date": None,
            "bind_method": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        self._policies[policy_id] = policy
        self._audit_packets[policy_id] = []
        self._documents[policy_id] = []
        logger.info(f"Policy created: {policy_id}")
        return policy

    def get_policy(self, policy_id: UUID) -> dict[str, Any] | None:
        """Get a policy by ID."""
        return self._policies.get(policy_id)

    def update_policy_state(self, policy_id: UUID, new_state: PolicyState) -> dict[str, Any] | None:
        """Update a policy's state."""
        policy = self._policies.get(policy_id)
        if not policy:
            return None

        policy["state"] = new_state
        policy["updated_at"] = datetime.utcnow().isoformat()

        if new_state == PolicyState.ACTIVE:
            policy["bind_date"] = datetime.utcnow().isoformat()
        elif new_state == PolicyState.CANCELLED:
            policy["cancellation_date"] = datetime.utcnow().isoformat()

        logger.info(f"Policy {policy_id} state updated to {new_state}")
        return policy

    def add_audit_packet(self, policy_id: UUID, packet: AuditPacket) -> None:
        """Add an audit packet for a policy."""
        if policy_id not in self._audit_packets:
            self._audit_packets[policy_id] = []
        self._audit_packets[policy_id].append(packet)

    def get_audit_packets(self, policy_id: UUID) -> list[AuditPacket]:
        """Get all audit packets for a policy."""
        return self._audit_packets.get(policy_id, [])

    def add_document(
        self,
        policy_id: UUID,
        doc_type: PolicyDocumentType,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add a policy document."""
        doc = {
            "type": doc_type,
            "content": content,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        if policy_id not in self._documents:
            self._documents[policy_id] = []
        self._documents[policy_id].append(doc)
        return doc

    def get_documents(self, policy_id: UUID) -> list[dict[str, Any]]:
        """Get all documents for a policy."""
        return self._documents.get(policy_id, [])

    def list_policies(self, state: PolicyState | None = None) -> list[dict[str, Any]]:
        """List policies, optionally filtered by state."""
        policies = list(self._policies.values())
        if state:
            policies = [p for p in policies if p["state"] == state]
        return policies


store = PolicyStore()
