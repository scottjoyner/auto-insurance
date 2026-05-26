# Testing Strategy

## Purpose

Testing must prove the system is deterministic, auditable, permissioned, and safe before adding high-authority AI, real-money treasury execution, or production blockchain deployments.

## Test Categories

```text
unit
integration
e2e
contract
security
compliance
model-eval
load
reconciliation
```

## Unit Tests

Required coverage:

- rating factor calculations
- quote eligibility rules
- quote expiration rules
- risk appetite decisions
- policy lifecycle transitions
- claim lifecycle transitions
- premium allocation math
- reserve snapshot hashing
- treasury policy evaluation
- event schema validation

## Integration Tests

Required flows:

```text
quote request -> quote generated
quote generated -> risk appetite evaluated
quote accepted -> policy bound
policy bound -> policy committed on-chain
premium received -> premium allocated
reserve snapshot -> reserve attested
claim submitted -> coverage checked
claim approved -> payout commitment recorded
```

## End-to-End Tests

The first E2E test should prove:

```text
customer intake
  -> quote
  -> risk appetite
  -> accept
  -> bind
  -> policy document hash
  -> chain commitment
  -> audit packet
```

## Contract Tests

Smart contract tests must cover:

- role access control
- policy registration
- policy status updates
- premium commitment recording
- claim commitment recording
- reserve attestation
- emergency pause
- signer rotation
- duplicate transaction handling

## Security Tests

Security tests must prove:

- no PII is placed in chain payloads
- AI agents cannot bypass tool permissions
- unauthorized users cannot bind policies
- unauthorized users cannot approve payouts
- unauthorized users cannot execute treasury proposals
- smart contract admin functions require approved signers
- secret values are not committed to the repo

## Compliance Tests

Compliance tests must prove:

- every quote references product and rating version
- every non-accept risk result has reason codes
- every bind has authority metadata
- every claim decision references policy version and evidence metadata
- every treasury proposal references policy checks
- every AI decision has model and tool traceability

## Model Evaluation Tests

AI model tests should check:

- product explanation accuracy
- quote explanation accuracy
- refusal to invent coverage
- human handoff for restricted actions
- resistance to prompt injection
- no alteration of rating logic
- no unauthorized treasury or claims action

## Reconciliation Tests

Reconciliation tests should compare:

- policy table to PolicyRegistry contract
- payment records to premium commitments
- claim records to claim commitments
- reserve snapshots to reserve attestations
- outbox rows to chain receipts

## Acceptance Criteria Before Production-Like Testing

- deterministic quote replay passes
- risk appetite policy tests pass
- policy lifecycle tests pass
- contract access control tests pass
- AI tool permission tests pass
- no PII-on-chain tests pass
- audit packet generation passes
