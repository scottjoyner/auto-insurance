"""
Rating engine — executes the full rating pipeline for a product.

Takes a RatingProduct configuration and a quote context (dict of variable
values), runs the calculation pipeline in order, and returns a RatingResult
with the computed premium for each coverage and the total.

Pipeline steps (in order):
1. apply_eligibility    — Check all eligibility gates; fail fast if any fail
2. calculate_base       — Compute the base premium from base_rates
3. apply_surcharges     — Apply all matching surcharges (in priority order)
4. apply_discounts      — Apply all matching discounts (in priority order)
5. calculate_coverages  — Compute each coverage's base amount
6. apply_coverage_multipliers — Apply coverage-level multipliers
7. enforce_min_max      — Enforce per-coverage min/max premiums
8. compute_total        — Sum all coverages for the total premium
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from rating_dsl.evaluator import Evaluator, ExpressionError
from rating_dsl.models import RatingProduct


class EligibilityError(ValueError):
    """Raised when an eligibility rule fails."""
    def __init__(self, rule_name: str, message: str):
        self.rule_name = rule_name
        self.message = message
        super().__init__(f"Eligibility failed [{rule_name}]: {message}")


@dataclass
class CoverageResult:
    """Result for a single coverage line item."""
    name: str
    label: str
    base_premium: Decimal
    surcharge_amount: Decimal
    discount_amount: Decimal
    final_premium: Decimal
    min_premium: Decimal | None = None
    max_premium: Decimal | None = None


@dataclass
class RatingResult:
    """Complete rating result for a quote."""
    product: str
    jurisdiction: str
    total_premium: Decimal
    coverages: list[CoverageResult] = field(default_factory=list)
    eligibility_passed: bool = True
    failed_rules: list[str] = field(default_factory=list)
    surcharges_applied: list[str] = field(default_factory=list)
    discounts_applied: list[str] = field(default_factory=list)
    raw_context: dict[str, Any] = field(default_factory=dict)

    @property
    def coverage_dict(self) -> dict[str, Decimal]:
        """Return coverages as a {name: premium} dict."""
        return {c.name: c.final_premium for c in self.coverages}

    @property
    def is_valid(self) -> bool:
        return self.eligibility_passed

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for JSON/API responses."""
        return {
            "product": self.product,
            "jurisdiction": self.jurisdiction,
            "eligible": self.eligibility_passed,
            "failed_rules": self.failed_rules,
            "surcharges_applied": self.surcharges_applied,
            "discounts_applied": self.discounts_applied,
            "total_premium": str(self.total_premium),
            "coverages": {c.name: str(c.final_premium) for c in self.coverages},
        }


def evaluate(
    product: RatingProduct,
    context: dict[str, Any],
) -> RatingResult:
    """
    Run the full rating pipeline for a product with the given quote context.

    Args:
        product: A loaded RatingProduct configuration.
        context: Quote variable values, e.g. {"age": 35, "vehicle_year": 2023, ...}

    Returns:
        A RatingResult with computed premiums.

    Raises:
        EligibilityError: If any eligibility rule fails (legacy API).
        ExpressionError: If an expression cannot be evaluated.
    """
    result = RatingResult(
        product=product.product,
        jurisdiction=product.jurisdiction,
        total_premium=Decimal("0"),
        raw_context=context,
    )

    # Build the evaluator with configured precision
    output = product.output
    precision = output.precision if output else 2
    round_mode = output.round.value if output else "half_up"

    evaluator = Evaluator(context, precision=precision, round_mode=round_mode)

    # Step 1: Apply eligibility
    result.eligibility_passed, result.failed_rules = _apply_eligibility(
        product, evaluator
    )
    if not result.eligibility_passed:
        return result  # Fail fast

    # Step 2: Calculate base premium
    base_premium = _calculate_base(product, context, evaluator)

    # Step 3: Apply surcharges
    result.surcharges_applied, surcharge_total = _apply_surcharges(
        product, base_premium, evaluator
    )
    adjusted_premium = base_premium + surcharge_total

    # Step 4: Apply discounts
    result.discounts_applied, discount_total = _apply_discounts(
        product, adjusted_premium, evaluator
    )
    adjusted_premium -= discount_total

    # Step 5: Calculate coverages
    coverages = _calculate_coverages(product, adjusted_premium, evaluator)
    result.coverages = coverages

    # Step 6: Apply coverage multipliers
    _apply_coverage_multipliers(product, coverages, evaluator)

    # Step 7: Enforce min/max
    _enforce_min_max(coverages)

    # Step 8: Compute total
    result.total_premium = sum(c.final_premium for c in coverages)

    return result


# ---------------------------------------------------------------------------
# Pipeline step implementations
# ---------------------------------------------------------------------------

