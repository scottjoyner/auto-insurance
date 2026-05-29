from decimal import Decimal
from pathlib import Path

import pytest

from rating_dsl.engine import evaluate
from rating_dsl.evaluator import ExpressionError
from rating_dsl.parser import load_product


PRODUCT_PATH = Path(__file__).resolve().parents[3] / "data" / "sample-products" / "sample_personal_auto_v1.yml"


def _base_context(**overrides):
    context = {
        "age": 35,
        "vehicle_year": 2023,
        "coverage_type": "standard",
        "vehicle_value": 25000,
        "driving_years": 15,
        "claims_3yr": 0,
        "credit_tier": "a",
    }
    context.update(overrides)
    return context


def test_standard_quote_uses_selected_base_rate_for_liability():
    product = load_product(PRODUCT_PATH)
    result = evaluate(product, _base_context())

    assert result.eligibility_passed is True
    assert "liability" in result.coverage_dict
    assert result.coverage_dict["liability"] > Decimal("0")
    assert result.coverage_dict["liability"] >= Decimal("50.00")
    assert result.total_premium == sum(result.coverage_dict.values())


def test_unknown_coverage_type_fails_closed():
    product = load_product(PRODUCT_PATH)

    with pytest.raises(ExpressionError):
        evaluate(product, _base_context(coverage_type="full"))


def test_eligibility_failure_returns_reason_code():
    product = load_product(PRODUCT_PATH)
    result = evaluate(product, _base_context(age=15))

    assert result.eligibility_passed is False
    assert "minimum_age" in result.failed_rules
    assert "eligibility_failed:minimum_age" in result.reason_codes
    assert result.total_premium == Decimal("0")
