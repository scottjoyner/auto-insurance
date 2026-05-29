"""Claims repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from claims_service.models import (
    ClaimEventRecord,
    ClaimEvidenceRecord,
    ClaimRecord,
    ClaimReserveHistoryRecord,
    ClaimStatusHistoryRecord,
)


class ClaimsRepository:
    """SQLAlchemy-backed claims repository."""

    def __init__(self, session: Session):
        self.session = session

    def create_fnol(
        self,
        *,
        policy_id: str,
        tenant_id: str | None,
        customer_id: str | None,
        loss_type: str,
        loss_date: datetime,
        loss_location: str,
        description: str,
        police_report_indicator: bool,
        injuries_indicator: bool,
        preferred_contact_method: str,
        fnol_payload: dict[str, Any],
        actor_id: str,
    ) -> ClaimRecord:
        claim = ClaimRecord(
            claim_id=str(uuid4()),
            tenant_id=tenant_id,
            customer_id=customer_id,
            policy_id=policy_id,
            loss_type=loss_type,
            loss_date=loss_date,
            loss_location=loss_location,
            description=description,
            police_report_indicator=police_report_indicator,
            injuries_indicator=injuries_indicator,
            preferred_contact_method=preferred_contact_method,
            fnol_payload=fnol_payload,
            severity="high" if injuries_indicator else "low",
            queue="New FNOL" if not injuries_indicator else "Manager Approval",
            created_by_actor_id=actor_id,
        )
        self.session.add(claim)
        self.session.flush()
        self.session.add(
            ClaimStatusHistoryRecord(
                claim_id=claim.claim_id,
                from_status=None,
                to_status=claim.status,
                reason="fnol_created",
                actor_id=actor_id,
            )
        )
        self._append_event("ClaimFNOLCreated", claim.claim_id, actor_id, {"policy_id": policy_id, "severity": claim.severity, "queue": claim.queue})
        self.session.commit()
        self.session.refresh(claim)
        return claim

    def get(self, claim_id: str) -> ClaimRecord | None:
        return self.session.get(ClaimRecord, str(claim_id))

    def list(self, *, tenant_id: str | None = None, customer_id: str | None = None, status: str | None = None, limit: int = 100) -> list[ClaimRecord]:
        query = self.session.query(ClaimRecord).order_by(ClaimRecord.created_at.desc())
        if tenant_id is not None:
            query = query.filter(ClaimRecord.tenant_id == tenant_id)
        if customer_id is not None:
            query = query.filter(ClaimRecord.customer_id == customer_id)
        if status is not None:
            query = query.filter(ClaimRecord.status == status)
        return query.limit(limit).all()

    def add_evidence(
        self,
        *,
        claim_id: str,
        evidence_type: str,
        source: str,
        uri: str,
        checksum: str,
        visibility: str,
        actor_id: str,
    ) -> ClaimEvidenceRecord:
        evidence = ClaimEvidenceRecord(
            evidence_id=str(uuid4()),
            claim_id=claim_id,
            evidence_type=evidence_type,
            source=source,
            uri=uri,
            checksum=checksum,
            visibility=visibility,
            uploaded_by_actor_id=actor_id,
        )
        self.session.add(evidence)
        self._append_event("ClaimEvidenceAdded", claim_id, actor_id, {"evidence_id": evidence.evidence_id, "evidence_type": evidence_type})
        self.session.commit()
        self.session.refresh(evidence)
        return evidence

    def recommend_reserve(self, *, claim_id: str, amount: float, reason: str, actor_id: str) -> ClaimReserveHistoryRecord:
        reserve = ClaimReserveHistoryRecord(
            claim_id=claim_id,
            amount=amount,
            reason=reason,
            recommended_by_actor_id=actor_id,
            status="pending_approval",
        )
        self.session.add(reserve)
        self._append_event("ClaimReserveRecommended", claim_id, actor_id, {"amount": amount, "reason": reason})
        self.session.commit()
        self.session.refresh(reserve)
        return reserve

    def approve_reserve(self, *, reserve_id: int, actor_id: str) -> ClaimReserveHistoryRecord | None:
        reserve = self.session.get(ClaimReserveHistoryRecord, reserve_id)
        if reserve is None:
            return None
        reserve.status = "approved"
        reserve.approved_by_actor_id = actor_id
        self._append_event("ClaimReserveApproved", reserve.claim_id, actor_id, {"reserve_id": reserve.id, "amount": reserve.amount})
        self.session.commit()
        self.session.refresh(reserve)
        return reserve

    def mark_denial_review(self, *, claim_id: str, reason: str, actor_id: str) -> ClaimRecord | None:
        claim = self.get(claim_id)
        if claim is None:
            return None
        from_status = claim.status
        claim.status = "denied pending manager review"
        claim.queue = "Denial Review"
        claim.updated_at = datetime.utcnow()
        self.session.add(
            ClaimStatusHistoryRecord(
                claim_id=claim.claim_id,
                from_status=from_status,
                to_status=claim.status,
                reason=reason,
                actor_id=actor_id,
            )
        )
        self._append_event("ClaimDenialReviewRequested", claim_id, actor_id, {"reason": reason})
        self.session.commit()
        self.session.refresh(claim)
        return claim

    def _append_event(self, event_type: str, aggregate_id: str, actor_id: str, payload: dict[str, Any]) -> None:
        self.session.add(
            ClaimEventRecord(
                event_id=str(uuid4()),
                event_type=event_type,
                aggregate_id=aggregate_id,
                actor_id=actor_id,
                payload=payload,
            )
        )
