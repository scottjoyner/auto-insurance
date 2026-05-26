# Compliance Framework

## Purpose

This file defines the compliance posture for the architecture phase. It is not legal advice. It exists to ensure implementation work does not accidentally create an ungoverned AI insurer, unapproved rating engine, or uncontrolled treasury system.

## Compliance Principles

1. Product, rate, form, and jurisdiction metadata must be versioned.
2. Every quote must be reproducible from a stored input snapshot.
3. Every bind decision must reference risk appetite and authority checks.
4. Every adverse or referral decision must have reason codes.
5. Every AI action must be traceable to model version, prompt version, retrieved context, and tool calls.
6. Every claim decision must reference policy version, coverage check, evidence, and approval authority.
7. Every treasury action must reference reserve status, liquidity policy, investment policy, approval, and execution evidence.
8. Every on-chain commitment must reconcile back to an off-chain source record.

## Required Compliance Domains

| Domain | Controls |
| --- | --- |
| Product governance | Product versioning, rate/form metadata, jurisdiction controls |
| AI governance | Model inventory, prompt registry, test results, human review rules |
| Underwriting | Reason codes, referral rules, manual override logging |
| Claims | Coverage verification, evidence retention, approval authority |
| Treasury | Investment policy, reserve segregation, approval workflow |
| Blockchain | PII exclusion, transaction audit, signer controls, reconciliation |
| Customer communications | Consent, disclosures, service records, complaint tracking |
| Audit | Immutable event log, export packets, chain/off-chain reconciliation |

## Compliance Artifacts

The repo should maintain:

```text
governance/ai_model_inventory.yml
governance/human_review_thresholds.yml
governance/product_approval_matrix.yml
governance/adverse_action_reason_codes.yml
governance/risk_appetite_policy.yml
governance/treasury_policy.yml
```

## Human Review Triggers

Human review should be required for:

- AI-generated adverse decisions.
- Quote declines.
- Risk appetite exceptions.
- Manual rating overrides.
- High-limit policy binds.
- Claim denials.
- High-value claim payouts.
- Suspected fraud cases.
- Treasury proposals above threshold.
- Product or rate changes.
- Smart contract upgrades.

## Audit Packet Requirements

Each major workflow should produce an audit packet.

### Quote audit packet

- applicant input snapshot
- product/rate/form version
- rating factors
- risk appetite result
- AI session references
- reason codes
- human review result, if applicable

### Policy audit packet

- accepted quote reference
- bind authority
- payment confirmation
- policy document hash
- policy lifecycle history
- blockchain transaction reference

### Claim audit packet

- FNOL record
- policy version
- coverage verification
- evidence metadata
- reserve changes
- decision reason codes
- approvals
- payout transaction reference

### Treasury audit packet

- reserve snapshot
- liquidity position
- policy evaluation result
- proposal
- approvals
- execution record
- on-chain attestation reference
