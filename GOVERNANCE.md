# Governance

## Purpose

Governance defines how the insurance platform changes over time. This includes AI model changes, rating logic changes, product approvals, treasury rules, smart contract administration, and human review thresholds.

## Governance Areas

| Area | Required Control |
| --- | --- |
| Product governance | Product/rate/form versioning and approval metadata |
| AI governance | Model inventory, evals, prompt registry, tool permissions |
| Risk appetite | Policy versioning, exposure limits, override approvals |
| Treasury | Asset limits, counterparty limits, liquidity rules, approvals |
| Smart contracts | Multisig, timelocks, emergency pause, upgrade logs |
| Claims | Approval authority, denial controls, reserve reviews |
| Security | Role reviews, key rotation, incident response |
| Compliance | Audit packets, complaint review, regulatory export |

## Decision Records

Major architecture and governance decisions should be tracked using ADRs under:

```text
docs/decisions/
```

Initial decisions to capture:

1. Blockchain-first but not blockchain-only architecture.
2. No sensitive insurance data on-chain.
3. Deterministic rating before AI decision authority.
4. Human review for adverse decisions and high-risk actions.
5. Local-chain development before production network selection.
6. Treasury simulation before real-money float execution.

## Change Management

Every regulated or high-impact change must include:

- change description
- affected services
- affected product/rate/form versions
- approval owner
- test evidence
- rollback plan
- audit log reference

## Approval Groups

```text
Product Approval Committee
AI Governance Committee
Underwriting Authority Committee
Claims Authority Committee
Treasury and Investment Committee
Security and Smart Contract Committee
Compliance Review Committee
```

## Governance Files

- `governance/ai_model_inventory.yml`
- `governance/human_review_thresholds.yml`
- `governance/product_approval_matrix.yml`
- `governance/adverse_action_reason_codes.yml`
- `governance/risk_appetite_policy.yml`
- `governance/treasury_policy.yml`

## Implementation Requirement

No service should hard-code governance thresholds. Thresholds should be loaded from versioned policy configuration and included in audit logs.