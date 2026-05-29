"""Compliance guards for policy bind decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ComplianceDecision:
    allowed: bool
    reason_codes: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


def evaluate_bind_request(quote_snapshot: dict[str, Any], risk_assessment_snapshot: dict[str, Any]) -> ComplianceDecision:
    """Evaluate whether a bind request may proceed to human approval.

    This is deliberately conservative. It does not replace regulatory review,
    but it prevents obvious invalid handoffs from being bound in Phase 1.
    """
    reason_codes: list[str] = []

    if not quote_snapshot:
        reason_codes.append("missing_quote_snapshot")
    if not risk_assessment_snapshot:
        reason_codes.append("missing_risk_assessment_snapshot")

    quote_status = str(quote_snapshot.get("status", "")).upper()
    if quote_status and quote_status not in {"QUOTED", "CONVERTED"}:
        reason_codes.append("quote_not_acceptable_status")

    if quote_snapshot.get("bind_eligible") is False:
        reason_codes.append("quote_not_bind_eligible")

    risk_decision = str(risk_assessment_snapshot.get("decision", "")).upper()
    if risk_decision in {"DECLINE", "REJECT", "DENY"}:
        reason_codes.append("risk_decision_requires_adverse_action_review")
    elif risk_decision in {"REFER", "ACCEPT_WITH_LIMITS"}:
        reason_codes.append("underwriter_review_required")

    return ComplianceDecision(
        allowed=not any(code in reason_codes for code in {
            "missing_quote_snapshot",
            "missing_risk_assessment_snapshot",
            "quote_not_acceptable_status",
            "quote_not_bind_eligible",
            "risk_decision_requires_adverse_action_review",
        }),
        reason_codes=reason_codes,
        details={"risk_decision": risk_decision, "quote_status": quote_status},
    )
