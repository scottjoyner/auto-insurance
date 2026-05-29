"""Repository adapter for risk appetite persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from risk_appetite_service.domain.models import RiskAssessment, RiskAppetitePolicy
from risk_appetite_service.storage.orm import RiskAssessmentRecord, RiskPolicyApprovalRecord, RiskPolicyVersionRecord


class RiskRepository:
    """SQLAlchemy-backed risk appetite repository."""

    def __init__(self, session: Session):
        self.session = session

    def create_policy_draft(self, policy: RiskAppetitePolicy, actor_id: str) -> RiskPolicyVersionRecord:
        record = RiskPolicyVersionRecord(
            version=policy.version,
            status="draft",
            effective_date=policy.effective_date,
            policy_data=self._policy_to_dict(policy),
            submitted_by_actor_id=actor_id,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def submit_policy(self, policy_id: int, actor_id: str, reason: str = "submitted") -> RiskPolicyVersionRecord | None:
        record = self.session.get(RiskPolicyVersionRecord, policy_id)
        if record is None:
            return None
        record.status = "submitted"
        record.submitted_by_actor_id = actor_id
        record.submitted_at = datetime.utcnow()
        self._append_policy_action(record.id, "submitted", actor_id, reason)
        self.session.commit()
        self.session.refresh(record)
        return record

    def approve_policy(self, policy_id: int, actor_id: str, reason: str = "approved") -> RiskPolicyVersionRecord | None:
        record = self.session.get(RiskPolicyVersionRecord, policy_id)
        if record is None:
            return None
        record.status = "approved"
        record.approved_by_actor_id = actor_id
        record.approved_at = datetime.utcnow()
        self._append_policy_action(record.id, "approved", actor_id, reason)
        self.session.commit()
        self.session.refresh(record)
        return record

    def activate_policy(self, policy_id: int, actor_id: str, reason: str = "activated") -> RiskPolicyVersionRecord | None:
        record = self.session.get(RiskPolicyVersionRecord, policy_id)
        if record is None:
            return None
        self.session.query(RiskPolicyVersionRecord).filter(RiskPolicyVersionRecord.status == "active").update({"status": "deprecated"})
        record.status = "active"
        record.activated_by_actor_id = actor_id
        record.activated_at = datetime.utcnow()
        self._append_policy_action(record.id, "activated", actor_id, reason)
        self.session.commit()
        self.session.refresh(record)
        return record

    def get_active_policy_record(self) -> RiskPolicyVersionRecord | None:
        return (
            self.session.query(RiskPolicyVersionRecord)
            .filter(RiskPolicyVersionRecord.status == "active")
            .order_by(RiskPolicyVersionRecord.activated_at.desc())
            .first()
        )

    def save_assessment(
        self,
        assessment: RiskAssessment,
        policy_version: str,
        quote_data: dict[str, Any],
        portfolio_state: dict[str, Any],
        actor_id: str,
    ) -> RiskAssessmentRecord:
        payload = assessment.to_dict()
        record = RiskAssessmentRecord(
            assessment_id=str(assessment.assessment_id),
            quote_id=str(assessment.quote_id),
            policy_version=policy_version,
            decision=str(assessment.decision),
            risk_score=assessment.risk_score,
            risk_level=payload.get("risk_level", "LOW"),
            quote_data=quote_data,
            portfolio_state=portfolio_state,
            assessment_payload=payload,
            actor_id=actor_id,
            assessed_at=assessment.assessed_at,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def _append_policy_action(self, policy_version_id: int, action: str, actor_id: str, reason: str) -> None:
        self.session.add(
            RiskPolicyApprovalRecord(
                policy_version_id=policy_version_id,
                action=action,
                actor_id=actor_id,
                reason=reason,
            )
        )

    def _policy_to_dict(self, policy: RiskAppetitePolicy) -> dict[str, Any]:
        return {
            "version": policy.version,
            "effective_date": policy.effective_date,
            "categories": {
                key: {
                    "name": value.name,
                    "threshold_pct": value.threshold_pct,
                    "warning_pct": value.warning_pct,
                    "action_on_threshold": str(value.action_on_threshold),
                    "description": value.description,
                    "priority": value.priority,
                }
                for key, value in policy.categories.items()
            },
            "capital_requirements": policy.capital_requirements,
            "reinsurance": policy.reinsurance,
            "decision_matrix": policy.decision_matrix,
        }
