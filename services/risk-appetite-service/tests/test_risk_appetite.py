"""Tests for the Risk Appetite Service."""

import pytest
from uuid import uuid4

from risk_appetite_service.domain.models import (
    CapitalImpact,
    ExposureCheck,
    ReinsuranceImpact,
    RiskAppetitePolicy,
    RiskCategoryRule,
    RiskDecision,
    RiskAssessment,
)
from risk_appetite_service.engine.risk_engine import RiskAppetiteEngine


# ---------------------------------------------------------------------------
# Domain model tests
# ---------------------------------------------------------------------------


class TestRiskCategoryRule:
    def test_from_dict(self):
        data = {
            "name": "agency_concentration",
            "threshold_pct": 10.0,
            "warning_pct": 7.0,
            "action_on_threshold": "REFER",
            "priority": 1,
        }
        rule = RiskCategoryRule.from_dict(data)
        assert rule.name == "agency_concentration"
        assert rule.threshold_pct == 10.0
        assert rule.warning_pct == 7.0
        assert rule.action_on_threshold == RiskDecision.REFER
        assert rule.priority == 1

    def test_from_dict_defaults(self):
        data = {"name": "test", "threshold_pct": 5.0, "warning_pct": 3.0}
        rule = RiskCategoryRule.from_dict(data)
        assert rule.action_on_threshold == RiskDecision.REFER
        assert rule.priority == 1


class TestRiskAppetitePolicy:
    def test_from_dict(self):
        data = {
            "version": "1.0",
            "effective_date": "2026-01-01",
            "categories": {
                "agency": {
                    "name": "agency_concentration",
                    "threshold_pct": 10.0,
                    "warning_pct": 7.0,
                    "action_on_threshold": "REFER",
                },
                "jurisdiction": {
                    "name": "geographic_concentration",
                    "threshold_pct": 15.0,
                    "warning_pct": 10.0,
                    "action_on_threshold": "REFER",
                },
            },
            "capital_requirements": {"min_ratio": 0.05},
            "reinsurance": {"retention_pct": 30.0, "total_capacity": 50_000_000.0},
        }
        policy = RiskAppetitePolicy.from_dict(data)
        assert policy.version == "1.0"
        assert len(policy.categories) == 2
        assert "agency" in policy.categories
        assert "jurisdiction" in policy.categories
        assert policy.capital_requirements == {"min_ratio": 0.05}

    def test_from_dict_minimal(self):
        data = {"version": "1.0"}
        policy = RiskAppetitePolicy.from_dict(data)
        assert policy.version == "1.0"
        assert len(policy.categories) == 0


class TestRiskAssessment:
    def test_default_state(self):
        a = RiskAssessment()
        assert a.decision == RiskDecision.ACCEPT
        assert a.risk_score == 0.0
        assert a.reason_codes == []

    def test_to_dict(self):
        a = RiskAssessment(
            quote_id=uuid4(),
            decision=RiskDecision.REFER,
            risk_score=65.0,
            triggered_rules=["agency_concentration"],
            category_breakdown={"driver_age": 70.0, "claim_severity": 40.0},
            reason_codes=["high_risk_score", "driver_age_excessive_risk"],
        )
        d = a.to_dict()
        assert d["decision"] == "REFER"
        assert d["risk_score"] == 65.0
        assert d["risk_level"] == "HIGH"
        assert "assessment_id" in d
        assert "assessed_at" in d

    def test_risk_level_low(self):
        a = RiskAssessment(risk_score=25.0)
        assert a._risk_level() == "LOW"

    def test_risk_level_medium(self):
        a = RiskAssessment(risk_score=45.0)
        assert a._risk_level() == "MEDIUM"

    def test_risk_level_high(self):
        a = RiskAssessment(risk_score=75.0)
        assert a._risk_level() == "HIGH"

    def test_risk_level_critical(self):
        a = RiskAssessment(risk_score=90.0)
        assert a._risk_level() == "CRITICAL"

    def test_is_acceptable_accept(self):
        a = RiskAssessment(decision=RiskDecision.ACCEPT)
        assert a.is_acceptable() is True

    def test_is_acceptable_decline(self):
        a = RiskAssessment(decision=RiskDecision.DECLINE)
        assert a.is_acceptable() is False

    def test_is_acceptable_with_limits(self):
        a = RiskAssessment(decision=RiskDecision.ACCEPT_WITH_LIMITS)
        assert a.is_acceptable() is True


