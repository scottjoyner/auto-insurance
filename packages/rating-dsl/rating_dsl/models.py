"""
Core Pydantic data models for the Rating DSL.

These define the typed representation of a rating product configuration,
the variables it accepts, eligibility rules, discounts, surcharges,
coverages, and the calculation pipeline.
"""

from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class NumericType(str, Enum):
    INTEGER = "integer"
    DECIMAL = "decimal"
    STRING = "string"
    BOOLEAN = "boolean"


class AmountSourceType(str, Enum):
    FIXED = "fixed"
    VARIABLE = "variable"
    FORMULA = "formula"


class DiscountType(str, Enum):
    PERCENTAGE = "percentage"
    FLAT = "flat"


class MultiplierType(str, Enum):
    PERCENTAGE = "percentage"
    FLAT = "flat"
    MULTIPLIER = "multiplier"


class RoundMode(str, Enum):
    HALF_UP = "half_up"
    HALF_DOWN = "half_down"
    CEILING = "ceiling"
    FLOOR = "floor"


class OutputCurrency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


# ---------------------------------------------------------------------------
# Variable definitions
# ---------------------------------------------------------------------------

class VariableDef(BaseModel):
    """A single input variable that the product accepts from the quote context."""

    name: str = Field(description="Variable name, used in expressions")
    type: NumericType = Field(description="NumericType.INTEGER | DECIMAL | STRING | BOOLEAN")
    description: str = Field(default="", description="Human-readable description")
    enum: Optional[list[str]] = Field(default=None, description="Allowed values for string/integer variables")
    default: Optional[Any] = Field(default=None, description="Fallback if not provided by caller")
    min: Optional[Decimal | int | float] = Field(default=None, description="Minimum allowed value")
    max: Optional[Decimal | int | float] = Field(default=None, description="Maximum allowed value")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: NumericType) -> NumericType:
        if v not in NumericType:
            raise ValueError(f"Invalid numeric type: {v}")
        return v


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------

class EligibilityRule(BaseModel):
    """A single eligibility gate. If the condition is False, the quote fails."""

    name: str = Field(default="", description="Optional human-readable name for the rule")
    rule: str = Field(description="Boolean expression, e.g. 'age >= 16'")
    fail: str = Field(description="Error message shown when the rule fails")
    priority: int = Field(default=0, description="Lower numbers evaluated first")


# ---------------------------------------------------------------------------
# Discounts & Surcharges
# ---------------------------------------------------------------------------

class ConditionalAmount(BaseModel):
    """A named discount or surcharge with a condition."""

    name: str = Field(description="Unique identifier for this discount/surcharge")
    type: DiscountType | MultiplierType = Field(description="percentage or flat")
    value: Decimal | int | float = Field(description="Numeric value")
    condition: str = Field(description="Boolean expression that must be True to apply")
    description: str = Field(default="", description="Human-readable description")
    priority: int = Field(default=0, description="Lower numbers applied first")


# ---------------------------------------------------------------------------
# Coverage definitions
# ---------------------------------------------------------------------------

class BaseAmount(BaseModel):
    """How the base amount for a coverage is determined."""

    type: AmountSourceType = Field(description="fixed | variable | formula")
    value: Optional[Decimal | int | float] = Field(default=None, description="Fixed value (used when type=fixed)")
    source: Optional[str] = Field(default=None, description="Variable name reference (used when type=variable)")
    formula: Optional[str] = Field(default=None, description="Expression string (used when type=formula)")


class CoverageDef(BaseModel):
    """A single coverage line item (e.g. collision, comprehensive)."""

    name: str = Field(description="Coverage key, used as the dict key")
    label: str = Field(description="Human-readable label")
    base_amount: BaseAmount = Field(description="How the base premium is calculated")
    multiplier: Optional[ConditionalMultiplier] = Field(default=None, description="Coverage-level multiplier")
    min_premium: Optional[Decimal] = Field(default=None, description="Minimum premium for this coverage")
    max_premium: Optional[Decimal] = Field(default=None, description="Maximum premium for this coverage")


class ConditionalMultiplier(BaseModel):
    """A coverage-level multiplier (percentage, flat, or raw multiplier)."""

    type: MultiplierType = Field(description="percentage | flat | multiplier")
    value: Decimal | int | float = Field(description="Numeric value")
    condition: Optional[str] = Field(default=None, description="Optional condition to apply")


# ---------------------------------------------------------------------------
# Calculation pipeline
# ---------------------------------------------------------------------------

class PipelineStep(BaseModel):
    """A single step in the calculation pipeline."""

    step: str = Field(description="Step name, e.g. 'apply_eligibility'")


class CalculationOrder(BaseModel):
    """The ordered list of steps in the rating pipeline."""

    steps: list[PipelineStep] = Field(description="Ordered steps")


# ---------------------------------------------------------------------------
# Output configuration
# ---------------------------------------------------------------------------

class OutputConfig(BaseModel):
    """Output formatting settings."""

    currency: OutputCurrency = Field(default=OutputCurrency.USD)
    precision: int = Field(default=2, ge=0, le=10)
    round: RoundMode = Field(default=RoundMode.HALF_UP)


# ---------------------------------------------------------------------------
# Root product config
# ---------------------------------------------------------------------------

class RatingProduct(BaseModel):
    """
    The complete rating product configuration, loaded from YAML and validated.

    This is the top-level model that represents a single insurance product's
    rating ruleset. It includes variables, eligibility gates, discounts,
    surcharges, coverages, calculation order, and output settings.
    """

    version: str = Field(description="DSL schema version, e.g. '1.0'")
    product: str = Field(description="Product identifier, e.g. 'sample_personal_auto_v1'")
    jurisdiction: str = Field(description="Jurisdiction code, e.g. 'SAMPLE'")

    variables: dict[str, VariableDef] = Field(default_factory=dict)
    eligibility: list[EligibilityRule] = Field(default_factory=list)
    discounts: list[ConditionalAmount] = Field(default_factory=list)
    surcharges: list[ConditionalAmount] = Field(default_factory=list)
    base_rates: dict[str, Decimal] = Field(default_factory=dict)
    coverages: dict[str, CoverageDef] = Field(default_factory=dict)
    calculation_order: Optional[CalculationOrder] = Field(default=None)
    output: Optional[OutputConfig] = Field(default=None)

    @property
    def eligible_steps(self) -> list[str]:
        """Return the list of step names from the calculation order."""
        if self.calculation_order:
            return [s.step for s in self.calculation_order.steps]
        return self._default_steps()

    @staticmethod
    def _default_steps() -> list[str]:
        return [
            "apply_eligibility",
            "calculate_base",
            "apply_surcharges",
            "apply_discounts",
            "calculate_coverages",
            "apply_coverage_multipliers",
            "enforce_min_max",
            "compute_total",
        ]

    @property
    def variable_names(self) -> list[str]:
        return list(self.variables.keys())

    @property
    def coverage_names(self) -> list[str]:
        return list(self.coverages.keys())
