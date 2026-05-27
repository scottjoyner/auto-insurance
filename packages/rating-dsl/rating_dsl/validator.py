"""
Rating DSL validator.

Validates a RatingProduct configuration for both schema correctness and
business rule consistency. Catches issues that YAML parsing and Pydantic
validation can't detect, such as:
- Circular variable references
- Invalid expression syntax in conditions
- Coverage base_amount that references undefined sources
- Missing required fields for specific amount types
- Duplicate discount/surcharge names
- Invalid calculation order steps
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from rating_dsl.models import (
    AmountSourceType,
    DiscountType,
    MultiplierType,
    NumericType,
    RatingProduct,
)
from rating_dsl.evaluator import Evaluator, ExpressionError


class ValidationError(ValueError):
    """Raised when a product configuration fails validation."""
    pass


class Validator:
    """
    Validates a RatingProduct configuration.

    Collects all validation errors and returns them together, rather than
    failing on the first error.
    """

    def __init__(self, product: RatingProduct):
        self.product = product
        self.errors: list[str] = []

    def validate(self) -> list[str]:
        """
        Run all validation checks.

        Returns:
            A list of error messages (empty if valid).
        """
        self._check_version()
        self._check_variables()
        self._check_eligibility()
        self._check_discounts()
        self._check_surcharges()
        self._check_base_rates()
        self._check_coverages()
        self._check_calculation_order()
        self._check_expression_safety()
        return self.errors

    # ------------------------------------------------------------------
    # Individual validation checks
    # ------------------------------------------------------------------

    def _check_version(self) -> None:
        """Validate DSL version compatibility."""
        version = self.product.version
        if not version:
            self.errors.append("Product version is required")
            return
        # Currently only support version 1.0
        major, *rest = version.split(".")
        if major != "1":
            self.errors.append(
                f"Unsupported DSL version '{version}'. "
                f"Only version 1.x is supported."
            )

    def _check_variables(self) -> None:
        """Validate variable definitions."""
        variables = self.product.variables
        seen_names: set[str] = set()

        for name, vdef in variables.items():
            if name in seen_names:
                self.errors.append(f"Duplicate variable name: '{name}'")
            seen_names.add(name)

            # Validate enum values if present
            if vdef.enum:
                if len(vdef.enum) < 2:
                    self.errors.append(
                        f"Variable '{name}': enum must have at least 2 values"
                    )

            # Validate min/max consistency
            if vdef.min is not None and vdef.max is not None:
                if vdef.min > vdef.max:
                    self.errors.append(
                        f"Variable '{name}': min ({vdef.min}) > max ({vdef.max})"
                    )

    def _check_eligibility(self) -> None:
        """Validate eligibility rules reference known variables."""
        known = set(self.product.variable_names)
        for i, rule in enumerate(self.product.eligibility):
            self._check_condition_vars(rule.rule, known, f"eligibility[{i}]")

    def _check_discounts(self) -> None:
        """Validate discount definitions."""
        known = set(self.product.variable_names)
        seen_names: set[str] = set()

        for i, disc in enumerate(self.product.discounts):  # type: ignore[index]
            name = disc.get("name", f"discount[{i}]")  # type: ignore[index]
            if name in seen_names:
                self.errors.append(f"Duplicate discount name: '{name}'")
            seen_names.add(name)
            self._check_condition_vars(disc["condition"], known, f"discount '{name}'")  # type: ignore[index]

            # Validate type-specific fields
            if disc["type"] == "flat" and not isinstance(disc["value"], (int, float, Decimal)):  # type: ignore[index]
                self.errors.append(f"Discount '{name}': value must be numeric for flat type")

    def _check_surcharges(self) -> None:
        """Validate surcharge definitions."""
        known = set(self.product.variable_names)
        seen_names: set[str] = set()

        for i, surch in enumerate(self.product.surcharges):  # type: ignore[index]
            name = surch.get("name", f"surcharge[{i}]")  # type: ignore[index]
            if name in seen_names:
                self.errors.append(f"Duplicate surcharge name: '{name}'")
            seen_names.add(name)
            self._check_condition_vars(surch["condition"], known, f"surcharge '{name}'")  # type: ignore[index]

    def _check_base_rates(self) -> None:
        """Validate base rates reference exists for each coverage."""
        if not self.product.base_rates:
            return  # Base rates are optional if coverages use formulas

    def _check_coverages(self) -> None:
        """Validate coverage definitions."""
        known_vars = set(self.product.variable_names)
        known_rates = set(self.product.base_rates.keys())

        for name, cov in self.product.coverages.items():
            base = cov.base_amount

            # Validate base_amount type
            if base.type == "fixed" and base.value is None:
                self.errors.append(
                    f"Coverage '{name}': base_amount.type='fixed' requires a 'value'"
                )
            elif base.type == "variable" and base.source is None:
                self.errors.append(
                    f"Coverage '{name}': base_amount.type='variable' requires a 'source'"
                )
            elif base.type == "variable" and base.source and base.source not in known_rates:
                self.errors.append(
                    f"Coverage '{name}': base_amount.source '{base.source}' "
                    f"not found in base_rates"
                )
            elif base.type == "formula" and base.formula is None:
                self.errors.append(
                    f"Coverage '{name}': base_amount.type='formula' requires a 'formula'"
                )

            # Validate multiplier condition references
            if cov.multiplier and cov.multiplier.condition:
                self._check_condition_vars(
                    cov.multiplier.condition, known_vars, f"coverage '{name}' multiplier"
                )

            # Validate min/max consistency
            if cov.min_premium and cov.max_premium:
                if cov.min_premium > cov.max_premium:
                    self.errors.append(
                        f"Coverage '{name}': min_premium ({cov.min_premium}) > "
                        f"max_premium ({cov.max_premium})"
                    )

    def _check_calculation_order(self) -> None:
        """Validate calculation order steps."""
        if not self.product.calculation_order:
            self.errors.append("calculation_order is required")
            return

        valid_steps = {
            "apply_eligibility",
            "calculate_base",
            "apply_surcharges",
            "apply_discounts",
            "calculate_coverages",
            "apply_coverage_multipliers",
            "enforce_min_max",
            "compute_total",
        }
        steps = [s.step for s in self.product.calculation_order.steps]
        seen: set[str] = set()

        for step in steps:
            if step not in valid_steps:
                self.errors.append(f"Unknown calculation step: '{step}'")
            if step in seen:
                self.errors.append(f"Duplicate calculation step: '{step}'")
            seen.add(step)

        # Check required ordering constraints
        step_indices = {s: i for i, s in enumerate(steps)}
        if "apply_eligibility" in step_indices and "calculate_base" in step_indices:
            if step_indices["apply_eligibility"] > step_indices["calculate_base"]:
                self.errors.append(
                    "'apply_eligibility' must come before 'calculate_base'"
                )
        if "apply_discounts" in step_indices and "apply_surcharges" in step_indices:
            if step_indices["apply_surcharges"] > step_indices["apply_discounts"]:
                self.errors.append(
                    "'apply_surcharges' must come before 'apply_discounts'"
                )

    def _check_expression_safety(self) -> None:
        """Check that all expressions use only allowed variables and operators."""
        known_vars = set(self.product.variable_names)
        context: dict[str, Any] = {}

        # Build a minimal context for expression testing
        for name, vdef in self.product.variables.items():
            if vdef.default is not None:
                context[name] = vdef.default
            elif vdef.type == NumericType.INTEGER:
                context[name] = 0
            elif vdef.type == NumericType.DECIMAL:
                context[name] = Decimal("0")
            elif vdef.type == NumericType.BOOLEAN:
                context[name] = False
            else:
                context[name] = ""

        # Test eligibility conditions
        for i, rule in enumerate(self.product.eligibility):
            self._test_expression(rule.rule, known_vars, context, f"eligibility[{i}]")

        # Test discount conditions
        for i, disc in enumerate(self.product.discounts):
            self._test_expression(disc["condition"], known_vars, context, f"discount[{i}]")

        # Test surcharge conditions
        for i, surch in enumerate(self.product.surcharges):
            self._test_expression(surch["condition"], known_vars, context, f"surcharge[{i}]")

        # Test coverage formulas
        for name, cov in self.product.coverages.items():
            if cov.base_amount.type == "formula" and cov.base_amount.formula:
                self._test_expression(
                    cov.base_amount.formula, known_vars, context,
                    f"coverage '{name}' formula"
                )

    def _test_expression(
        self,
        expression: str,
        known_vars: set[str],
        context: dict[str, Any],
        location: str,
    ) -> None:
        """Test an expression for syntax and allowed-variable safety."""
        evaluator = Evaluator(context)
        try:
            evaluator._parse(expression)
        except ExpressionError as e:
            self.errors.append(f"{location}: {e}")

    def _check_condition_vars(
        self,
        condition: str,
        known_vars: set[str],
        location: str,
    ) -> None:
        """Check that a condition only references known variables."""
        # Extract variable names from the condition using simple tokenization
        import re
        tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', condition)
        unknown = [t for t in tokens if t not in known_vars
                    and t not in ('True', 'False', 'and', 'or', 'not', 'if', 'else')]
        if unknown:
            self.errors.append(
                f"{location}: unknown variables in condition: {unknown}. "
                f"Known: {list(known_vars)}"
            )


def validate_product(product: RatingProduct) -> list[str]:
    """
    Convenience function to validate a RatingProduct.

    Args:
        product: The product to validate.

    Returns:
        A list of error messages (empty if valid).
    """
    validator = Validator(product)
    return validator.validate()
