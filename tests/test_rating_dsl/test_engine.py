"""
Tests for the Rating DSL engine (full rating pipeline).

Tests the end-to-end rating flow: eligibility checks, base calculation,
surcharges, discounts, coverages, and totals.
"""

import pytest
from decimal import Decimal
from pathlib import Path

from rating_dsl.parser import load_product
from rating_dsl.engine import (
    evaluate,
    RatingResult,
    EligibilityError,
    CoverageResult,
)


@pytest.fixture
def sample_product():
    """Load the sample personal auto product."""
    # Resolve relative to this file's location
    base = Path(__file__).resolve().parent.parent.parent
    sample_path = base / "data" / "sample-products" / "sample_personal_auto_v1.yml"
    if not sample_path.exists():
        pytest.skip("Sample product YAML not found")
    return load_product(sample_path)


# ---------------------------------------------------------------------------
# Happy path tests
# ---------------------------------------------------------------------------

class TestHappyPath:
    """Test successful rating scenarios."""

    def test_eligible_quote(self, sample_product):
        """A fully eligible quote should rate successfully."""
        result = evaluate(sample_product, {
            "age": 35,
            "vehicle_year": 2023,
            "coverage_type": "standard",
            "vehicle_value": 25000,
            "driving_years": 15,
            "claims_3yr": 0,
            "credit_tier": "a",
        })
        assert result.eligibility_passed is True
        assert result.is_valid is True
        assert result.total_premium > 0
        assert len(result.coverages) > 0
        assert result.surcharges_applied == []
        assert "good_driver" in result.discounts_applied
        assert "new_vehicle" in result.discounts_applied

    def test_young_driver_quote(self, sample_product):
        """A young driver should get a surcharge."""
        result = evaluate(sample_product, {
            "age": 20,
            "vehicle_year": 2020,
            "coverage_type": "standard",
            "vehicle_value": 15000,
            "driving_years": 2,
            "claims_3yr": 0,
            "credit_tier": "b",
        })
        assert result.eligibility_passed is True
        assert "young_driver" in result.surcharges_applied
        assert result.total_premium > 0

    def test_high_claims_quote(self, sample_product):
        """A high-claims driver should get a surcharge."""
        result = evaluate(sample_product, {
            "age": 40,
            "vehicle_year": 2018,
            "coverage_type": "basic",
            "vehicle_value": 20000,
            "driving_years": 15,
            "claims_3yr": 3,
            "credit_tier": "c",
        })
        assert result.eligibility_passed is True
        assert "claims_surge" in result.surcharges_applied
        assert result.total_premium > 0

    def test_poor_credit_quote(self, sample_product):
        """A poor credit tier should get a surcharge."""
        result = evaluate(sample_product, {
            "age": 45,
            "vehicle_year": 2022,
            "coverage_type": "premium",
            "vehicle_value": 35000,
            "driving_years": 20,
            "claims_3yr": 0,
            "credit_tier": "e",
        })
        assert result.eligibility_passed is True
        assert "poor_credit" in result.surcharges_applied
        assert result.total_premium > 0


# ---------------------------------------------------------------------------
# Eligibility failure tests
# ---------------------------------------------------------------------------

class TestEligibilityFailure:
    """Test eligibility gate failures."""

    def test_underage(self, sample_product):
        """Quote from an underage applicant should fail."""
        result = evaluate(sample_product, {
            "age": 15,
            "vehicle_year": 2020,
            "coverage_type": "standard",
            "vehicle_value": 10000,
            "driving_years": 0,
            "claims_3yr": 0,
            "credit_tier": "a",
        })
        assert result.eligibility_passed is False
        assert result.is_valid is False
        assert len(result.failed_rules) > 0

    def test_no_driving_experience(self, sample_product):
        """Quote with no driving experience should fail."""
        result = evaluate(sample_product, {
            "age": 25,
            "vehicle_year": 2020,
            "coverage_type": "standard",
            "vehicle_value": 10000,
            "driving_years": 0,
            "claims_3yr": 0,
            "credit_tier": "a",
        })
        assert result.eligibility_passed is False
        assert "driving_experience" in result.failed_rules

    def test_too_many_claims(self, sample_product):
        """Quote with too many claims should fail."""
        result = evaluate(sample_product, {
            "age": 35,
            "vehicle_year": 2020,
            "coverage_type": "standard",
            "vehicle_value": 10000,
            "driving_years": 10,
            "claims_3yr": 4,
            "credit_tier": "a",
        })
        assert result.eligibility_passed is False
        assert "claims_limit" in result.failed_rules

    def test_old_vehicle(self, sample_product):
        """Quote for an old vehicle should fail."""
        result = evaluate(sample_product, {
            "age": 35,
            "vehicle_year": 1985,
            "coverage_type": "standard",
            "vehicle_value": 2000,
            "driving_years": 10,
            "claims_3yr": 0,
            "credit_tier": "a",
        })
        assert result.eligibility_passed is False
        assert "vehicle_age" in result.failed_rules


# ---------------------------------------------------------------------------
# Coverage result tests
# ---------------------------------------------------------------------------