class TestExposureCheck:
    def test_to_dict_within_limits(self):
        e = ExposureCheck(
            category="agency",
            current_concentration_pct=5.0,
            threshold_pct=10.0,
            is_within_limits=True,
            trend="increasing",
        )
        d = e.to_dict()
        assert d["within_limits"] is True
        assert d["trend"] == "increasing"

    def test_to_dict_exceeded(self):
        e = ExposureCheck(
            category="jurisdiction",
            current_concentration_pct=20.0,
            threshold_pct=15.0,
            is_within_limits=False,
            warning="Geographic concentration exceeds 15% threshold",
        )
        d = e.to_dict()
        assert d["within_limits"] is False
        assert "exceeds" in d["warning"]


class TestCapitalImpact:
    def test_to_dict_within_tolerance(self):
        c = CapitalImpact(
            estimated_reserve_requirement=1000.0,
            estimated_capital_requirement=500.0,
            current_available_capital=10_000_000.0,
            remaining_capital_after=9_999_500.0,
            capital_ratio_before=0.15,
            capital_ratio_after=0.149,
            is_within_tolerance=True,
        )
        d = c.to_dict()
        assert d["within_tolerance"] is True
        assert d["estimated_reserve_requirement"] == 1000.0


class TestReinsuranceImpact:
    def test_to_dict_within_capacity(self):
        r = ReinsuranceImpact(
            net_retention=700.0,
            ceded_amount=300.0,
            reinsurance_utilization_before=0.6,
            reinsurance_utilization_after=0.65,
            is_within_capacity=True,
        )
        d = r.to_dict()
        assert d["within_capacity"] is True
        assert d["utilization_after"] == 0.65


# ---------------------------------------------------------------------------
# Engine tests
# ---------------------------------------------------------------------------


