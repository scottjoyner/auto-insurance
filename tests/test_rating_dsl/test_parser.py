"""
Tests for the Rating DSL parser.

Tests YAML loading, type coercion, and model construction.
"""

import pytest
from decimal import Decimal
from pathlib import Path

from rating_dsl.parser import load_product, parse_product_dict, ParseError


SAMPLE_YAML = """
version: "1.0"
product: test_product_v1
jurisdiction: SAMPLE

variables:
  age:
    type: integer
    description: Applicant age
    min: 16
    max: 99
  vehicle_year:
    type: integer
    description: Vehicle model year
  coverage_type:
    type: string
    enum: [basic, standard, premium]
  vehicle_value:
    type: decimal
    description: Current market value
  claims_3yr:
    type: integer
    description: Claims in last 3 years
  credit_tier:
    type: string
    enum: [a, b, c, d, e]

eligibility:
  - name: age_check
    rule: age >= 16
    fail: "Must be at least 16"
    priority: 1
  - name: claims_check
    rule: claims_3yr <= 3
    fail: "Too many claims"
    priority: 2

discounts:
  - name: clean_driver
    type: percentage
    value: 10.0
    condition: claims_3yr == 0
    description: "10% off for clean driving"
    priority: 1

surcharges:
  - name: young_driver
    type: percentage
    value: 25.0
    condition: age < 25
    description: "25% for young drivers"
    priority: 1

base_rates:
  basic: 85.00
  standard: 120.00
  premium: 175.00

coverages:
  liability:
    label: "Bodily Injury & Property Liability"
    base_amount:
      type: variable
      source: base_rates
    min_premium: 50.00
    max_premium: 500.00
  collision:
    label: "Collision Coverage"
    base_amount:
      type: formula
      formula: "vehicle_value * 0.008"
    multiplier:
      type: percentage
      value: 75.0
  comprehensive:
    label: "Comprehensive Coverage"
    base_amount:
      type: fixed
      value: 30.00

calculation_order:
  steps:
    - step: apply_eligibility
    - step: calculate_base
    - step: apply_surcharges
    - step: apply_discounts
    - step: calculate_coverages
    - step: apply_coverage_multipliers
    - step: enforce_min_max
    - step: compute_total

output:
  currency: USD
  precision: 2
  round: half_up
"""


# ---------------------------------------------------------------------------
# load_product tests
# ---------------------------------------------------------------------------

class TestLoadProduct:
    """Test loading products from YAML files."""

    def test_load_existing_file(self):
        """Load the sample personal auto product."""
        # Resolve relative to this file's location
        base = Path(__file__).resolve().parent.parent.parent
        sample_path = base / "data" / "sample-products" / "sample_personal_auto_v1.yml"
        if sample_path.exists():
            product = load_product(sample_path)
            assert product.product == "sample_personal_auto_v1"
            assert product.version == "1.0"
            assert product.jurisdiction == "SAMPLE"

    def test_load_nonexistent_file(self):
        """Loading a nonexistent file raises ParseError."""
        with pytest.raises(ParseError, match="not found"):
            load_product("/nonexistent/path.yml")

    def test_load_invalid_yaml(self):
        """Invalid YAML raises ParseError."""
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("{{invalid yaml: [")
            f.flush()
            with pytest.raises(ParseError, match="YAML parse error"):
                load_product(f.name)


# ---------------------------------------------------------------------------
# parse_product_dict tests
# ---------------------------------------------------------------------------

