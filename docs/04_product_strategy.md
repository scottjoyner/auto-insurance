# Product Strategy

## MVP Decision

**Product**: Sample personal auto insurance
**Status**: architecture_sample_only
**Jurisdiction**: SAMPLE (modeled on NC)
**Target**: Architecture prototype / MGA-style operating layer

## Why Sample Personal Auto

- Universal need with well-understood rating factors
- Clear regulatory framework to model
- Large addressable market for validation
- Standard coverage options (liability, collision, comprehensive)
- Well-documented NC auto insurance regulations
- Sample values are architecture test data, not real rates

## Product Lifecycle

```
DRAFT -> ARCHITECTURE_SAMPLE_ONLY -> INTERNAL_REVIEW
  -> COMPLIANCE_REVIEW -> APPROVED_FOR_TESTING
  -> APPROVED_FOR_PRODUCTION -> SUSPENDED or RETIRED
```

## Sample Product

- **ID**: sample_personal_auto_v1
- **Version**: 2026.001
- **Base rate**: $500/year (architecture test value)
- **Premium range**: $500-$2,500/year (architecture test values)
- **Coverages**: liability (required), collision (optional), comprehensive (optional)
- **Liability limits**: 25/50, 100/300, 250/500
- **Deductibles**: 250, 500, 1000, 2000
- **Rating variables**: vehicle_age_band, deductible_level, driver_age_band, zip_code_factor, driving_record

## Future Products (Phase 3+)

- Parametric travel delay
- Renters
- Device protection
- Personal cyber

Each future product requires:
- Product approval committee sign-off
- Regulatory filing (if applicable)
- Actuarial review
- Legal review
- Compliance review
- Blockchain architecture review
- AI governance review
- Treasury policy update
