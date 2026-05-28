# API Contracts

## Purpose

This document defines the API contract boundaries for the blockchain gateway service.
All write endpoints support idempotency keys, authenticated actors, correlation IDs,
audit logging, schema validation, and versioned response shapes.

## Blockchain Gateway Endpoints

### Policy Registration

```http
POST /chain/policies/register
Content-Type: application/json

{
  "policy_id": "pol_123",
  "commitment_hash": "0xabc...",
  "status": "PENDING"
}

Response:
{
  "success": true,
  "outbox_id": "uuid-here",
  "policy_id": "pol_123",
  "message": "Policy queued for blockchain registration"
}
```

### Update Policy Status

```http
POST /chain/policies/{policy_id}/status
Content-Type: application/json

{
  "status": "ACTIVE"
}

Response:
{
  "success": true,
  "outbox_id": "uuid-here",
  "policy_id": "pol_123",
  "message": "Status update queued for blockchain"
}
```

### Record Premium Event

```http
POST /chain/premiums/record
Content-Type: application/json

{
  "policy_id": "pol_123",
  "commitment_hash": "0xabc..."
}

Response:
{
  "success": true,
  "outbox_id": "uuid-here",
  "policy_id": "pol_123",
  "message": "Premium event queued for blockchain submission"
}
```

### Record Claim Event

```http
POST /chain/claims/record
Content-Type: application/json

{
  "policy_id": "pol_123",
  "commitment_hash": "0xabc..."
}

Response:
{
  "success": true,
  "outbox_id": "uuid-here",
  "policy_id": "pol_123",
  "message": "Claim event queued for blockchain submission"
}
```

### Attest Reserves

```http
POST /chain/reserves/attest
Content-Type: application/json

{
  "policy_id": "pol_123",
  "commitment_hash": "0xabc..."
}

Response:
{
  "success": true,
  "outbox_id": "uuid-here",
  "policy_id": "pol_123",
  "message": "Reserve attestation queued for blockchain submission"
}
```

### Get Transaction

```http
GET /chain/transactions/{tx_hash}

Response:
{
  "tx_hash": "0xdef...",
  "block_number": 42,
  "status": "confirmed",
  "gas_used": 21000,
  "logs": 1
}
```

### Reconcile

```http
GET /chain/reconcile?window_hours=24

Response:
{
  "timestamp": "2026-05-27T22:00:00Z",
  "window_hours": 24,
  "local_events_count": 10,
  "chain_events_count": 10,
  "missing_from_chain": [],
  "missing_from_local": [],
  "hash_mismatches": [],
  "discrepancies": [],
  "is_clean": true
}
```

### Query Policy

```http
GET /policies/{policy_id}

Response:
{
  "policy_id": "0xabc...",
  "commitment_hash": "0xdef...",
  "status": "ACTIVE",
  "committed_at": 1716854400,
  "committed_by": "0x123..."
}
```

### Query Policy Status

```http
GET /policies/{policy_id}/status

Response:
{
  "policy_id": "pol_123",
  "status": "ACTIVE"
}
```

### Query Policy Events

```http
GET /policies/{policy_id}/events

Response:
[
  {
    "index": 0,
    "event_type": "BIND",
    "policy_id": "0xabc...",
    "commitment_hash": "0xdef...",
    "committed_at": 1716854400,
    "committed_by": "0x123..."
  }
]
```

### Query Events by Type

```http
GET /events/by-type/{event_type}

Response:
[
  {
    "index": 0,
    "event_type": "BIND",
    "policy_id": "0xabc...",
    "commitment_hash": "0xdef...",
    "committed_at": 1716854400,
    "committed_by": "0x123..."
  }
]
```

### Outbox Stats

```http
GET /outbox/stats

Response:
{
  "pending": 5,
  "submitted": 3,
  "committed": 42,
  "failed": 0
}
```

### Health Check

```http
GET /health

Response:
{
  "status": "healthy",
  "service": "blockchain-gateway",
  "connected": true,
  "chain_id": 31337,
  "outbox": {
    "pending": 0,
    "submitted": 0,
    "committed": 42,
    "failed": 0
  },
  "reconciler_enabled": true,
  "signer_policy": {
    "policy_commiters": [],
    "status_updaters": [],
    "event_recorders": [],
    "allow_all": true
  }
}
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

## Status Enum

| Value      | Description              |
|------------|--------------------------|
| PENDING    | Policy committed, pending activation |
| ACTIVE     | Policy is active         |
| ENDORSEMENT | Policy under endorsement review |
| CANCELLED  | Policy has been cancelled |
| EXPIRED    | Policy has expired       |

## Event Type Enum

| Value            | Description              |
|------------------|--------------------------|
| BIND             | Policy binding event     |
| ENDORSEMENT      | Endorsement event        |
| CANCELLATION     | Cancellation event       |
| RENEWAL          | Renewal event            |
| CLAIM_FILING     | Claim filing event       |
| CLAIM_SETTLEMENT | Claim settlement event   |
