# Risk Appetite Engine

## Purpose

The risk appetite engine decides whether the company should accept, refer, limit, reinsure, decline, or request more information for a risk.

It is not a pricing engine. It is the portfolio and capital control layer that sits beside the quote engine.

## Inputs

```text
applicant profile
product ID
jurisdiction
coverage limits
deductibles
risk factors
quote premium
loss history
geographic exposure
portfolio concentration
reserve impact
capital impact
liquidity impact
reinsurance availability
fraud indicators
manual underwriting flags
```

## Outputs

```text
decision
reason codes
capital impact
reserve impact
portfolio concentration impact
reinsurance recommendation
human review requirement
audit trace
```

## Decisions

```text
ACCEPT
ACCEPT_WITH_LIMITS
ACCEPT_WITH_REINSURANCE
REFER_TO_UNDERWRITER
DECLINE
REQUEST_MORE_INFO
WAITLIST
```

## Evaluation Dimensions

| Dimension | Examples |
| --- | --- |
| Product | Auto, renters, cyber, travel, device protection |
| Jurisdiction | State, county, ZIP, regulatory approval status |
| Exposure | Limit, deductible, insured value, aggregate exposure |
| Customer risk | Loss history, payment behavior, fraud indicators |
| Portfolio risk | Concentration, correlated losses, accumulation |
| Capital | Required capital, solvency margin, reserve load |
| Liquidity | Expected claim timing, cash ladder, stress scenarios |
| Reinsurance | Treaty capacity, retention, counterparty limits |
| Operational | Claims complexity, legal complexity, servicing load |

## Policy-Driven Implementation

The service must load risk appetite from versioned policy config rather than hard-coding thresholds.

Policy file:

```text
governance/risk_appetite_policy.yml
```

## Example Response

```json
{
  "decision": "REFER_TO_UNDERWRITER",
  "reason_codes": [
    "ZIP_CONCENTRATION_LIMIT",
    "CAPITAL_USAGE_ABOVE_THRESHOLD"
  ],
  "capital_impact": {
    "required_capital_delta": 183.22,
    "reserve_delta": 91.11
  },
  "portfolio_impact": {
    "zip_exposure_after_bind": 0.084,
    "zip_limit": 0.075
  },
  "required_approvals": [
    "UNDERWRITER_LEVEL_2"
  ]
}
```

## MVP Rules

Initial MVP should support:

- max policy limit check
- max customer exposure check
- max geography exposure check
- blocked jurisdiction check
- referral threshold check
- reserve impact stub
- reinsurance availability stub
- reason code output

## Required Tests

- Decline blocked jurisdiction.
- Refer above max limit.
- Accept within all thresholds.
- Accept with limits when exposure can be reduced.
- Require underwriter review when concentration exceeds threshold.
- Ensure every non-ACCEPT decision has reason codes.