class TestCoverageResults:
    """Test individual coverage results."""

    def test_coverage_names_present(self, sample_product):
        """All defined coverages should appear in results."""
        result = evaluate(sample_product, {
            "age": 35,
            "vehicle_year": 2023,
            "coverage_type": "standard",
            "vehicle_value": 25000,
            "driving_years": 15,
            "claims_3yr": 0,
            "credit_tier": "a",
        })
        coverage_names = {c.name for c in result.coverages}
        assert "liability" in coverage_names
        assert "collision" in coverage_names
        assert "comprehensive" in coverage_names
        assert "uninsured_motorist" in coverage_names
        assert "medical_payments" in coverage_names

    def test_coverage_dict(self, sample_product):
        """coverage_dict should return {name: premium} mapping."""
        result = evaluate(sample_product, {
            "age": 35,
            "vehicle_year": 2023,
            "coverage_type": "standard",
            "vehicle_value": 25000,
            "driving_years": 15,
            "claims_3yr": 0,
            "credit_tier": "a",
        })
        d = result.coverage_dict
        assert isinstance(d, dict)
        assert len(d) == len(result.coverages)
        assert all(isinstance(v, Decimal) for v in d.values())

    def test_total_equals_sum_of_coverages(self, sample_product):
        """Total premium should equal the sum of all coverages."""
        result = evaluate(sample_product, {
            "age": 35,
            "vehicle_year": 2023,
            "coverage_type": "standard",
            "vehicle_value": 25000,
            "driving_years": 15,
            "claims_3yr": 0,
            "credit_tier": "a",
        })
        total_from_coverages = sum(c.final_premium for c in result.coverages)
        assert result.total_premium == total_from_coverages

    def test_to_dict_serialization(self, sample_product):
        """to_dict should return a JSON-serializable dict."""
        result = evaluate(sample_product, {
            "age": 35,
            "vehicle_year": 2023,
            "coverage_type": "standard",
            "vehicle_value": 25000,
            "driving_years": 15,
            "claims_3yr": 0,
            "credit_tier": "a",
        })
        d = result.to_dict()
        assert d["product"] == "sample_personal_auto_v1"
        assert d["jurisdiction"] == "SAMPLE"
        assert d["eligible"] is True
        assert isinstance(d["total_premium"], str)
        assert isinstance(d["coverages"], dict)


# ---------------------------------------------------------------------------
# Min/max premium enforcement tests
# ---------------------------------------------------------------------------

class TestMinMaxEnforcement:
    """Test per-coverage minimum and maximum premium enforcement."""

    def test_min_premium_enforced(self, sample_product):
        """Coverage with calculated premium below minimum should be raised."""
        # Use a very low vehicle value to trigger min_premium on liability
        result = evaluate(sample_product, {
            "age": 35,
            "vehicle_year": 2023,
            "coverage_type": "basic",
            "vehicle_value": 1000,  # Very low
            "driving_years": 15,
            "claims_3yr": 0,
            "credit_tier": "a",
        })
        liability = next(c for c in result.coverages if c.name == "liability")
        assert liability.final_premium >= 50.00  # min_premium


# ---------------------------------------------------------------------------
# RatingResult dataclass tests
# ---------------------------------------------------------------------------

class TestRatingResult:
    """Test RatingResult properties and methods."""

    def test_is_valid_false_on_eligibility_failure(self, sample_product):
        result = evaluate(sample_product, {
            "age": 15,
            "vehicle_year": 2020,
            "coverage_type": "standard",
            "vehicle_value": 10000,
            "driving_years": 0,
            "claims_3yr": 0,
            "credit_tier": "a",
        })
        assert result.is_valid is False

    def test_is_valid_true_on_success(self, sample_product):
        result = evaluate(sample_product, {
            "age": 35,
            "vehicle_year": 2023,
            "coverage_type": "standard",
            "vehicle_value": 25000,
            "driving_years": 15,
            "claims_3yr": 0,
            "credit_tier": "a",
        })
        assert result.is_valid is True

    def test_failed_rules_list(self, sample_product):
        result = evaluate(sample_product, {
            "age": 15,
            "vehicle_year": 1980,
            "coverage_type": "standard",
            "vehicle_value": 1000,
            "driving_years": 0,
            "claims_3yr": 5,
            "credit_tier": "a",
        })
        assert len(result.failed_rules) > 0
        assert "minimum_age" in result.failed_rules
        assert "vehicle_age" in result.failed_rules
        assert "driving_experience" in result.failed_rules
        assert "claims_limit" in result.failed_rules


# ---------------------------------------------------------------------------
# Determinism tests
# ---------------------------------------------------------------------------

class TestDeterminism:
    """Test that the same input always produces the same output."""

    def test_same_input_same_output(self, sample_product):
        ctx = {
            "age": 35,
            "vehicle_year": 2023,
            "coverage_type": "standard",
            "vehicle_value": 25000,
            "driving_years": 15,
            "claims_3yr": 0,
            "credit_tier": "a",
        }
        r1 = evaluate(sample_product, ctx)
        r2 = evaluate(sample_product, ctx)
        assert r1.total_premium == r2.total_premium
        assert r1.coverage_dict == r2.coverage_dict
        assert r1.surcharges_applied == r2.surcharges_applied
        assert r1.discounts_applied == r2.discounts_applied
