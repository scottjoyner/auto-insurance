"""
Rating DSL — Deterministic YAML-based insurance rating engine.

Public API:
    load_product(path)    -> RatingProduct   # Load & parse a YAML product
    validate_product(prod) -> list[str]       # Validate a product config
    evaluate(product, ctx) -> RatingResult    # Run the rating engine

Usage:
    >>> from rating_dsl import load_product, validate_product, evaluate
    >>> product = load_product("sample_personal_auto_v1.yml")
    >>> errors = validate_product(product)
    >>> result = evaluate(product, {
    ...     "age": 35,
    ...     "vehicle_year": 2023,
    ...     "coverage_type": "standard",
    ...     "vehicle_value": 25000,
    ...     "driving_years": 15,
    ...     "claims_3yr": 0,
    ...     "credit_tier": "a",
    ... })
    >>> print(result.total_premium)
    108.42
"""

from rating_dsl.models import RatingProduct
from rating_dsl.parser import load_product, parse_product_dict
from rating_dsl.validator import validate_product, Validator
from rating_dsl.evaluator import Evaluator
from rating_dsl.engine import evaluate, RatingResult

__all__ = [
    "RatingProduct",
    "RatingResult",
    "Evaluator",
    "Validator",
    "load_product",
    "parse_product_dict",
    "validate_product",
    "evaluate",
]

__version__ = "0.1.0"
