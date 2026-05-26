# Event Model

## Purpose

The event model provides immutable, auditable state transitions across insurance workflows. Events connect service boundaries, drive workflows, produce audit packets, and reconcile blockchain commitments.

## Event Envelope

```json
{
  "event_id": "evt_01HX",
  "event_type": "QuoteGenerated",
  "aggregate_type": "Quote",
  "aggregate_id": "quote_123",
  "occurred_at": "2026-05-26T14:00:00Z",
  "actor": {
    "actor_type": "AI_AGENT",
    "actor_id": "agent_quote_v1"
  },
  "correlation_id": "corr_abc",
  "causation_id": "evt_prev",
  "payload": {},
  "schema_version": "1.0.0"
}
```

## Required Envelope Fields

| Field | Purpose |
| --- | --- |
| event_id | Globally unique event ID |
| event_type | Specific event name |
| aggregate_type | Business object type |
| aggregate_id | Business object ID |
| occurred_at | Timestamp |
| actor | User, system, AI agent, service, or signer |
| correlation_id | Request or workflow correlation |
| causation_id | Previous event that caused this event |
| payload | Event-specific data |
| schema_version | Event schema version |

## Core Event Groups

### Customer and CRM

```text
LeadCreated
ConsentCaptured
CustomerCreated
CommunicationPreferenceUpdated
CampaignTouchpointRecorded
ServiceCaseCreated
HumanHandoffRequested
```

### Quote

```text
QuoteRequested
QuoteInputSnapshotCreated
QuoteGenerated
QuoteRecalculated
QuoteReferred
QuoteAccepted
QuoteExpired
QuoteWithdrawn
```

### Risk Appetite

```text
RiskAssessmentRequested
RiskAssessmentCompleted
RiskReferredToUnderwriter
RiskDeclined
RiskAcceptedWithLimits
RiskAppetitePolicyChanged
```

### Policy

```text
PolicyBindRequested
PolicyBound
PolicyIssued
PolicyEndorsed
PolicyRenewed
PolicyCancellationRequested
PolicyCancelled
PolicyReinstated
PolicyExpired
PolicyCommittedOnChain
```

### Premium and Treasury

```text
PremiumReceived
PremiumAllocated
ReserveSnapshotCreated
ReserveSnapshotAttestedOnChain
TreasuryProposalCreated
TreasuryProposalApproved
TreasuryProposalRejected
TreasuryExecutionRecorded
TreasuryPolicyViolationDetected
```

### Claims

```text
ClaimSubmitted
ClaimEvidenceAdded
ClaimCoverageCheckCompleted
ClaimReserveSet
ClaimReviewRequested
ClaimApproved
ClaimDenied
ClaimPayoutApproved
ClaimPaid
ClaimClosed
ClaimReopened
ClaimCommittedOnChain
```

### AI and Compliance

```text
AIInteractionLogged
AIToolCallExecuted
AIHumanReviewTriggered
ComplianceReviewCreated
ComplianceReviewCompleted
DecisionReasonRecorded
AuditPacketGenerated
```

### Blockchain

```text
ChainTransactionRequested
ChainTransactionSubmitted
ChainTransactionConfirmed
ChainTransactionFailed
ChainReconciliationCompleted
ChainReconciliationMismatchDetected
```

## Event Storage

The MVP can start with a PostgreSQL event table and outbox table. Later versions can add Kafka, Redpanda, NATS, or another event bus.

## Outbox Pattern

```text
service transaction
  -> domain record written
  -> outbox event written in same DB transaction
  -> worker processes event
  -> event status marked complete
```

## Idempotency

Consumers must handle duplicate events using event ID deduplication, aggregate version checks, idempotency keys, transaction receipt references, and replay-safe handlers.

## Audit Requirements

Every material insurance decision should be reconstructable from events. Event payloads should avoid raw PII when possible and reference secured records by ID.
