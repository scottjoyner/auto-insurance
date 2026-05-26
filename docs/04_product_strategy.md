# Product Strategy

## Purpose

The product strategy defines the starting insurance product scope, why the MVP should remain constrained, and how products should be represented in the system.

## MVP Recommendation

The first implementation should use a sample product or low-complexity product so the architecture can prove quote, risk, policy, blockchain, audit, and treasury flows without immediately taking on full production regulatory complexity.

Recommended starting options:

1. Sample personal auto product for architecture only.
2. Parametric travel delay product.
3. Renters product.
4. Device protection product.
5. Personal cyber product.

## Product Configuration Requirements

Every product must define:

```text
product_id
product_name
product_version
jurisdiction
coverage_options
limits
deductibles
eligibility_rules
rating_variables
rate_version
form_version
approval_status
effective_date
expiration_date
owner
```

## Product Lifecycle

```text
DRAFT
ARCHITECTURE_SAMPLE_ONLY
INTERNAL_REVIEW
COMPLIANCE_REVIEW
APPROVED_FOR_TESTING
APPROVED_FOR_PRODUCTION
SUSPENDED
RETIRED
```

## Product Governance

Products must be listed in:

```text
governance/product_approval_matrix.yml
```

No product should be bindable unless:

- product is active
- jurisdiction is allowed
- rate version is approved for the environment
- form version is approved for the environment
- risk appetite allows the product
- human review rules are satisfied

## Product-to-System Flow

```text
Product config
  -> quote-service loads rating rules
  -> risk-appetite-service evaluates portfolio fit
  -> policy-service binds approved quote
  -> document-service generates package
  -> blockchain-gateway records commitment
```

## MVP Product Boundary

The initial product should not attempt to solve every real insurance complexity. The goal is to prove the operating platform.

MVP should include:

- one product
- one sample jurisdiction
- one rating plan
- one coverage package
- simple deductible options
- simple eligibility rules
- risk appetite gates
- quote-to-bind flow

MVP should exclude:

- multi-state rating
- real production filings
- advanced actuarial pricing
- multiple coverage forms
- producer commission complexity
- real claims automation at launch
