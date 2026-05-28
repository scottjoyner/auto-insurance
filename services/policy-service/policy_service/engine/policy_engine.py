"""Policy engine - policy lifecycle state machine, bind flow, audit packet generation."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from policy_service.domain.models import (
    AuditEventType,
    AuditPacket,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
    BindMethod,
    BindRequest,
    BindRequestInput,
    Coverage,
    PolicyDocumentType,
    PolicyHolder,
    PolicyLifecycle,
    PolicyState,
    PolicyTransition,
    PolicyTransitionError,
    VehicleInfo,
)

logger = logging.getLogger(__name__)


class PolicyEngine:
    """Policy lifecycle engine with state machine."""

    def __init__(self, lifecycle: PolicyLifecycle | None = None):
        self.lifecycle = lifecycle or self._default_lifecycle()
        self._audit_packets: dict[UUID, list[AuditPacket]] = {}

    def _default_lifecycle(self) -> PolicyLifecycle:
        """Default policy lifecycle state machine."""
        return PolicyLifecycle(
            states=[
                PolicyStateTransition(
                    from_state=PolicyState.DRAFT,
                    to_state=PolicyState.PENDING_BIND,
                    requires_approval=False,
                    description="Submit draft for binding",
                ),
                PolicyStateTransition(
                    from_state=PolicyState.PENDING_BIND,
                    to_state=PolicyState.ACTIVE,
                    requires_approval=True,
                    description="Approve and bind policy",
                ),
                PolicyStateTransition(
                    from_state=PolicyState.ACTIVE,
                    to_state=PolicyState.ENDORSEMENT,
                    requires_approval=True,
                    description="Process endorsement",
                ),
                PolicyStateTransition(
                    from_state=PolicyState.ACTIVE,
                    to_state=PolicyState.CANCELLED,
                    requires_approval=True,
                    description="Cancel policy",
                ),
                PolicyStateTransition(
                    from_state=PolicyState.ACTIVE,
                    to_state=PolicyState.EXPIRED,
                    requires_approval=False,
                    description="Policy expires",
                ),
                PolicyStateTransition(
                    from_state=PolicyState.ENDORSEMENT,
                    to_state=PolicyState.ACTIVE,
                    requires_approval=True,
                    description="Approve endorsement",
                ),
                PolicyStateTransition(
                    from_state=PolicyState.CANCELLED,
                    to_state=PolicyState.DRAFT,
                    requires_approval=False,
                    description="Reactivate cancelled policy",
                ),
            ]
        )

    def _validate_transition(self, current_state: PolicyState, target_state: PolicyState) -> None:
        """Validate a state transition."""
        if not self.lifecycle.is_valid_transition(current_state, target_state):
            valid_targets = self.lifecycle.get_valid_transitions(current_state)
            raise PolicyTransitionError(
                f"Cannot transition from {current_state} to {target_state}. "
                f"Valid transitions: {valid_targets}"
            )

    def generate_audit_packet(
        self,
        event_type: AuditEventType,
        policy_id: UUID,
        metadata: dict[str, Any] | None = None,
    ) -> AuditPacket:
        """Generate an audit packet for blockchain commitment."""
        data = {
            "event_type": event_type,
            "policy_id": str(policy_id),
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {}),
        }
        commitment_hash = hashlib.sha256(
            str(sorted(data.items())).encode()
        ).hexdigest()

        packet = AuditPacket(
            event_type=event_type,
            policy_id=policy_id,
            commitment_hash=commitment_hash,
            metadata=metadata or {},
        )

        if policy_id not in self._audit_packets:
            self._audit_packets[policy_id] = []
        self._audit_packets[policy_id].append(packet)

        logger.info(f"Audit packet generated: {event_type} for policy {policy_id}")
        return packet

    def create_bind_request(
        self,
        input_data: BindRequestInput,
        quote_data: dict[str, Any],
    ) -> BindRequest:
        """Create a bind request from quote data."""
        policy_id = uuid4()

        bind_request = BindRequest(
            quote_id=input_data.quote_id,
            policy_id=policy_id,
            policy_holder=PolicyHolder(
                name=quote_data.get("policy_holder_name", ""),
                address=quote_data.get("policy_holder_address", ""),
                phone=quote_data.get("policy_holder_phone", ""),
                email=quote_data.get("policy_holder_email", ""),
                driver_license=quote_data.get("driver_license", ""),
                date_of_birth=quote_data.get("date_of_birth", ""),
            ),
            vehicle=VehicleInfo(
                make=quote_data.get("vehicle_make", ""),
                model=quote_data.get("vehicle_model", ""),
                year=quote_data.get("vehicle_year", 0),
                vin=quote_data.get("vehicle_vin", ""),
                license_plate=quote_data.get("license_plate", ""),
                state=quote_data.get("vehicle_state", ""),
                mileage=quote_data.get("vehicle_mileage", 0),
                primary_use=quote_data.get("vehicle_primary_use", ""),
                garage_location=quote_data.get("garage_location", ""),
            ),
            coverages=[
                Coverage(
                    type=cv.get("type", ""),
                    limit=cv.get("limit", 0.0),
                    deductible=cv.get("deductible", 0.0),
                    premium=cv.get("premium", 0.0),
                    metadata=cv.get("metadata", {}),
                )
                for cv in quote_data.get("coverages", [])
            ],
            total_premium=quote_data.get("total_premium", 0.0),
            effective_date=input_data.effective_date,
            expiration_date=input_data.expiration_date,
            bind_method=input_data.bind_method,
            ai_confidence=input_data.ai_confidence,
        )

        logger.info(f"Bind request created: {policy_id} from quote {input_data.quote_id}")
        return bind_request

    def create_approval_request(
        self,
        bind_request: BindRequest,
        expires_in_hours: int = 24,
    ) -> ApprovalRequest:
        """Create a human approval request for a bind request."""
        return ApprovalRequest(
            bind_request=bind_request,
            approval_status=ApprovalStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours),
        )

    def process_approval(
        self,
        approval_request: ApprovalRequest,
        decision: ApprovalDecision,
    ) -> dict[str, Any]:
        """Process a human approval decision."""
        # Check expiration
        if approval_request.approval_status == ApprovalStatus.EXPIRED:
            return {"success": False, "message": "Approval request has expired"}

        if decision.approval_status == ApprovalStatus.APPROVED:
            approval_request.approval_status = ApprovalStatus.APPROVED
            approval_request.approver = decision.approver
            approval_request.comments = decision.comments
            approval_request.approved_at = datetime.utcnow()

            logger.info(
                f"Bind request {approval_request.bind_request.policy_id} approved "
                f"by {decision.approver}"
            )
            return {
                "success": True,
                "message": "Bind request approved",
                "approval_request": approval_request,
            }

        elif decision.approval_status == ApprovalStatus.REJECTED:
            approval_request.approval_status = ApprovalStatus.REJECTED
            approval_request.approver = decision.approver
            approval_request.comments = decision.comments
            approval_request.approved_at = datetime.utcnow()

            logger.info(
                f"Bind request {approval_request.bind_request.policy_id} rejected "
                f"by {decision.approver}"
            )
            return {
                "success": False,
                "message": "Bind request rejected",
                "approval_request": approval_request,
            }

        return {"success": False, "message": "Invalid approval status"}

    def transition_state(
        self,
        current_state: PolicyState,
        target_state: PolicyState,
        policy_id: UUID,
    ) -> dict[str, Any]:
        """Transition a policy to a new state."""
        self._validate_transition(current_state, target_state)

        # Generate audit packet for significant transitions
        if target_state == PolicyState.ACTIVE:
            packet = self.generate_audit_packet(
                AuditEventType.BIND,
                policy_id,
                metadata={"from_state": current_state, "to_state": target_state},
            )
            return {
                "success": True,
                "new_state": target_state,
                "audit_packet": packet,
            }

        elif target_state == PolicyState.ENDORSEMENT:
            packet = self.generate_audit_packet(
                AuditEventType.ENDORSEMENT,
                policy_id,
                metadata={"from_state": current_state, "to_state": target_state},
            )
            return {
                "success": True,
                "new_state": target_state,
                "audit_packet": packet,
            }

        elif target_state == PolicyState.CANCELLED:
            packet = self.generate_audit_packet(
                AuditEventType.CANCELLATION,
                policy_id,
                metadata={"from_state": current_state, "to_state": target_state},
            )
            return {
                "success": True,
                "new_state": target_state,
                "audit_packet": packet,
            }

        return {
            "success": True,
            "new_state": target_state,
            "audit_packet": None,
        }

    def get_valid_transitions(self, current_state: PolicyState) -> list[PolicyState]:
        """Get valid transitions from a state."""
        return self.lifecycle.get_valid_transitions(current_state)

    def get_audit_packets(self, policy_id: UUID) -> list[AuditPacket]:
        """Get all audit packets for a policy."""
        return self._audit_packets.get(policy_id, [])

    def generate_policy_document(
        self,
        policy_id: UUID,
        doc_type: PolicyDocumentType,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate a policy document."""
        return {
            "policy_id": str(policy_id),
            "type": doc_type,
            "content": content,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
