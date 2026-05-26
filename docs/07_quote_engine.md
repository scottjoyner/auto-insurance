# Quote Engine

## Purpose

The quote engine generates deterministic, reproducible, explainable quotes from versioned product and rating configuration.

The AI agent may collect inputs and explain results, but the quote calculation itself should be deterministic and testable.

## Responsibilities

- Validate product eligibility.
- Load product configuration.
- Load jurisdiction-specific rating plan.
- Calculate premium.
- Apply discounts, fees, taxes, and surcharges.
- Produce coverage options.
- Produce explainability metadata.
- Emit quote events.
- Store quote input snapshots.

## Required Inputs

```text
applicant profile
product ID
jurisdiction
coverage selections
deductible selections
underwriting answers
rating variables
third-party data references
risk appetite result
quote effective date
```

## Required Outputs

```text
quote ID
product version
rating version
jurisdiction
premium
coverage terms
deductible
fees and taxes
reason codes
rating factors
bind eligibility
expiration date
input snapshot hash
explainability package
```

## Product Configuration

Product config should live under:

```text
data/sample-products/
packages/product-config/
```

Example shape:

```yaml
product_id: sample_personal_auto_v1
jurisdiction: NC
version: 2026.001
status: draft
base_rate: 500.00
variables:
  vehicle_age_band:
    type: categorical
    factor_table:
      new: 1.15
      mid: 1.00
      old: 0.95
  deductible:
    type: numeric
    factor_table:
      250: 1.20
      500: 1.00
      1000: 0.88
rules:
  - id: refer_high_limit
    when: coverage_limit > 100000
    action: refer
    reason_code: LIMIT_REQUIRES_UNDERWRITING
```

## Quote Lifecycle

```text
DRAFT
GENERATED
REFERRED
ACCEPTED
EXPIRED
BOUND
WITHDRAWN
```

## Determinism Requirements

A quote must be reproducible using:

- quote input snapshot
- product version
- rating version
- jurisdiction
- effective date
- factor tables
- rule versions
- external data references or cached values

## Explainability Requirements

Quote output should include:

- base rate
- applied factors
- discounts
- surcharges
- fees
- taxes
- referral flags
- decline flags
- reason codes

## MVP Acceptance Criteria

- Generate a quote for a sample product.
- Persist quote input snapshot.
- Return rating factor breakdown.
- Return bind eligibility.
- Replay quote calculation from snapshot.
- Emit `QuoteGenerated` event.
