"""
Tests for the Rating DSL expression evaluator.

Tests the safe expression engine that evaluates boolean expressions and
numeric formulas found in rating product configurations.
"""

import pytest
from decimal import Decimal

from rating_dsl.evaluator import Evaluator, ExpressionError


# ---------------------------------------------------------------------------
# Boolean expression tests
# ---------------------------------------------------------------------------

class TestEvaluateBoolean:
    """Test boolean expression evaluation."""

    def setup_method(self):
        self.ctx = {
            "age": 35,
            "vehicle_year": 2023,
            "claims_3yr": 1,
            "credit_tier": "b",
            "driving_years": 15,
            "vehicle_value": 25000,
        }

    def test_comparison_greater_than(self):
        assert Evaluator(self.ctx).evaluate_boolean("age > 30") is True
        assert Evaluator(self.ctx).evaluate_boolean("age > 40") is False

    def test_comparison_less_than(self):
        assert Evaluator(self.ctx).evaluate_boolean("age < 40") is True
        assert Evaluator(self.ctx).evaluate_boolean("age < 30") is False

    def test_comparison_equal(self):
        assert Evaluator(self.ctx).evaluate_boolean("vehicle_year == 2023") is True
        assert Evaluator(self.ctx).evaluate_boolean("vehicle_year == 2020") is False

    def test_comparison_not_equal(self):
        assert Evaluator(self.ctx).evaluate_boolean("credit_tier != 'a'") is True
        assert Evaluator(self.ctx).evaluate_boolean("credit_tier != 'b'") is False

    def test_comparison_gte_lte(self):
        assert Evaluator(self.ctx).evaluate_boolean("age >= 35") is True
        assert Evaluator(self.ctx).evaluate_boolean("age <= 35") is True
        assert Evaluator(self.ctx).evaluate_boolean("age >= 36") is False

    def test_and_operator(self):
        ctx = {"age": 35, "claims_3yr": 0}
        assert Evaluator(ctx).evaluate_boolean("age >= 16 and claims_3yr == 0") is True
        assert Evaluator(ctx).evaluate_boolean("age >= 16 and claims_3yr == 1") is False

    def test_or_operator(self):
        ctx = {"age": 20, "driving_years": 5}
        assert Evaluator(ctx).evaluate_boolean("age < 25 or driving_years >= 10") is True
        assert Evaluator(ctx).evaluate_boolean("age < 25 or driving_years >= 5") is True

    def test_not_operator(self):
        ctx = {"claims_3yr": 0}
        assert Evaluator(ctx).evaluate_boolean("not claims_3yr > 0") is True
        assert Evaluator(ctx).evaluate_boolean("not claims_3yr == 0") is False

    def test_chained_comparison(self):
        ctx = {"age": 35}
        assert Evaluator(ctx).evaluate_boolean("16 <= age <= 99") is True
        assert Evaluator(ctx).evaluate_boolean("16 <= 100 <= 99") is False

    def test_short_circuit_and(self):
        """Test that 'and' short-circuits: False and ... returns False."""
        ctx = {"age": 10}
        assert Evaluator(ctx).evaluate_boolean("age >= 16 and claims_3yr == 0") is False

    def test_short_circuit_or(self):
        """Test that 'or' short-circuits: True or ... returns True."""
        ctx = {"age": 35}
        assert Evaluator(ctx).evaluate_boolean("age >= 16 or claims_3yr == 0") is True


# ---------------------------------------------------------------------------
# Numeric expression tests
# ---------------------------------------------------------------------------

class TestEvaluateNumeric:
    """Test numeric expression evaluation."""

    def setup_method(self):
        self.ctx = {
            "vehicle_value": 25000,
            "base_rate": 100,
            "discount_pct": 10,
            "surcharge_pct": 15,
        }

    def test_addition(self):
        result = Evaluator(self.ctx).evaluate_numeric("base_rate + 25")
        assert result == Decimal("125")

    def test_subtraction(self):
        result = Evaluator(self.ctx).evaluate_numeric("base_rate - 25")
        assert result == Decimal("75")

    def test_multiplication(self):
        result = Evaluator(self.ctx).evaluate_numeric("vehicle_value * 0.008")
        assert result == Decimal("200.00")

    def test_division(self):
        result = Evaluator(self.ctx).evaluate_numeric("vehicle_value / 2")
        assert result == Decimal("12500.00")

    def test_combined_expression(self):
        """Test a realistic premium calculation."""
        ctx = {
            "vehicle_value": 30000,
            "base_rate": 120,
        }
        # vehicle_value * 0.008 + base_rate
        result = Evaluator(ctx).evaluate_numeric("vehicle_value * 0.008 + base_rate")
        assert result == Decimal("360.00")

    def test_parenthesized_expression(self):
        ctx = {"a": 10, "b": 5, "c": 2}
        result = Evaluator(ctx).evaluate_numeric("(a + b) * c")
        assert result == Decimal("30.00")

    def test_unary_negative(self):
        ctx = {"x": 5}
        result = Evaluator(ctx).evaluate_numeric("-x")
        assert result == Decimal("-5")

    def test_unary_positive(self):
        ctx = {"x": 5}
        result = Evaluator(ctx).evaluate_numeric("+x")
        assert result == Decimal("5")

    def test_power_operator(self):
        ctx = {"x": 2}
        result = Evaluator(ctx).evaluate_numeric("x ** 3")
        assert result == Decimal("8.00")


