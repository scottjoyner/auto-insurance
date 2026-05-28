"""Risk appetite domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class RiskDecision(StrEnum):
    ACCEPT = "ACCEPT"
    ACCEPT_WITH_LIMITS = "ACCEPT_WITH_LIMITS"
    REFER = "REFER"
    DECLINE = "DECLINE"
    REQUEST_MORE_INFO = "REQUEST_MORE_INFO"


class RiskCategory(StrEnum):
    AGENCY_CONCENTRATION = "agency_concentration"
    GEOGRAPHIC_CONCENTRATION = "geographic_concentration"
    LINE_OF_BUSINESS = "line_of_business"
    VEHICLE_TYPE = "vehicle_type"
    DRIVER_AGE = "driver_age"
    CLAIM_SEVERITY = "claim_severity"
    CAPITAL_ADEQUACY = "capital_adequacy"
    REINSURANCE_CAPACITY = "reinsurance_capacity"


@dataclass(frozen=True)
class RiskAppetitePolicy:
    """Configuration for risk appetite rules."""
    version: str
    effective_date: str
    categories: dict[str, "RiskCategoryRule"] = field(default_factory=dict)
    capital_requirements: dict[str, Any] = field(default_factory=dict)
    reinsurance: dict[str, Any] = field(default_factory=dict)
    decision_matrix: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RiskAppetitePolicy":
        categories = {}
        for key, rule_data in data.get("categories", {}).items():
            categories[key] = RiskCategoryRule.from_dict(rule_data)
        return cls(
            version=data.get("version", "1.0"),
            effective_date=data.get("effective_date", "2026-01-01"),
            categories=categories,
            capital_requirements=data.get("capital_requirements", {}),
            reinsurance=data.get("reinsurance", {}),
            decision_matrix=data.get("decision_matrix", {}),
        )


@dataclass(frozen=True)
class RiskCategoryRule:
    """A single risk category rule."""
    name: str
    threshold_pct: float
    warning_pct: float
    action_on_threshold: RiskDecision
    description: str = ""
    priority: int = 1

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RiskCategoryRule":
        return cls(
            name=data.get("name", "unknown"),
            threshold_pct=float(data.get("threshold_pct", 0.0)),
            warning_pct=float(data.get("warning_pct", 0.0)),
            action_on_threshold=RiskDecision(data.get("action_on_threshold", "REFER")),
            description=data.get("description", ""),
            priority=int(data.get("priority", 1)),
        )


@dataclass
class RiskAssessment:
    """Result of a risk appetite assessment."""
    assessment_id: UUID = field(default_factory=uuid4)
    quote_id: UUID | None = None
    decision: RiskDecision = RiskDecision.ACCEPT
    risk_score: float = 0.0
    max_risk_score: float = 100.0
    triggered_rules: list[str] = field(default_factory=list)
    category_breakdown: dict[str, float] = field(default_factory=dict)
    exposure_concentration: dict[str, Any] = field(default_factory=dict)
    capital_impact: dict[str, Any] = field(default_factory=dict)
    reinsurance_impact: dict[str, Any] = field(default_factory=dict)
    limits_applied: dict[str, Any] = field(default_factory=dict)
    reason_codes: list[str] = field(default_factory=list)
    audit_metadata: dict[str, Any] = field(default_factory=dict)
    assessed_at: datetime = field(default_factory=lambda: datetime.utcnow())

    def to_dict(self) -> dict[str, Any]:
        return {
            "assessment_id": str(self.assessment_id),
            "quote_id": str(self.quote_id) if self.quote_id else None,
            "decision": self.decision,
            "risk_score": self.risk_score,
            "max_risk_score": self.max_risk_score,
            "risk_level": self._risk_level(),
            "triggered_rules": self.triggered_rules,
            "category_breakdown": self.category_breakdown,
            "exposure_concentration": self.exposure_concentration,
            "capital_impact": self.capital_impact,
            "reinsurance_impact": self.reinsurance_impact,
            "limits_applied": self.limits_applied,
            "reason_codes": self.reason_codes,
            "assessed_at": self.assessed_at.isoformat(),
        }

    def _risk_level(self) -> str:
        if self.risk_score <= 30:
            return "LOW"
        elif self.risk_score <= 60:
            return "MEDIUM"
        elif self.risk_score <= 80:
            return "HIGH"
        else:
            return "CRITICAL"

    def is_acceptable(self) -> bool:
        return self.decision in (RiskDecision.ACCEPT, RiskDecision.ACCEPT_WITH_LIMITS)


@dataclass
class ExposureCheck:
    """Result of an exposure concentration check."""
    category: str
    current_concentration_pct: float
    threshold_pct: float
    is_within_limits: bool
    trend: str = "stable"  # increasing, decreasing, stable
    warning: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "current_concentration_pct": self.current_concentration_pct,
            "threshold_pct": self.threshold_pct,
            "within_limits": self.is_within_limits,
            "trend": self.trend,
            "warning": self.warning,
        }


@dataclass
class CapitalImpact:
    """Estimated capital/reserve impact of a quote."""
    estimated_reserve_requirement: float
    estimated_capital_requirement: float
    current_available_capital: float
    remaining_capital_after: float
    capital_ratio_before: float
    capital_ratio_after: float
    is_within_tolerance: bool
    warning: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "estimated_reserve_requirement": self.estimated_reserve_requirement,
            "estimated_capital_requirement": self.estimated_capital_requirement,
            "current_available_capital": self.current_available_capital,
            "remaining_capital_after": self.remaining_capital_after,
            "capital_ratio_before": self.capital_ratio_before,
            "capital_ratio_after": self.capital_ratio_after,
            "within_tolerance": self.is_within_tolerance,
            "warning": self.warning,
        }


@dataclass
class ReinsuranceImpact:
    """Estimated reinsurance impact of a quote."""
    net_retention: float
    ceded_amount: float
    reinsurance_utilization_before: float
    reinsurance_utilization_after: float
    is_within_capacity: bool
    warning: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "net_retention": self.net_retention,
            "ceded_amount": self.ceded_amount,
            "utilization_before": self.reinsurance_utilization_before,
            "utilization_after": self.reinsurance_utilization_after,
            "within_capacity": self.is_within_capacity,
            "warning": self.warning,
        }
