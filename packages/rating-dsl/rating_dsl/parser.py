"""
Rating DSL YAML parser.

Loads a YAML product configuration file and converts it into a validated
`RatingProduct` model. Handles type coercion, defaults, and basic schema
validation before the full validator runs.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from rating_dsl.models import (
    AmountSourceType,
    BaseAmount,
    ConditionalMultiplier,
    CoverageDef,
    DiscountType,
    EligibilityRule,
    MultiplierType,
    OutputConfig,
    OutputCurrency,
    RatingProduct,
    RoundMode,
    VariableDef,
)


class ParseError(ValueError):
    """Raised when YAML parsing or type coercion fails."""
    pass


def load_product(yaml_path: str | Path) -> RatingProduct:
    """
    Load a rating product configuration from a YAML file.

    Args:
        yaml_path: Path to the YAML file.

    Returns:
        A validated RatingProduct model.

    Raises:
        ParseError: If the file cannot be parsed or types are invalid.
    """
    path = Path(yaml_path)
    if not path.exists():
        raise ParseError(f"Product file not found: {path}")

    try:
        with open(path, "r") as f:
            raw = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ParseError(f"YAML parse error in {path}: {e}") from e

    if not isinstance(raw, dict):
        raise ParseError(f"Expected a YAML mapping at the root of {path}")

    return parse_product_dict(raw, source=str(path))


def parse_product_dict(raw: dict[str, Any], source: str = "<string>") -> RatingProduct:
    """
    Parse a raw YAML dict into a RatingProduct model.

    Args:
        raw: The parsed YAML dictionary.
        source: Human-readable source identifier for error messages.

    Returns:
        A RatingProduct model.

    Raises:
        ParseError: If required fields are missing or types are invalid.
    """
    # --- Top-level required fields ---
    for field in ("version", "product", "jurisdiction"):
        if field not in raw:
            raise ParseError(f"Missing required field '{field}' in {source}")

    # --- Variables ---
    variables: dict[str, VariableDef] = {}
    if "variables" in raw and raw["variables"]:
        for name, vdef in raw["variables"].items():
            if not isinstance(vdef, dict):
                raise ParseError(f"Variable '{name}' in {source} must be a mapping")
            variables[name] = _parse_variable(vdef, name, source)

    # --- Eligibility ---
    eligibility: list[EligibilityRule] = []
    if "eligibility" in raw and raw["eligibility"]:
        for item in raw["eligibility"]:
            if not isinstance(item, dict):
                raise ParseError(f"Eligibility rule in {source} must be a mapping")
            eligibility.append(_parse_eligibility(item, source))

    # --- Discounts ---
    discounts: list = []
    if "discounts" in raw and raw["discounts"]:
        for item in raw["discounts"]:
            if not isinstance(item, dict):
                raise ParseError(f"Discount in {source} must be a mapping")
            discounts.append(_parse_conditional_amount(item, source))

    # --- Surcharges ---
    surcharges: list = []
    if "surcharges" in raw and raw["surcharges"]:
        for item in raw["surcharges"]:
            if not isinstance(item, dict):
                raise ParseError(f"Surcharges in {source} must be a mapping")
            surcharges.append(_parse_conditional_amount(item, source))

    # --- Base rates ---
    base_rates: dict[str, Decimal] = {}
    if "base_rates" in raw and raw["base_rates"]:
        for key, val in raw["base_rates"].items():
            base_rates[key] = _to_decimal(val)

    # --- Coverages ---
    coverages: dict[str, CoverageDef] = {}
    if "coverages" in raw and raw["coverages"]:
        for name, cdef in raw["coverages"].items():
            if not isinstance(cdef, dict):
                raise ParseError(f"Coverage '{name}' in {source} must be a mapping")
            coverages[name] = _parse_coverage(cdef, name, source)

    # --- Calculation order ---
    calculation_order = None
    if "calculation_order" in raw and raw["calculation_order"]:
        co = raw["calculation_order"]
        if isinstance(co, dict) and "steps" in co:
            steps = []
            for s in co["steps"]:
                if isinstance(s, dict) and "step" in s:
                    steps.append({"step": s["step"]})
                elif isinstance(s, str):
                    steps.append({"step": s})
            calculation_order = {"steps": steps}

    # --- Output ---
    output = None
    if "output" in raw and raw["output"]:
        output = _parse_output(raw["output"], source)

    # --- Build the product ---
    product = RatingProduct(
        version=str(raw["version"]),
        product=str(raw["product"]),
        jurisdiction=str(raw["jurisdiction"]),
        variables=variables,
        eligibility=eligibility,
        discounts=discounts,  # type: ignore[arg-type]
        surcharges=surcharges,  # type: ignore[arg-type]
        base_rates=base_rates,
        coverages=coverages,
        calculation_order=calculation_order,  # type: ignore[arg-type]
        output=output,
    )

    return product


# ---------------------------------------------------------------------------
# Individual field parsers
# ---------------------------------------------------------------------------

def _parse_variable(raw: dict, name: str, source: str) -> VariableDef:
    """Parse a single variable definition."""
    type_str = str(raw.get("type", "integer")).lower()
    type_map = {
        "integer": "integer",
        "int": "integer",
        "decimal": "decimal",
        "float": "decimal",
        "string": "string",
        "str": "string",
        "boolean": "boolean",
        "bool": "boolean",
    }
    numeric_type = type_map.get(type_str, type_str)
    from rating_dsl.models import NumericType
    try:
        nt = NumericType(numeric_type)
    except ValueError:
        raise ParseError(f"Unknown variable type '{numeric_type}' for '{name}' in {source}")

    return VariableDef(
        name=name,
        type=numeric_type,
        description=str(raw.get("description", "")),
        enum=raw.get("enum"),
        default=raw.get("default"),
        min=raw.get("min"),
        max=raw.get("max"),
    )


def _parse_eligibility(raw: dict, source: str) -> EligibilityRule:
    """Parse a single eligibility rule."""
    return EligibilityRule(
        name=str(raw.get("name", "")),
        rule=str(raw["rule"]),
        fail=str(raw["fail"]),
        priority=int(raw.get("priority", 0)),
    )


def _parse_conditional_amount(raw: dict, source: str):
    """Parse a discount or surcharge entry. Returns the raw dict
    with type coercion applied; the evaluator handles the rest."""
    return {
        "name": str(raw["name"]),
        "type": str(raw.get("type", "percentage")),
        "value": _to_decimal(raw.get("value", 0)),
        "condition": str(raw.get("condition", "True")),
        "description": str(raw.get("description", "")),
        "priority": int(raw.get("priority", 0)),
    }


def _parse_coverage(raw: dict, name: str, source: str) -> CoverageDef:
    """Parse a single coverage definition."""
    base_raw = raw.get("base_amount", {})
    if not isinstance(base_raw, dict):
        raise ParseError(f"Coverage '{name}' base_amount must be a mapping")

    base_amount = CoverageDef(
        name=name,
        label=str(raw.get("label", name)),
        base_amount=BaseAmount(
            type=str(base_raw["type"]),
            value=_to_decimal(base_raw.get("value")) if "value" in base_raw else None,
            source=base_raw.get("source"),
            formula=base_raw.get("formula"),
        ),
        multiplier=None,
        min_premium=_to_decimal(raw.get("min_premium")) if "min_premium" in raw else None,
        max_premium=_to_decimal(raw.get("max_premium")) if "max_premium" in raw else None,
    )

    # Parse optional multiplier
    mult_raw = raw.get("multiplier")
    if mult_raw and isinstance(mult_raw, dict):
        base_amount.multiplier = ConditionalMultiplier(
            type=str(mult_raw.get("type", "multiplier")),
            value=_to_decimal(mult_raw.get("value", 1)),
            condition=str(mult_raw.get("condition")) if "condition" in mult_raw else None,
        )

    return base_amount


def _parse_output(raw: dict, source: str) -> OutputConfig:
    """Parse output configuration."""
    currency = raw.get("currency", "USD")
    try:
        currency_enum = OutputCurrency(currency)
    except ValueError:
        raise ParseError(f"Invalid currency '{currency}' in {source}")

    round_mode = raw.get("round", "half_up")
    try:
        round_enum = RoundMode(round_mode)
    except ValueError:
        raise ParseError(f"Invalid round mode '{round_mode}' in {source}")

    return OutputConfig(
        currency=currency_enum,
        precision=int(raw.get("precision", 2)),
        round=round_enum,
    )


# ---------------------------------------------------------------------------
# Type coercion helpers
# ---------------------------------------------------------------------------

def _to_decimal(value: Any) -> Decimal | None:
    """Convert a value to Decimal, returning None for None/empty."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:
        return None
