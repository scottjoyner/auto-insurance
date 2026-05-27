# Rating DSL — Deterministic YAML-Based Insurance Rating Engine

A configurable, deterministic rating system for insurance products. Products
are defined as YAML files that declare variables, eligibility rules, discounts,
surcharges, coverages, and the calculation pipeline — all evaluated with a
safe expression engine.

## Quick Start

```python
from rating_dsl import load_product, validate_product, evaluate

# 1. Load the product config
product = load_product("sample_personal_auto_v1.yml")

# 2. Validate (catches config errors)
errors = validate_product(product)
if errors:
    for e in errors:
        print(f"ERROR: {e}")

# 3. Rate a quote
result = evaluate(product, {
    "age": 35,
    "vehicle_year": 2023,
    "coverage_type": "standard",
    "vehicle_value": 25000,
    "driving_years": 15,
    "claims_3yr": 0,
    "credit_tier": "a",
})

print(f"Total premium: ${result.total_premium}")
print(f"Coverages: {result.coverage_dict}")
```

## Product Configuration Reference

### Top-Level Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `version` | Yes | string | DSL schema version (currently `1.0`) |
| `product` | Yes | string | Product identifier (e.g., `sample_personal_auto_v1`) |
| `jurisdiction` | Yes | string | Jurisdiction code (e.g., `SAMPLE`) |
| `variables` | No | mapping | Input variable definitions |
| `eligibility` | No | list | Eligibility gate rules |
| `discounts` | No | list | Conditional discounts |
| `surcharges` | No | list | Conditional surcharges |
| `base_rates` | No | mapping | Base rate by coverage type |
| `coverages` | No | mapping | Coverage line item definitions |
| `calculation_order` | No | object | Explicit pipeline step ordering |
| `output` | No | object | Output formatting settings |

### Variables

Input variables that the product accepts from the quote context.

```yaml
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
  driving_years:
    type: integer
    description: Years of licensed driving experience
  claims_3yr:
    type: integer
    description: Number of claims in last 3 years
  credit_tier:
    type: string
    enum: [a, b, c, d, e]
    description: Credit-based insurance tier
```

Supported types: `integer`, `decimal`, `string`, `boolean`

### Eligibility Rules

Boolean gates that must all pass for a quote to proceed. If any fails, the
quote is rejected with the failure message.

```yaml
eligibility:
  - name: minimum_age
    rule: age >= 16
    fail: "Applicant must be at least 16 years old"
    priority: 1
  - name: driving_experience
    rule: driving_years >= 1
    fail: "Must have at least 1 year of licensed driving experience"
    priority: 2
  - name: claims_limit
    rule: claims_3yr <= 3
    fail: "Maximum 3 claims in the past 3 years"
    priority: 3
```

### Discounts

Conditional premium reductions, applied in priority order.

```yaml
discounts:
  - name: new_vehicle
    type: percentage
    value: 5.0
    condition: vehicle_year >= 2023
    description: "5% off for newer vehicles"
    priority: 1
  - name: good_driver
    type: percentage
    value: 10.0
    condition: claims_3yr == 0
    description: "10% off for clean driving history"
    priority: 2
  - name: experienced_driver
    type: percentage
    value: 3.0
    condition: driving_years >= 10
    description: "3% off for 10+ years experience"
    priority: 3
```

Supported types: `percentage` (of current premium), `flat` (fixed dollar amount)

### Surcharges

Conditional premium additions, applied in priority order (before discounts).

```yaml
surcharges:
  - name: young_driver
    type: percentage
    value: 25.0
    condition: age < 25
    description: "25% surcharge for drivers under 25"
    priority: 1
  - name: claims_surge
    type: percentage
    value: 15.0
    condition: claims_3yr >= 2
    description: "15% surcharge for 2+ claims"
    priority: 2
```

### Base Rates

Base premium by coverage type. Used when a coverage's `base_amount.type` is
`variable` and references a key in this mapping.

```yaml
base_rates:
  basic: 85.00
  standard: 120.00
  premium: 175.00
```

### Coverages

Individual coverage line items with their own base calculation logic.

```yaml
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
      type: formula
      formula: "vehicle_value * 0.005"
    multiplier:
      type: percentage
      value: 65.0
  uninsured_motorist:
    label: "Uninsured Motorist"
    base_amount:
      type: fixed
      value: 25.00
```

### Calculation Order

Explicit ordering of pipeline steps. If omitted, the default order is used:

1. `apply_eligibility`
2. `calculate_base`
3. `apply_surcharges`
4. `apply_discounts`
5. `calculate_coverages`
6. `apply_coverage_multipliers`
7. `enforce_min_max`
8. `compute_total`

```yaml
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
```

### Output Configuration

```yaml
output:
  currency: USD
  precision: 2
  round: half_up
```

Supported round modes: `half_up`, `half_down`, `ceiling`, `floor`

## Expression Language

### Boolean Expressions (eligibility, conditions)

```
age >= 16
claims_3yr <= 3
vehicle_year >= 2023 and credit_tier != 'e'
age < 25 or claims_3yr >= 2
```

Supported operators: `>=`, `<=`, `>`, `<`, `==`, `!=`, `and`, `or`, `not`

### Numeric Formulas (base_amount.type=formula)

```
vehicle_value * 0.008
vehicle_value * 0.005 + 25
max(vehicle_value * 0.01, 100)
round(vehicle_value * 0.008, 0)
```

Supported operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`, unary `-`

Supported functions: `abs()`, `min()`, `max()`, `round()`, `int()`, `float()`, `pow()`

Math module access: `math.sqrt()`, `math.ceil()`, `math.floor()`, etc.

## RatingResult

```python
@dataclass
class RatingResult:
    product: str
    jurisdiction: str
    total_premium: Decimal
    coverages: list[CoverageResult]
    eligibility_passed: bool
    failed_rules: list[str]
    surcharges_applied: list[str]
    discounts_applied: list[str]
    raw_context: dict[str, Any]

    @property
    def coverage_dict(self) -> dict[str, Decimal]:
        """{name: premium} mapping"""

    @property
    def is_valid(self) -> bool:
        """True if eligibility passed"""

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON/API responses"""
```

## Directory Structure

```
packages/rating-dsl/
├── README.md                    # This file
├── schema/
│   └── rating-dsl-schema.json  # JSON Schema for config validation
├── rating_dsl/
│   ├── __init__.py              # Public API
│   ├── models.py                # Pydantic data models
│   ├── parser.py                # YAML loading & type coercion
│   ├── validator.py             # Schema & business rule validation
│   ├── evaluator.py             # Safe expression engine
│   └── engine.py                # Full rating pipeline
└── data/
    └── sample-products/
        └── sample_personal_auto_v1.yml
```

## Design Decisions

1. **Deterministic, not ML-based** — All rating logic is explicit in YAML.
   No hidden weights or training data. Fully auditable.

2. **Safe expression evaluation** — Uses Python's `ast` module with a
   restricted namespace. No `eval()`, no arbitrary code execution.

3. **Decimal arithmetic** — All monetary values use Python's `Decimal` type
   to avoid floating-point precision issues.

4. **Fail-fast eligibility** — Eligibility checks run first. If any rule
   fails, the quote is rejected immediately with a clear error message.

5. **Priority-ordered discounts/surcharges** — Each is sorted by priority
   (lower first) before application. Multiple discounts/surcharges can
   match for a single quote.

6. **Extensible pipeline** — Steps are explicitly ordered and can be
   customized. New steps can be added by extending the pipeline.
