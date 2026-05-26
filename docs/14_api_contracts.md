# API Contracts

## Purpose

This document defines initial API contract boundaries. The first implementation should convert these into OpenAPI specs.

## Common Requirements

Every write endpoint should support:

- idempotency key
- authenticated actor
- correlation ID
- audit logging
- schema validation
- versioned response shape

## Quote Service

```http
POST /quotes
GET /quotes/{quote_id}
POST /quotes/{quote_id}/recalculate
POST /quotes/{quote_id}/accept
POST /quotes/{quote_id}/expire
```

Quote response should include:

```json
{
  "quote_id": "quote_123",
  "status": "GENERATED",
  "product_id": "sample_personal_auto_v1",
  "product_version": "2026.001",
  "jurisdiction": "SAMPLE",
  "premium": 500.0,
  "bind_eligible": false,
  "reason_codes": [],
  "input_snapshot_hash": "hash",
  "expires_at": "2026-06-26T00:00:00Z"
}
```

## Risk Appetite Service

```http
POST /risk-appetite/evaluate
GET /risk-appetite/policies/current
POST /risk-appetite/scenarios
GET /risk-appetite/exposure-summary
```

Decision response should include:

```json
{
  "decision": "REFER_TO_UNDERWRITER",
  "reason_codes": ["LIMIT_REQUIRES_UNDERWRITING"],
  "required_approvals": ["UNDERWRITER_L2"],
  "audit_reference": "audit_123"
}
```

## Policy Service

```http
POST /policies/bind
GET /policies/{policy_id}
POST /policies/{policy_id}/endorsements
POST /policies/{policy_id}/cancel
POST /policies/{policy_id}/renew
POST /policies/{policy_id}/sync-chain
```

## Claims Service

```http
POST /claims
GET /claims/{claim_id}
POST /claims/{claim_id}/evidence
POST /claims/{claim_id}/coverage-check
POST /claims/{claim_id}/reserve
POST /claims/{claim_id}/decision
POST /claims/{claim_id}/payout
```

## AI Agent Orchestrator

```http
POST /agent/sessions
POST /agent/sessions/{session_id}/messages
POST /agent/sessions/{session_id}/handoff
GET /agent/sessions/{session_id}/audit
```

## Treasury Service

```http
POST /treasury/premium-received
POST /treasury/reserve-snapshots
GET /treasury/liquidity-ladder
POST /treasury/proposals
POST /treasury/proposals/{proposal_id}/approve
POST /treasury/proposals/{proposal_id}/execute
GET /treasury/solvency-dashboard
```

## Blockchain Gateway

```http
POST /chain/policies/register
POST /chain/premiums/record
POST /chain/claims/record
POST /chain/reserves/attest
GET /chain/transactions/{tx_hash}
GET /chain/reconcile
```

## Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request failed schema validation.",
    "details": [],
    "correlation_id": "corr_123"
  }
}
```