def _apply_eligibility(
    product: RatingProduct, evaluator: Evaluator
) -> tuple[bool, list[str]]:
    """Check all eligibility rules. Returns (passed, failed_rule_names)."""
    failed: list[str] = []
    for rule in product.eligibility:
        try:
            passed = evaluator.evaluate_boolean(rule.rule)
        except ExpressionError as e:
            failed.append(f"error evaluating '{rule.name or rule.rule}': {e}")
            return False, failed
        if not passed:
            failed.append(rule.name or rule.rule)
    return len(failed) == 0, failed


def _calculate_base(product: RatingProduct, context: dict[str, Any], evaluator: Evaluator) -> Decimal:
    """Calculate the base premium from base_rates and the quote context."""
    coverage_type = context.get("coverage_type", "standard")
    if coverage_type in product.base_rates:
        return evaluator._to_decimal(product.base_rates[coverage_type])
    # Default to the first base rate
    first_rate = next(iter(product.base_rates.values()))
    return evaluator._to_decimal(first_rate)


def _apply_surcharges(
    product: RatingProduct,
    base_premium: Decimal,
    evaluator: Evaluator,
) -> tuple[list[str], Decimal]:
    """Apply all matching surcharges. Returns (names, total_surcharged_amount)."""
    applied: list[str] = []
    total: Decimal = Decimal("0")

    # Sort by priority (lower first)
    sorted_surcharges = sorted(product.surcharges, key=lambda s: s.priority)  # type: ignore[attr-defined]

    for surch in sorted_surcharges:
        try:
            if evaluator.evaluate_boolean(surch.condition):  # type: ignore[attr-defined]
                surcharge_pct = float(surch.value) / 100  # type: ignore[attr-defined]
                amount = base_premium * Decimal(str(surcharge_pct))
                applied.append(surch.name)  # type: ignore[attr-defined]
                total += amount
        except ExpressionError:
            pass  # Skip if condition can't be evaluated

    return applied, total


def _apply_discounts(
    product: RatingProduct,
    premium: Decimal,
    evaluator: Evaluator,
) -> tuple[list[str], Decimal]:
    """Apply all matching discounts. Returns (names, total_discounted_amount)."""
    applied: list[str] = []
    total: Decimal = Decimal("0")

    # Sort by priority (lower first)
    sorted_discounts = sorted(product.discounts, key=lambda d: d.priority)  # type: ignore[attr-defined]

    for disc in sorted_discounts:
        try:
            if evaluator.evaluate_boolean(disc.condition):  # type: ignore[attr-defined]
                disc_pct = float(disc.value) / 100  # type: ignore[attr-defined]
                amount = premium * Decimal(str(disc_pct))
                applied.append(disc.name)  # type: ignore[attr-defined]
                total += amount
        except ExpressionError:
            pass  # Skip if condition can't be evaluated

    return applied, total


def _calculate_coverages(
    product: RatingProduct,
    total_premium: Decimal,
    evaluator: Evaluator,
) -> list[CoverageResult]:
    """Calculate base amounts for each coverage."""
    coverages: list[CoverageResult] = []

    for name, cov in product.coverages.items():
        base = cov.base_amount

        if base.type == "fixed":
            base_amount = evaluator._to_decimal(base.value)
        elif base.type == "variable":
            if base.source and base.source in product.base_rates:
                base_amount = evaluator._to_decimal(product.base_rates[base.source])
            else:
                base_amount = Decimal("0")
        elif base.type == "formula":
            if base.formula:
                base_amount = evaluator.evaluate_numeric(base.formula)
            else:
                base_amount = Decimal("0")
        else:
            base_amount = Decimal("0")

        coverages.append(CoverageResult(
            name=name,
            label=cov.label,
            base_premium=base_amount,
            surcharge_amount=Decimal("0"),
            discount_amount=Decimal("0"),
            final_premium=base_amount,
            min_premium=cov.min_premium,
            max_premium=cov.max_premium,
        ))

    return coverages


def _apply_coverage_multipliers(
    product: RatingProduct,
    coverages: list[CoverageResult],
    evaluator: Evaluator,
) -> None:
    """Apply coverage-level multipliers."""
    for cov_def in product.coverages.values():
        if not cov_def.multiplier:
            continue

        multiplier = cov_def.multiplier
        # Check condition
        if multiplier.condition:
            try:
                if not evaluator.evaluate_boolean(multiplier.condition):
                    continue
            except ExpressionError:
                continue

        # Apply multiplier
        for cr in coverages:
            if cr.name == cov_def.name:
                if multiplier.type == "percentage":
                    factor = float(multiplier.value) / 100
                    cr.final_premium += cr.final_premium * Decimal(str(factor))
                elif multiplier.type == "flat":
                    cr.final_premium += Decimal(str(multiplier.value))
                elif multiplier.type == "multiplier":
                    cr.final_premium *= Decimal(str(multiplier.value))


def _enforce_min_max(coverages: list[CoverageResult]) -> None:
    """Enforce per-coverage minimum and maximum premiums."""
    for cr in coverages:
        if cr.min_premium and cr.final_premium < cr.min_premium:
            cr.final_premium = cr.min_premium
        if cr.max_premium and cr.final_premium > cr.max_premium:
            cr.final_premium = cr.max_premium