class TestParseProductDict:
    """Test parsing raw YAML dicts."""

    def test_minimal_product(self):
        """Parse a minimal valid product config."""
        raw = {
            "version": "1.0",
            "product": "min_test",
            "jurisdiction": "SAMPLE",
        }
        product = parse_product_dict(raw)
        assert product.product == "min_test"
        assert product.version == "1.0"
        assert product.jurisdiction == "SAMPLE"
        assert product.variables == {}
        assert product.eligibility == []
        assert product.coverages == {}

    def test_missing_required_fields(self):
        """Missing required fields raise ParseError."""
        for field in ("version", "product", "jurisdiction"):
            raw = {
                "version": "1.0",
                "product": "test",
                "jurisdiction": "SAMPLE",
            }
            del raw[field]
            with pytest.raises(ParseError, match=f"Missing required field '{field}'"):
                parse_product_dict(raw)

    def test_full_product(self):
        """Parse a full product config with all fields."""
        import yaml
        raw = yaml.safe_load(SAMPLE_YAML)
        product = parse_product_dict(raw)

        assert product.product == "test_product_v1"
        assert len(product.variables) == 6
        assert len(product.eligibility) == 2
        assert len(product.discounts) == 1
        assert len(product.surcharges) == 1
        assert len(product.base_rates) == 3
        assert len(product.coverages) == 3

        # Check variable types
        assert product.variables["age"].type == "integer"
        assert product.variables["coverage_type"].type == "string"
        assert product.variables["vehicle_value"].type == "decimal"

        # Check base rates
        assert product.base_rates["basic"] == Decimal("85.00")
        assert product.base_rates["standard"] == Decimal("120.00")

        # Check eligibility
        assert product.eligibility[0].name == "age_check"
        assert product.eligibility[0].rule == "age >= 16"

        # Check discounts
        assert product.discounts[0].name == "clean_driver"
        assert product.discounts[0].value == Decimal("10.0")

        # Check coverages
        cov = product.coverages["collision"]
        assert cov.label == "Collision Coverage"
        assert cov.base_amount.type == "formula"
        assert cov.base_amount.formula == "vehicle_value * 0.008"

        # Check calculation order
        assert product.calculation_order is not None
        assert len(product.calculation_order.steps) == 8

        # Check output
        assert product.output is not None
        assert product.output.currency.value == "USD"


# ---------------------------------------------------------------------------
# Variable parsing tests
# ---------------------------------------------------------------------------

class TestVariableParsing:
    """Test variable definition parsing."""

    def test_type_aliases(self):
        """Test type name aliases (int -> integer, float -> decimal)."""
        raw = {
            "version": "1.0",
            "product": "test",
            "jurisdiction": "SAMPLE",
            "variables": {
                "age": {"type": "int"},
                "value": {"type": "float"},
                "name": {"type": "str"},
                "active": {"type": "bool"},
            },
        }
        product = parse_product_dict(raw)
        assert product.variables["age"].type == "integer"
        assert product.variables["value"].type == "decimal"
        assert product.variables["name"].type == "string"
        assert product.variables["active"].type == "boolean"

    def test_variable_with_enum(self):
        """Test enum variable parsing."""
        raw = {
            "version": "1.0",
            "product": "test",
            "jurisdiction": "SAMPLE",
            "variables": {
                "tier": {"type": "string", "enum": ["a", "b", "c"]},
            },
        }
        product = parse_product_dict(raw)
        assert product.variables["tier"].enum == ["a", "b", "c"]

    def test_variable_with_min_max(self):
        """Test min/max constraint parsing."""
        raw = {
            "version": "1.0",
            "product": "test",
            "jurisdiction": "SAMPLE",
            "variables": {
                "age": {"type": "integer", "min": 16, "max": 99},
            },
        }
        product = parse_product_dict(raw)
        assert product.variables["age"].min == 16
        assert product.variables["age"].max == 99


# ---------------------------------------------------------------------------
# Coverage parsing tests
# ---------------------------------------------------------------------------

class TestCoverageParsing:
    """Test coverage definition parsing."""

    def test_fixed_base_amount(self):
        """Test coverage with fixed base amount."""
        raw = {
            "version": "1.0",
            "product": "test",
            "jurisdiction": "SAMPLE",
            "coverages": {
                "medpay": {
                    "label": "Medical Payments",
                    "base_amount": {"type": "fixed", "value": 15.00},
                },
            },
        }
        product = parse_product_dict(raw)
        cov = product.coverages["medpay"]
        assert cov.base_amount.type == "fixed"
        assert cov.base_amount.value == Decimal("15.00")

    def test_formula_base_amount(self):
        """Test coverage with formula base amount."""
        raw = {
            "version": "1.0",
            "product": "test",
            "jurisdiction": "SAMPLE",
            "coverages": {
                "collision": {
                    "label": "Collision",
                    "base_amount": {"type": "formula", "formula": "vehicle_value * 0.008"},
                },
            },
        }
        product = parse_product_dict(raw)
        cov = product.coverages["collision"]
        assert cov.base_amount.type == "formula"
        assert cov.base_amount.formula == "vehicle_value * 0.008"

    def test_variable_base_amount(self):
        """Test coverage with variable base amount."""
        raw = {
            "version": "1.0",
            "product": "test",
            "jurisdiction": "SAMPLE",
            "base_rates": {"standard": 120.00},
            "coverages": {
                "liability": {
                    "label": "Liability",
                    "base_amount": {"type": "variable", "source": "base_rates"},
                },
            },
        }
        product = parse_product_dict(raw)
        cov = product.coverages["liability"]
        assert cov.base_amount.type == "variable"
        assert cov.base_amount.source == "base_rates"
