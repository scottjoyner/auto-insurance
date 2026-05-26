# Low-Level Design

## Service Boundaries

The platform should be built as modular services with shared schemas and a common event envelope.

## Service: quote-service

### Responsibilities

- Accept quote requests.
- Validate product eligibility.
- Load product configuration and rating rules.
- Calculate premium.
- Generate explainability output.
- Emit quote events.

### Initial endpoints

```http
POST /quotes
GET /quotes/{quote_id}
POST /quotes/{quote_id}/recalculate
POST /quotes/{quote_id}/accept
POST /quotes/{quote_id}/expire
```

### Core records

```text
quote
quote_input_snapshot
quote_rating_result
quote_factor
quote_reason_code
quote_status_history
```

## Service: risk-appetite-service

### Responsibilities

- Evaluate whether a risk fits current appetite.
- Calculate exposure concentration.
- Estimate capital and reserve impacts.
- Check policy limits and reinsurance availability.
- Return decision and reason codes.

### Initial endpoints

```http
POST /risk-appetite/evaluate
GET /risk-appetite/policies/current
POST /risk-appetite/scenarios
GET /risk-appetite/exposure-summary
```

### Decision values

```text
ACCEPT
ACCEPT_WITH_LIMITS
ACCEPT_WITH_REINSURANCE
REFER_TO_UNDERWRITER
DECLINE
REQUEST_MORE_INFO
WAITLIST
```

## Service: policy-service

### Responsibilities

- Bind accepted quotes.
- Issue policy versions.
- Manage endorsements.
- Manage cancellation and reinstatement.
- Generate policy lifecycle events.
- Trigger blockchain commitments.

### Initial endpoints

```http
POST /policies/bind
GET /policies/{policy_id}
POST /policies/{policy_id}/endorsements
POST /policies/{policy_id}/cancel
POST /policies/{policy_id}/renew
POST /policies/{policy_id}/sync-chain
```

## Service: ai-agent-orchestrator

### Responsibilities

- Manage sessions.
- Classify intent.
- Retrieve approved product and policy knowledge.
- Call permissioned tools.
- Route human review.
- Produce compliant customer-facing responses.

### Initial endpoints

```http
POST /agent/sessions
POST /agent/sessions/{session_id}/messages
POST /agent/sessions/{session_id}/handoff
GET /agent/sessions/{session_id}/audit
```

## Service: claims-service

### Responsibilities

- Create claim records.
- Collect FNOL.
- Verify coverage.
- Manage evidence metadata.
- Set reserves.
- Route claim decisions.
- Trigger payout commitments.

### Initial endpoints

```http
POST /claims
GET /claims/{claim_id}
POST /claims/{claim_id}/evidence
POST /claims/{claim_id}/coverage-check
POST /claims/{claim_id}/reserve
POST /claims/{claim_id}/decision
POST /claims/{claim_id}/payout
```

## Service: treasury-service

### Responsibilities

- Track premium cashflow.
- Allocate earned/unearned premium.
- Calculate reserves.
- Maintain liquidity ladder.
- Evaluate treasury proposals.
- Require approvals.
- Emit reserve attestations.

### Initial endpoints

```http
POST /treasury/premium-received
POST /treasury/reserve-snapshots
GET /treasury/liquidity-ladder
POST /treasury/proposals
POST /treasury/proposals/{proposal_id}/approve
POST /treasury/proposals/{proposal_id}/execute
```

## Service: blockchain-gateway

### Responsibilities

- Convert off-chain events into chain transactions.
- Submit idempotent transactions.
- Index receipts.
- Reconcile contract state to off-chain records.
- Enforce signer and contract permissions.

### Initial endpoints

```http
POST /chain/policies/register
POST /chain/premiums/record
POST /chain/claims/record
POST /chain/reserves/attest
GET /chain/transactions/{tx_hash}
GET /chain/reconcile
```

## Event Envelope

```json
{
  "event_id": "evt_01HX...",
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

## Idempotency

Every write endpoint should accept or generate an idempotency key. Chain writes must use an outbox pattern:

```text
application event
  -> outbox row
  -> blockchain worker
  -> transaction submitted
  -> receipt indexed
  -> off-chain record updated
  -> reconciliation job verifies state
```
