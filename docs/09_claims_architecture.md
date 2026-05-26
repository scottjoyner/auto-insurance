# Claims Architecture

## Purpose

The claims system manages first notice of loss, evidence, coverage verification, reserve setting, review, decisioning, payout approval, and claim closure.

## Claim Lifecycle

```text
FNOL_RECEIVED
EVIDENCE_PENDING
COVERAGE_REVIEW
FRAUD_REVIEW
ADJUSTER_REVIEW
RESERVE_SET
APPROVED
DENIED
PAYMENT_PENDING
PAID
CLOSED
REOPENED
```

## Responsibilities

- Create claim records.
- Collect FNOL.
- Link claim to policy version.
- Verify coverage.
- Manage evidence metadata.
- Hash evidence manifests.
- Run triage rules.
- Set and update reserves.
- Route to adjuster or manager review.
- Record decision reason codes.
- Trigger payout approval workflow.
- Record on-chain claim commitment.

## Initial Endpoints

```http
POST /claims
GET /claims/{claim_id}
POST /claims/{claim_id}/evidence
POST /claims/{claim_id}/coverage-check
POST /claims/{claim_id}/reserve
POST /claims/{claim_id}/decision
POST /claims/{claim_id}/payout
POST /claims/{claim_id}/close
POST /claims/{claim_id}/reopen
```

## Coverage Check

Coverage verification must reference:

- policy ID
- policy version
- loss date
- coverage terms
- exclusions
- deductible
- claim type
- jurisdiction

## Evidence Model

Evidence should be stored off-chain. The claims service should store metadata and hashes.

Evidence metadata:

```text
evidence_id
claim_id
file_reference
file_hash
evidence_type
uploaded_by
uploaded_at
retention_policy
access_control_policy
```

## Claim Payout Controls

Payouts require:

- active or applicable policy coverage
- claim decision approval
- reserve availability
- payout authority check
- human review if above threshold
- payment rail selection
- audit event
- optional chain commitment

## MVP Acceptance Criteria

- Claim can be submitted against a policy.
- Claim links to policy version.
- Evidence metadata can be attached.
- Coverage check produces a result.
- Reserve can be set.
- Claim decision can be recorded.
- Audit packet can be generated.
