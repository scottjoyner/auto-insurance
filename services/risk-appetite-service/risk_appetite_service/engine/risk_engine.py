"""Risk appetite engine - evaluates quotes against risk appetite policy."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from risk_appetite_service.domain.models import (
    CapitalImpact,
    ExposureCheck,
    ReinsuranceImpact,
    RiskAssessment,
    RiskAppetitePolicy,
    RiskDecision,
    RiskCategory,
)

logger = logging.getLogger(__name__)


class RiskAppetiteEngine:
    """Evaluates quotes against a risk appetite policy."""

    def __init__(self, policy: RiskAppetitePolicy):
        self.policy = policy

    def assess(
        self,
        quote_id: UUID,
        quote_data: dict[str, Any],
        portfolio_state: dict[str, Any],
    ) -> RiskAssessment:
        """Run the full risk appetite assessment."""
        assessment = RiskAssessment(quote_id=quote_id)

        # 1. Exposure concentration checks
        assessment.exposure_concentration = self._check_exposures(quote_data, portfolio_state)

        # 2. Capital/reserve impact
        assessment.capital_impact = self._estimate_capital_impact(quote_data, portfolio_state)

        # 3. Reinsurance impact
        assessment.reinsurance_impact = self._estimate_reinsurance_impact(quote_data, portfolio_state)

        # 4. Category-specific checks
        assessment.category_breakdown = self._check_categories(quote_data, portfolio_state)

        # 5. Compute overall risk score
        assessment.risk_score = self._compute_risk_score(assessment)

        # 6. Determine decision based on decision matrix
        assessment.decision = self._determine_decision(assessment)

        # 7. Apply limits if needed
        assessment.limits_applied = self._apply_limits(assessment)

        # 8. Collect reason codes
        assessment.reason_codes = self._collect_reason_codes(assessment)

        logger.info(
            "Risk assessment %s: %s (score: %.1f)",
            assessment.assessment_id,
            assessment.decision,
            assessment.risk_score,
        )
        return assessment

    def _check_exposures(
        self,
        quote_data: dict[str, Any],
        portfolio_state: dict[str, Any],
    ) -> dict[str, Any]:
        """Check exposure concentration limits."""
        results = {}
        thresholds = self.policy.categories

        # Agency concentration
        agency_pct = self._get_concentration(
            portfolio_state, "agency", quote_data.get("agency_id", "")
        )
        agency_rule = self.policy.categories.get("agency")
        agency_threshold = agency_rule.threshold_pct if agency_rule else 10.0
        results["agency_concentration"] = ExposureCheck(
            category="agency",
            current_concentration_pct=agency_pct,
            threshold_pct=agency_threshold,
            is_within_limits=agency_pct < agency_threshold,
        ).to_dict()

        # Geographic concentration
        geo_pct = self._get_concentration(
            portfolio_state, "jurisdiction", quote_data.get("jurisdiction", "")
        )
        geo_rule = self.policy.categories.get("jurisdiction")
        geo_threshold = geo_rule.threshold_pct if geo_rule else 15.0
        results["geographic_concentration"] = ExposureCheck(
            category="jurisdiction",
            current_concentration_pct=geo_pct,
            threshold_pct=geo_threshold,
            is_within_limits=geo_pct < geo_threshold,
        ).to_dict()

        # Line of business concentration
        lob_pct = self._get_concentration(
            portfolio_state, "product", quote_data.get("product_id", "")
        )
        lob_rule = self.policy.categories.get("product")
        lob_threshold = lob_rule.threshold_pct if lob_rule else 20.0
        results["line_of_business"] = ExposureCheck(
            category="product",
            current_concentration_pct=lob_pct,
            threshold_pct=lob_threshold,
            is_within_limits=lob_pct < lob_threshold,
        ).to_dict()

        return results

    def _get_concentration(
        self,
        portfolio_state: dict[str, Any],
        category: str,
        value: str,
    ) -> float:
        """Calculate concentration percentage for a category."""
        total = portfolio_state.get(f"total_{category}_policies", 1000)
        count = portfolio_state.get(f"{category}_counts", {}).get(value, 0)
        if total == 0:
            return 0.0
        return (count / total) * 100

    def _estimate_capital_impact(
        self,
        quote_data: dict[str, Any],
        portfolio_state: dict[str, Any],
    ) -> dict[str, Any]:
        """Estimate capital/reserve impact of a quote."""
        premium = quote_data.get("total_premium", 0.0)
        available_capital = portfolio_state.get("available_capital", 10_000_000.0)
        current_ratio = portfolio_state.get("capital_ratio", 0.15)

        # Rough estimate: reserve = 20% of premium (stub)
        reserve_requirement = premium * 0.2
        capital_requirement = premium * 0.05

        remaining = available_capital - capital_requirement
        new_ratio = remaining / max(available_capital, 1) if available_capital > 0 else 0

        return CapitalImpact(
            estimated_reserve_requirement=reserve_requirement,
            estimated_capital_requirement=capital_requirement,
            current_available_capital=available_capital,
            remaining_capital_after=remaining,
            capital_ratio_before=current_ratio,
            capital_ratio_after=new_ratio,
            is_within_tolerance=new_ratio > 0.05,
        ).to_dict()

    def _estimate_reinsurance_impact(
        self,
        quote_data: dict[str, Any],
        portfolio_state: dict[str, Any],
    ) -> dict[str, Any]:
        """Estimate reinsurance impact of a quote."""
        premium = quote_data.get("total_premium", 0.0)
        retention_pct = self.policy.reinsurance.get("retention_pct", 30.0)
        total_capacity = self.policy.reinsurance.get("total_capacity", 50_000_000.0)
        current_utilization = self.policy.reinsurance.get("current_utilization", 0.6)

        ceded = premium * (1 - retention_pct / 100)
        net_retention = premium - ceded
        new_utilization = current_utilization + (ceded / total_capacity)

        return ReinsuranceImpact(
            net_retention=net_retention,
            ceded_amount=ceded,
            reinsurance_utilization_before=current_utilization,
            reinsurance_utilization_after=new_utilization,
            is_within_capacity=new_utilization < 0.95,
        ).to_dict()

    def _check_categories(
        self,
        quote_data: dict[str, Any],
        portfolio_state: dict[str, Any],
    ) -> dict[str, float]:
        """Check risk categories against thresholds."""
        breakdown = {}
        for cat_name, rule in self.policy.categories.items():
            # Calculate category risk score (0-100)
            score = self._calculate_category_score(cat_name, quote_data, portfolio_state)
            breakdown[cat_name] = score
        return breakdown

    def _calculate_category_score(
        self,
        cat_name: str,
        quote_data: dict[str, Any],
        portfolio_state: dict[str, Any],
    ) -> float:
        """Calculate a risk score for a specific category."""
        # Stub implementation - would use actual risk factors
        score = 0.0

        if cat_name == "driver_age":
            age = quote_data.get("age", 35)
            if age < 25:
                score = 70.0  # young driver = high risk
            elif age > 70:
                score = 40.0  # older driver = moderate risk
        elif cat_name == "claim_severity":
            claims = quote_data.get("claims_3yr", 0)
            score = min(100.0, claims * 25.0)
        elif cat_name == "vehicle_type":
            vehicle_year = quote_data.get("vehicle_year", 2023)
            if vehicle_year < 2015:
                score = 30.0
            else:
                score = 10.0
        else:
            score = 20.0  # default moderate risk

        return score

    def _compute_risk_score(self, assessment: RiskAssessment) -> float:
        """Compute overall risk score from category breakdown."""
        if not assessment.category_breakdown:
            return 0.0

        weights = {
            "driver_age": 0.25,
            "claim_severity": 0.25,
            "vehicle_type": 0.15,
            "agency_concentration": 0.10,
            "geographic_concentration": 0.10,
            "line_of_business": 0.15,
        }

        total = 0.0
        for cat, score in assessment.category_breakdown.items():
            weight = weights.get(cat, 0.10)
            total += score * weight

        return min(100.0, total)

    def _determine_decision(self, assessment: RiskAssessment) -> RiskDecision:
        """Determine risk decision based on risk score and decision matrix."""
        decision_matrix = self.policy.decision_matrix

        # Default decision logic
        if assessment.risk_score <= 30:
            return RiskDecision.ACCEPT
        elif assessment.risk_score <= 60:
            return RiskDecision.ACCEPT_WITH_LIMITS
        elif assessment.risk_score <= 80:
            return RiskDecision.REFER
        else:
            return RiskDecision.DECLINE

    def _apply_limits(self, assessment: RiskAssessment) -> dict[str, Any]:
        """Apply limits if decision is ACCEPT_WITH_LIMITS."""
        if assessment.decision != RiskDecision.ACCEPT_WITH_LIMITS:
            return {}

        return {
            "max_premium": 5000.0,
            "max_coverage_amount": 100000.0,
            "required_additional_info": ["proof_of_ownership", "driving_record"],
        }

    def _collect_reason_codes(self, assessment: RiskAssessment) -> list[str]:
        """Collect reason codes for the decision."""
        codes = []

        if assessment.risk_score > 60:
            codes.append("high_risk_score")

        for cat, score in assessment.category_breakdown.items():
            if score > 70:
                codes.append(f"{cat}_excessive_risk")

        # Check exposure limits
        for key, exposure in assessment.exposure_concentration.items():
            if isinstance(exposure, dict) and not exposure.get("within_limits", True):
                codes.append(f"exposure_{key}_exceeded")

        # Check capital
        capital = assessment.capital_impact
        if isinstance(capital, dict) and not capital.get("within_tolerance", True):
            codes.append("capital_adequacy_concern")

        return codes
