# Event Schemas Package

## Purpose

Canonical event type definitions shared across all services. Events are the immutable audit trail of the insurance operating system.

## File Structure

```
packages/event-schemas/
  README.md
  pyproject.toml
  src/
    event_schemas/
      __init__.py
      base.py                 # DomainEvent base class
      customer_events.py       # LeadCreated, ConsentCaptured, etc.
      quote_events.py          # QuoteGenerated, QuoteAccepted, etc.
      risk_events.py           # RiskAppetiteEvaluated, etc.
      policy_events.py         # PolicyBound, PolicyEndorsed, etc.
      claim_events.py          # ClaimFNOLReceived, ClaimApproved, etc.
      blockchain_events.py     # PolicyCommitted, PremiumCommitted, etc.
      treasury_events.py       # PremiumAllocated, ReserveSnapshot, etc.
  tests/
    test_event_validation.py
    test_event_serialization.py
```

## Core Event Types

### Customer Events

```python
# LeadCreated
@dataclass
class LeadCreatedEvent:
    event_id: str
    event_type: str = "LeadCreated"
    aggregate_type: str = "Lead"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "lead_source": "",
        "lead_type": "",
        "applicant_data": {},
        "schema_version": "1.0.0"
    })

# ConsentCaptured
@dataclass
class ConsentCapturedEvent:
    event_id: str
    event_type: str = "ConsentCaptured"
    aggregate_type: "Consent"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "consent_type": "",
        "consent_scope": "",
        "consent_expires_at": None,
        "schema_version": "1.0.0"
    })

# CustomerCreated
@dataclass
class CustomerCreatedEvent:
    event_id: str
    event_type: str = "CustomerCreated"
    aggregate_type: "Customer"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "customer_id": "",
        "party_id": "",
        "schema_version": "1.0.0"
    })
```

### Quote Events

```python
@dataclass
class QuoteGeneratedEvent:
    event_id: str
    event_type: str = "QuoteGenerated"
    aggregate_type: "Quote"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "quote_id": "",
        "product_id": "",
        "product_version": "",
        "jurisdiction": "",
        "premium": 0.0,
        "bind_eligible": False,
        "reason_codes": [],
        "expires_at": None,
        "input_snapshot_hash": "",
        "rating_factors": {},
        "schema_version": "1.0.0"
    })

@dataclass
class QuoteAcceptedEvent:
    event_id: str
    event_type: str = "QuoteAccepted"
    aggregate_type: "Quote"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "quote_id": "",
        "accepted_by": "",
        "schema_version": "1.0.0"
    })

@dataclass
class QuoteExpiredEvent:
    event_id: str
    event_type: str = "QuoteExpired"
    aggregate_type: "Quote"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "quote_id": "",
        "expired_at": None,
        "schema_version": "1.0.0"
    })
```

### Risk Events

```python
@dataclass
class RiskAppetiteEvaluatedEvent:
    event_id: str
    event_type: str = "RiskAppetiteEvaluated"
    aggregate_type: "RiskAssessment"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "quote_id": "",
        "decision": "",
        "reason_codes": [],
        "required_approvals": [],
        "capital_impact_estimate": None,
        "reserve_impact_estimate": None,
        "schema_version": "1.0.0"
    })
```

### Policy Events

```python
@dataclass
class PolicyBoundEvent:
    event_id: str
    event_type: str = "PolicyBound"
    aggregate_type: "Policy"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "policy_id": "",
        "policy_version": "",
        "quote_id": "",
        "product_id": "",
        "product_version": "",
        "premium": 0.0,
        "effective_date": None,
        "expiration_date": None,
        "bind_approved_by": "",
        "blockchain_commitment_hash": None,
        "schema_version": "1.0.0"
    })

@dataclass
class PolicyEndorsedEvent:
    event_id: str
    event_type: str = "PolicyEndorsed"
    aggregate_type: "Policy"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "policy_id": "",
        "policy_version": "",
        "endorsement_type": "",
        "premium_adjustment": 0.0,
        "effective_date": None,
        "schema_version": "1.0.0"
    })

@dataclass
class PolicyCancelledEvent:
    event_id: str
    event_type: str = "PolicyCancelled"
    aggregate_type: "Policy"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "policy_id": "",
        "policy_version": "",
        "cancellation_type": "",
        "effective_date": None,
        "refund_amount": 0.0,
        "schema_version": "1.0.0"
    })
```

### Claim Events

```python
@dataclass
class ClaimFNOLReceivedEvent:
    event_id: str
    event_type: str = "ClaimFNOLReceived"
    aggregate_type: "Claim"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "claim_id": "",
        "policy_id": "",
        "policy_version": "",
        "claim_type": "",
        "loss_date": None,
        "estimated_loss_amount": None,
        "schema_version": "1.0.0"
    })

@dataclass
class ClaimApprovedEvent:
    event_id: str
    event_type: str = "ClaimApproved"
    aggregate_type: "Claim"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "claim_id": "",
        "decision": "",
        "reserve_amount": 0.0,
        "payout_amount": 0.0,
        "decision_reason_codes": [],
        "approved_by": "",
        "schema_version": "1.0.0"
    })

@dataclass
class ClaimDeniedEvent:
    event_id: str
    event_type: str = "ClaimDenied"
    aggregate_type: "Claim"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "claim_id": "",
        "decision_reason_codes": [],
        "denied_by": "",
        "schema_version": "1.0.0"
    })
```

### Blockchain Events

```python
@dataclass
class PolicyCommittedEvent:
    event_id: str
    event_type: str = "PolicyCommitted"
    aggregate_type: "BlockchainPolicy"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "policy_id": "",
        "commitment_hash": "",
        "contract_address": "",
        "transaction_hash": "",
        "status": "",
        "schema_version": "1.0.0"
    })

@dataclass
class PremiumCommittedEvent:
    event_id: str
    event_type: str = "PremiumCommitted"
    aggregate_type: "BlockchainPremium"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "policy_id": "",
        "payment_reference": "",
        "amount": 0.0,
        "asset_type": "",
        "commitment_hash": "",
        "contract_address": "",
        "transaction_hash": "",
        "schema_version": "1.0.0"
    })
```

### Treasury Events

```python
@dataclass
class PremiumAllocatedEvent:
    event_id: str
    event_type: str = "PremiumAllocated"
    aggregate_type: "PremiumAllocation"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "policy_id": "",
        "payment_reference": "",
        "total_amount": 0.0,
        "buckets": {},
        "liquidity_impact": None,
        "schema_version": "1.0.0"
    })

@dataclass
class ReserveSnapshotEvent:
    event_id: str
    event_type: str = "ReserveSnapshot"
    aggregate_type: "ReserveSnapshot"
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict = field(default_factory=lambda: {
        "snapshot_hash": "",
        "methodology_hash": "",
        "total_reserve": 0.0,
        "buckets": {},
        "attested_by": "",
        "schema_version": "1.0.0"
    })
```