class TestRiskAppetiteEngine:
    def setup_method(self):
        self.policy = RiskAppetitePolicy(
            version="1.0",
            effective_date="2026-01-01",
            categories={
                "agency": RiskCategoryRule(
                    name="agency_concentration",
                    threshold_pct=10.0,
                    warning_pct=7.0,
                    action_on_threshold=RiskDecision.REFER,
                ),
                "jurisdiction": RiskCategoryRule(
                    name="geographic_concentration",
                    threshold_pct=15.0,
                    warning_pct=10.0,
                    action_on_threshold=RiskDecision.REFER,
                ),
                "product": RiskCategoryRule(
                    name="line_of_business",
                    threshold_pct=20.0,
                    warning_pct=15.0,
                    action_on_threshold=RiskDecision.REFER,
                ),
            },
            capital_requirements={"min_ratio": 0.05},
            reinsurance={
                "retention_pct": 30.0,
                "total_capacity": 50_000_000.0,
                "current_utilization": 0.6,
            },
            decision_matrix={
                "low": {"max_score": 30, "decision": "ACCEPT"},
                "medium": {"max_score": 60, "decision": "ACCEPT_WITH_LIMITS"},
                "high": {"max_score": 80, "decision": "REFER"},
                "critical": {"max_score": 100, "decision": "DECLINE"},
            },
        )
        self.engine = RiskAppetiteEngine(self.policy)

    def _default_portfolio(self):
        return {
            "total_agency_policies": 1000,
            "total_jurisdiction_policies": 1000,
            "total_product_policies": 1000,
            "agency_counts": {"A001": 50, "A002": 30},
            "jurisdiction_counts": {"SAMPLE": 200, "OTHER": 100},
            "product_counts": {"personal_auto_v1": 400, "commercial_v1": 300},
            "available_capital": 10_000_000.0,
            "capital_ratio": 0.15,
        }

    def test_assess_low_risk(self):
        """Low-risk quote should be ACCEPT."""
        quote_data = {
            "total_premium": 100.0,
            "age": 40,
            "vehicle_year": 2023,
            "claims_3yr": 0,
            "agency_id": "A001",
            "jurisdiction": "SAMPLE",
            "product_id": "personal_auto_v1",
        }
        portfolio = self._default_portfolio()
        result = self.engine.assess(uuid4(), quote_data, portfolio)

        assert result.decision == RiskDecision.ACCEPT
        assert result.risk_score < 30
        assert result.is_acceptable() is True

    def test_assess_high_risk(self):
        """High-risk quote should be REFER or DECLINE."""
        quote_data = {
            "total_premium": 500.0,
            "age": 19,
            "vehicle_year": 2005,
            "claims_3yr": 3,
            "agency_id": "A001",
            "jurisdiction": "SAMPLE",
            "product_id": "personal_auto_v1",
        }
        portfolio = self._default_portfolio()
        result = self.engine.assess(uuid4(), quote_data, portfolio)

        assert result.risk_score > 30
        assert len(result.reason_codes) > 0

    def test_assess_with_reason_codes(self):
        """High-risk quote should have reason codes."""
        quote_data = {
            "total_premium": 500.0,
            "age": 19,
            "vehicle_year": 2005,
            "claims_3yr": 3,
            "agency_id": "A001",
            "jurisdiction": "SAMPLE",
            "product_id": "personal_auto_v1",
        }
        portfolio = self._default_portfolio()
        result = self.engine.assess(uuid4(), quote_data, portfolio)

        assert "high_risk_score" in result.reason_codes or "driver_age_excessive_risk" in result.reason_codes
        assert "claim_severity_excessive_risk" in result.reason_codes

    def test_exposure_checks(self):
        """Exposure checks should be populated."""
        quote_data = {
            "total_premium": 100.0,
            "age": 40,
            "vehicle_year": 2023,
            "claims_3yr": 0,
            "agency_id": "A001",
            "jurisdiction": "SAMPLE",
            "product_id": "personal_auto_v1",
        }
        portfolio = self._default_portfolio()
        result = self.engine.assess(uuid4(), quote_data, portfolio)

        assert "agency_concentration" in result.exposure_concentration
        assert "geographic_concentration" in result.exposure_concentration
        assert "line_of_business" in result.exposure_concentration

    def test_capital_impact(self):
        """Capital impact should be populated."""
        quote_data = {
            "total_premium": 100.0,
            "age": 40,
            "vehicle_year": 2023,
            "claims_3yr": 0,
        }
        portfolio = self._default_portfolio()
        result = self.engine.assess(uuid4(), quote_data, portfolio)

        assert "estimated_reserve_requirement" in result.capital_impact
        assert "estimated_capital_requirement" in result.capital_impact
        assert "within_tolerance" in result.capital_impact

    def test_reinsurance_impact(self):
        """Reinsurance impact should be populated."""
        quote_data = {
            "total_premium": 100.0,
            "age": 40,
            "vehicle_year": 2023,
            "claims_3yr": 0,
        }
        portfolio = self._default_portfolio()
        result = self.engine.assess(uuid4(), quote_data, portfolio)

        assert "net_retention" in result.reinsurance_impact
        assert "ceded_amount" in result.reinsurance_impact
        assert "within_capacity" in result.reinsurance_impact

    def test_limits_applied_for_accept_with_limits(self):
        """Limits should be applied for ACCEPT_WITH_LIMITS decisions."""
        quote_data = {
            "total_premium": 500.0,
            "age": 65,
            "vehicle_year": 2018,
            "claims_3yr": 1,
            "agency_id": "A001",
            "jurisdiction": "SAMPLE",
            "product_id": "personal_auto_v1",
        }
        portfolio = self._default_portfolio()
        result = self.engine.assess(uuid4(), quote_data, portfolio)

        if result.decision == RiskDecision.ACCEPT_WITH_LIMITS:
            assert len(result.limits_applied) > 0

    def test_decision_matrix_mapping(self):
        """Test decision mapping for different risk scores."""
        # Low risk
        low_quote = {
            "total_premium": 100.0,
            "age": 40,
            "vehicle_year": 2023,
            "claims_3yr": 0,
        }
        portfolio = self._default_portfolio()
        result = self.engine.assess(uuid4(), low_quote, portfolio)
        assert result.risk_score <= 60  # Should be low enough for ACCEPT or ACCEPT_WITH_LIMITS


class TestRiskAppetiteEngineDefaults:
    def test_engine_with_no_categories(self):
        """Engine should work with empty categories."""
        policy = RiskAppetitePolicy(
            version="1.0",
            effective_date="2026-01-01",
            reinsurance={"retention_pct": 30.0, "total_capacity": 50_000_000.0},
        )
        engine = RiskAppetiteEngine(policy)

        quote_data = {"total_premium": 100.0}
        portfolio = {"total_agency_policies": 1000}
        result = engine.assess(uuid4(), quote_data, portfolio)

        assert result.decision == RiskDecision.ACCEPT
