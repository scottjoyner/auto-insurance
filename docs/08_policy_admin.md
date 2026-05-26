# Policy Administration

## Purpose

The policy administration system manages the lifecycle of policies after quote acceptance. It is responsible for binding, issuing, endorsing, renewing, cancelling, reinstating, and verifying coverage.

## Policy Lifecycle

```text
DRAFT_QUOTE
QUOTED
ACCEPTED
BIND_REQUESTED
BOUND
ISSUED
ACTIVE
ENDORSED
RENEWAL_PENDING
RENEWED
CANCEL_PENDING
CANCELLED
EXPIRED
REINSTATED
CLAIM_LOCKED
```

## Responsibilities

- Validate accepted quote.
- Validate bind authority.
- Confirm required payment or billing setup.
- Generate policy version.
- Generate policy documents.
- Hash policy document package.
- Emit policy lifecycle events.
- Trigger blockchain policy commitment.
- Support endorsements.
- Support renewals.
- Support cancellations and reinstatements.

## Initial Endpoints

```http
POST /policies/bind
GET /policies/{policy_id}
POST /policies/{policy_id}/endorsements
POST /policies/{policy_id}/cancel
POST /policies/{policy_id}/renew
POST /policies/{policy_id}/reinstate
POST /policies/{policy_id}/sync-chain
```

## Bind Preconditions

A policy may only bind if:

- quote exists
- quote is accepted
- quote is not expired
- product is allowed for bind
- jurisdiction is allowed
- risk appetite decision permits bind
- required human reviews are complete
- payment or billing requirements are satisfied
- policy documents can be generated

## Policy Versioning

Every policy change should create or reference a policy version.

Versioned items:

- coverage limits
- deductibles
- endorsements
- exclusions
- effective date
- expiration date
- insured assets
- parties
- documents
- policy hash

## Blockchain Commitments

Policy service should not write to the chain directly. It should emit an event or write an outbox record that the blockchain gateway consumes.

```text
PolicyBound
  -> policy document package hashed
  -> PolicyCommitmentRequested
  -> blockchain gateway submits transaction
  -> PolicyCommittedOnChain
```

## MVP Acceptance Criteria

- Accepted quote can bind.
- Policy ID and policy version are created.
- Policy lifecycle event is emitted.
- Policy document package hash is generated.
- Chain commitment request is created.
- Audit packet can be generated.
