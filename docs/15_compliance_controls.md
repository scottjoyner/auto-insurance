# Compliance Controls

## Purpose

This document defines implementation-level compliance controls that each service should respect.

## Control Families

```text
product_governance
quote_reproducibility
risk_appetite
policy_authority
claims_authority
ai_governance
treasury_governance
blockchain_privacy
auditability
security_access
```

## Product Governance Controls

- Product configuration must include product version.
- Rating configuration must include rating version.
- Jurisdiction must be explicit.
- Bind must be blocked if product is not allowed for bind.
- Product approval status must be checked before quote and bind.

## Quote Reproducibility Controls

- Quote input snapshot must be stored.
- Rating factors must be stored.
- Quote result must include reason codes.
- Quote result must include expiration.
- Quote result must be replayable.

## Risk Appetite Controls

- Every risk appetite decision must include policy version.
- Non-accept decisions must include reason codes.
- Concentration limits must be checked.
- Capital and reserve impact stubs must exist in MVP.
- Manual overrides require reason codes.

## Policy Authority Controls

- Bind requires accepted quote.
- Bind requires unexpired quote.
- Bind requires risk appetite approval or review completion.
- Bind requires payment or billing readiness.
- Bind must emit audit event.

## Claims Authority Controls

- Claim must reference policy version.
- Coverage check must run before payout.
- Evidence metadata must be retained.
- Claim denial requires review.
- Claim payout above threshold requires approval.

## AI Governance Controls

- AI model must be listed in model inventory.
- AI prompt must be versioned.
- AI tool calls must be logged.
- AI cannot bypass tool permissions.
- AI cannot invent coverage.
- AI cannot modify rating logic.
- AI cannot execute treasury actions.

## Treasury Governance Controls

- Treasury proposal must be evaluated against policy.
- Disallowed assets must be blocked.
- Counterparty limits must be enforced.
- Liquidity limits must be enforced.
- Real execution must remain disabled in MVP.

## Blockchain Privacy Controls

- PII must not be included in chain payloads.
- Policy documents must remain off-chain.
- Claim evidence must remain off-chain.
- On-chain values should be hashes, commitments, and attestations.
- Chain writes must be reconciled.

## Auditability Controls

- Every material decision must emit an event.
- Every workflow should have a correlation ID.
- Every human review should be logged.
- Every AI tool call should be logged.
- Every chain transaction should reference an off-chain source record.

## Security Access Controls

- Use RBAC and ABAC.
- Enforce least privilege.
- Require signer controls for chain transactions.
- Require approval workflows for restricted actions.
- Log access to sensitive documents.
