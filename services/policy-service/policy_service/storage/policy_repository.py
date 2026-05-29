"""Repository adapter for policy bind workflow persistence."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from policy_service.storage.orm import ApprovalRecord, BindRequestRecord, PolicyEventRecord, PolicyRecord


class PolicyRepository:
    """SQLAlchemy-backed repository for bind requests and policies."""

    def __init__(self, session: Session):
        self.session = session

    def create_bind_request(
        self,
        quote_id: UUID | str,
        effective_date: datetime,
        expiration_date: datetime,
        quote_snapshot: dict,
        risk_assessment_snapshot: dict,
        actor_id: str,
        bind_method: str = "human_approval",
    ) -> BindRequestRecord:
        policy_id = str(uuid4())
        record = BindRequestRecord(
            bind_request_id=str(uuid4()),
            quote_id=str(quote_id),
            policy_id=policy_id,
            status="pending_approval",
            bind_method=bind_method,
            total_premium=float(quote_snapshot.get("total_premium", 0.0)),
            effective_date=effective_date,
            expiration_date=expiration_date,
            quote_snapshot=quote_snapshot,
            risk_assessment_snapshot=risk_assessment_snapshot,
            created_by_actor_id=actor_id,
        )
        approval = ApprovalRecord(
            approval_id=str(uuid4()),
            bind_request_id=record.bind_request_id,
            status="pending",
        )
        self.session.add(record)
        self.session.add(approval)
        self._append_event("BindRequestCreated", record.bind_request_id, actor_id, {"quote_id": str(quote_id), "policy_id": policy_id})
        self.session.commit()
        self.session.refresh(record)
        return record

    def get_bind_request(self, bind_request_id: UUID | str) -> BindRequestRecord | None:
        return self.session.get(BindRequestRecord, str(bind_request_id))

    def get_policy(self, policy_id: UUID | str) -> PolicyRecord | None:
        return self.session.get(PolicyRecord, str(policy_id))

    def approve_bind_request(self, bind_request_id: UUID | str, actor_id: str, comments: str = "") -> PolicyRecord | None:
        bind_request = self.get_bind_request(bind_request_id)
        if bind_request is None:
            return None
        if bind_request.status not in {"pending_approval", "approved"}:
            return None

        approval = (
            self.session.query(ApprovalRecord)
            .filter(ApprovalRecord.bind_request_id == str(bind_request_id))
            .order_by(ApprovalRecord.created_at.desc())
            .first()
        )
        if approval:
            approval.status = "approved"
            approval.approver_actor_id = actor_id
            approval.comments = comments
            approval.decided_at = datetime.utcnow()

        bind_request.status = "approved"
        bind_request.updated_at = datetime.utcnow()
        policy = PolicyRecord(
            policy_id=bind_request.policy_id,
            quote_id=bind_request.quote_id,
            bind_request_id=bind_request.bind_request_id,
            state="active",
            total_premium=bind_request.total_premium,
            effective_date=bind_request.effective_date,
            expiration_date=bind_request.expiration_date,
            bind_packet={
                "quote_snapshot": bind_request.quote_snapshot,
                "risk_assessment_snapshot": bind_request.risk_assessment_snapshot,
                "approval_id": approval.approval_id if approval else None,
            },
            bound_by_actor_id=actor_id,
        )
        self.session.add(policy)
        self._append_event("BindRequestApproved", bind_request.bind_request_id, actor_id, {"policy_id": policy.policy_id})
        self._append_event("PolicyBound", policy.policy_id, actor_id, {"quote_id": policy.quote_id, "bind_request_id": bind_request.bind_request_id})
        self.session.commit()
        self.session.refresh(policy)
        return policy

    def reject_bind_request(self, bind_request_id: UUID | str, actor_id: str, comments: str = "") -> BindRequestRecord | None:
        bind_request = self.get_bind_request(bind_request_id)
        if bind_request is None:
            return None
        approval = (
            self.session.query(ApprovalRecord)
            .filter(ApprovalRecord.bind_request_id == str(bind_request_id))
            .order_by(ApprovalRecord.created_at.desc())
            .first()
        )
        if approval:
            approval.status = "rejected"
            approval.approver_actor_id = actor_id
            approval.comments = comments
            approval.decided_at = datetime.utcnow()
        bind_request.status = "rejected"
        bind_request.updated_at = datetime.utcnow()
        self._append_event("BindRequestRejected", bind_request.bind_request_id, actor_id, {"comments": comments})
        self.session.commit()
        self.session.refresh(bind_request)
        return bind_request

    def list_policies(self, state: str | None = None, limit: int = 100) -> list[PolicyRecord]:
        query = self.session.query(PolicyRecord).order_by(PolicyRecord.bound_at.desc())
        if state:
            query = query.filter(PolicyRecord.state == state)
        return query.limit(limit).all()

    def _append_event(self, event_type: str, aggregate_id: str, actor_id: str, payload: dict) -> None:
        self.session.add(
            PolicyEventRecord(
                event_id=str(uuid4()),
                event_type=event_type,
                aggregate_id=aggregate_id,
                actor_id=actor_id,
                payload=payload,
            )
        )