# ---------------------------------------------------------------------------
# Built-in function tests
# ---------------------------------------------------------------------------

class TestBuiltins:
    """Test allowed built-in functions."""

    def test_abs(self):
        ctx = {"x": -5}
        result = Evaluator(ctx).evaluate_numeric("abs(x)")
        assert result == Decimal("5")

    def test_min(self):
        ctx = {"a": 10, "b": 20}
        result = Evaluator(ctx).evaluate_numeric("min(a, b)")
        assert result == Decimal("10")

    def test_max(self):
        ctx = {"a": 10, "b": 20}
        result = Evaluator(ctx).evaluate_numeric("max(a, b)")
        assert result == Decimal("20")

    def test_round(self):
        ctx = {"x": 3.14159}
        result = Evaluator(ctx).evaluate_numeric("round(x, 2)")
        assert result == Decimal("3.14")

    def test_int(self):
        ctx = {"x": 3.7}
        result = Evaluator(ctx).evaluate_numeric("int(x)")
        assert result == Decimal("3")

    def test_float(self):
        ctx = {"x": 5}
        result = Evaluator(ctx).evaluate_numeric("float(x)")
        assert result == Decimal("5.00")

    def test_math_sqrt(self):
        ctx = {"x": 25}
        result = Evaluator(ctx).evaluate_numeric("math.sqrt(x)")
        assert result == Decimal("5.00")

    def test_math_floor(self):
        ctx = {"x": 3.7}
        result = Evaluator(ctx).evaluate_numeric("math.floor(x)")
        assert result == Decimal("3.00")

    def test_math_ceil(self):
        ctx = {"x": 3.2}
        result = Evaluator(ctx).evaluate_numeric("math.ceil(x)")
        assert result == Decimal("4.00")


# ---------------------------------------------------------------------------
# Precision and rounding tests
# ---------------------------------------------------------------------------

class TestPrecision:
    """Test decimal precision and rounding."""

    def test_default_precision(self):
        ctx = {"x": 1, "y": 3}
        result = Evaluator(ctx).evaluate_numeric("x / y")
        assert result == Decimal("0.33")

    def test_custom_precision(self):
        ctx = {"x": 1, "y": 3}
        result = Evaluator(ctx, precision=4).evaluate_numeric("x / y")
        assert result == Decimal("0.3333")

    def test_half_up_rounding(self):
        ctx = {"x": 2.555}
        result = Evaluator(ctx, precision=2, round_mode="half_up").evaluate_numeric("x")
        assert result == Decimal("2.56")

    def test_half_down_rounding(self):
        ctx = {"x": 2.555}
        result = Evaluator(ctx, precision=2, round_mode="half_down").evaluate_numeric("x")
        assert result == Decimal("2.55")

    def test_ceiling_rounding(self):
        ctx = {"x": 2.1}
        result = Evaluator(ctx, precision=0, round_mode="ceiling").evaluate_numeric("x")
        assert result == Decimal("3")

    def test_floor_rounding(self):
        ctx = {"x": 2.9}
        result = Evaluator(ctx, precision=0, round_mode="floor").evaluate_numeric("x")
        assert result == Decimal("2")


# ---------------------------------------------------------------------------
# Safety tests — rejected expressions
# ---------------------------------------------------------------------------

class TestSafety:
    """Test that dangerous expressions are rejected."""

    def test_subprocess_rejected(self):
        ctx = {}
        with pytest.raises(ExpressionError, match="Attribute access|Disallowed"):
            Evaluator(ctx).evaluate_boolean("__import__('os').system('ls')")

    def test_attribute_access_restricted(self):
        ctx = {}
        with pytest.raises(ExpressionError, match="Attribute access only allowed"):
            Evaluator(ctx).evaluate_boolean("str.upper('hello')")

    def test_unknown_function_rejected(self):
        ctx = {}
        with pytest.raises(ExpressionError, match="Attribute access|Unknown function"):
            Evaluator(ctx).evaluate_boolean("open('/etc/passwd').read()")

    def test_syntax_error(self):
        ctx = {}
        with pytest.raises(ExpressionError, match="Syntax error"):
            Evaluator(ctx).evaluate_boolean("age >=")

    def test_unknown_variable(self):
        ctx = {"age": 35}
        with pytest.raises(ExpressionError, match="Unknown variable"):
            Evaluator(ctx).evaluate_boolean("unknown_var > 0")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_value(self):
        ctx = {"x": 0}
        result = Evaluator(ctx).evaluate_boolean("x == 0")
        assert result is True

    def test_negative_value(self):
        ctx = {"x": -5, "y": -3}
        result = Evaluator(ctx).evaluate_boolean("x < y")
        assert result is True

    def test_string_comparison(self):
        ctx = {"tier": "a"}
        result = Evaluator(ctx).evaluate_boolean("tier == 'a'")
        assert result is True

    def test_large_numbers(self):
        ctx = {"x": 1000000, "y": 1000000}
        result = Evaluator(ctx).evaluate_numeric("x + y")
        assert result == Decimal("2000000.00")

    def test_decimal_values(self):
        ctx = {"x": 100.50, "y": 50.25}
        result = Evaluator(ctx).evaluate_numeric("x + y")
        assert result == Decimal("150.75")
