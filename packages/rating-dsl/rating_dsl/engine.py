"""Rating engine — executes the full rating pipeline for a product."""

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
    reason_codes: list[str] = field(default_factory=list)
    raw_context: dict[str, Any] = field(default_factory=dict)

    @property
    def coverage_dict(self) -> dict[str, Decimal]:
        return {c.name: c.final_premium for c in self.coverages}

    @property
    def is_valid(self) -> bool:
        return self.eligibility_passed

    def to_dict(self) -> dict[str, Any]:
        return {
            "product": self.product,
            "jurisdiction": self.jurisdiction,
            "eligible": self.eligibility_passed,
            "failed_rules": self.failed_rules,
            "reason_codes": self.reason_codes,
            "surcharges_applied": self.surcharges_applied,
            "discounts_applied": self.discounts_applied,
            "total_premium": str(self.total_premium),
            "coverages": {c.name: str(c.final_premium) for c in self.coverages},
        }


def evaluate(product: RatingProduct, context: dict[str, Any]) -> RatingResult:
    result = RatingResult(product=product.product, jurisdiction=product.jurisdiction, total_premium=Decimal("0"), raw_context=context)
    output = product.output
    precision = output.precision if output else 2
    round_mode = output.round.value if output else "half_up"
    evaluator = Evaluator(context, precision=precision, round_mode=round_mode)

    result.eligibility_passed, result.failed_rules = _apply_eligibility(product, evaluator)
    if not result.eligibility_passed:
        result.reason_codes = [f"eligibility_failed:{rule}" for rule in result.failed_rules]
        return result

    base_premium = _calculate_base(product, context, evaluator)
    result.surcharges_applied, surcharge_total = _apply_surcharges(product, base_premium, evaluator)
    adjusted_premium = base_premium + surcharge_total
    result.discounts_applied, discount_total = _apply_discounts(product, adjusted_premium, evaluator)

    coverages = _calculate_coverages(product, context, evaluator)
    _apply_global_adjustments(coverages, surcharge_total, discount_total)
    result.coverages = coverages
    _apply_coverage_multipliers(product, coverages, evaluator)
    _enforce_min_max(coverages)
    result.total_premium = sum(c.final_premium for c in coverages)
    return result


def _apply_eligibility(product: RatingProduct, evaluator: Evaluator) -> tuple[bool, list[str]]:
    failed: list[str] = []
    for rule in sorted(product.eligibility, key=lambda r: r.priority):
        try:
            passed = evaluator.evaluate_boolean(rule.rule)
        except ExpressionError as e:
            failed.append(f"error evaluating '{rule.name or rule.rule}': {e}")
            return False, failed
        if not passed:
            failed.append(rule.name or rule.rule)
    return len(failed) == 0, failed


def _calculate_base(product: RatingProduct, context: dict[str, Any], evaluator: Evaluator) -> Decimal:
    coverage_type = context.get("coverage_type")
    if not coverage_type:
        raise ExpressionError("Missing required variable: coverage_type")
    if coverage_type not in product.base_rates:
        allowed = ", ".join(sorted(product.base_rates.keys()))
        raise ExpressionError(f"Unsupported coverage_type '{coverage_type}'. Allowed: {allowed}")
    return evaluator._to_decimal(product.base_rates[coverage_type])


def _apply_surcharges(product: RatingProduct, base_premium: Decimal, evaluator: Evaluator) -> tuple[list[str], Decimal]:
    applied: list[str] = []
    total = Decimal("0")
    for surch in sorted(product.surcharges, key=lambda s: s.priority):
        if evaluator.evaluate_boolean(surch.condition):
            amount = base_premium * (Decimal(str(surch.value)) / Decimal("100")) if surch.type == "percentage" else Decimal(str(surch.value))
            applied.append(surch.name)
            total += amount
    return applied, total


def _apply_discounts(product: RatingProduct, premium: Decimal, evaluator: Evaluator) -> tuple[list[str], Decimal]:
    applied: list[str] = []
    total = Decimal("0")
    for disc in sorted(product.discounts, key=lambda d: d.priority):
        if evaluator.evaluate_boolean(disc.condition):
            amount = premium * (Decimal(str(disc.value)) / Decimal("100")) if disc.type == "percentage" else Decimal(str(disc.value))
            applied.append(disc.name)
            total += amount
    return applied, total


def _calculate_coverages(product: RatingProduct, context: dict[str, Any], evaluator: Evaluator) -> list[CoverageResult]:
    coverages: list[CoverageResult] = []
    coverage_type = context.get("coverage_type")
    for name, cov in product.coverages.items():
        base = cov.base_amount
        if base.type == "fixed":
            base_amount = evaluator._to_decimal(base.value)
        elif base.type == "variable":
            if base.source == "base_rates":
                if coverage_type not in product.base_rates:
                    raise ExpressionError(f"Unsupported coverage_type '{coverage_type}' for base_rates lookup")
                base_amount = evaluator._to_decimal(product.base_rates[coverage_type])
            elif base.source and base.source in context:
                base_amount = evaluator._to_decimal(context[base.source])
            elif base.source and base.source in product.base_rates:
                base_amount = evaluator._to_decimal(product.base_rates[base.source])
            else:
                raise ExpressionError(f"Unknown variable base source '{base.source}' for coverage '{name}'")
        elif base.type == "formula":
            base_amount = evaluator.evaluate_numeric(base.formula) if base.formula else Decimal("0")
        else:
            raise ExpressionError(f"Unsupported base amount type '{base.type}' for coverage '{name}'")
        coverages.append(CoverageResult(name=name, label=cov.label, base_premium=base_amount, surcharge_amount=Decimal("0"), discount_amount=Decimal("0"), final_premium=base_amount, min_premium=cov.min_premium, max_premium=cov.max_premium))
    return coverages


def _apply_global_adjustments(coverages: list[CoverageResult], surcharge_total: Decimal, discount_total: Decimal) -> None:
    total_base = sum(c.final_premium for c in coverages)
    if total_base <= 0:
        return
    for coverage in coverages:
        share = coverage.final_premium / total_base
        coverage.surcharge_amount = surcharge_total * share
        coverage.discount_amount = discount_total * share
        coverage.final_premium = coverage.final_premium + coverage.surcharge_amount - coverage.discount_amount


def _apply_coverage_multipliers(product: RatingProduct, coverages: list[CoverageResult], evaluator: Evaluator) -> None:
    for cov_name, cov_def in product.coverages.items():
        if not cov_def.multiplier:
            continue
        multiplier = cov_def.multiplier
        if multiplier.condition and not evaluator.evaluate_boolean(multiplier.condition):
            continue
        for cr in coverages:
            if cr.name == cov_name:
                if multiplier.type == "percentage":
                    cr.final_premium += cr.final_premium * (Decimal(str(multiplier.value)) / Decimal("100"))
                elif multiplier.type == "flat":
                    cr.final_premium += Decimal(str(multiplier.value))
                elif multiplier.type == "multiplier":
                    cr.final_premium *= Decimal(str(multiplier.value))


def _enforce_min_max(coverages: list[CoverageResult]) -> None:
    for cr in coverages:
        if cr.min_premium and cr.final_premium < cr.min_premium:
            cr.final_premium = cr.min_premium
        if cr.max_premium and cr.final_premium > cr.max_premium:
            cr.final_premium = cr.max_premium
