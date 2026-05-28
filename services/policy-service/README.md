# Policy Service

Policy lifecycle management, bind flow, audit packet generation, and human approval workflow.

## Architecture

```
policy-service/
├── pyproject.toml
├── data/
│   └── sample-policies/
│       └── sample_policy_v1.yml      # Sample policy YAML
├── policy_service/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # Configuration
│   ├── domain/
│   │   ├── __init__.py
│   │   └── models.py                # Domain models (PolicyState, BindRequest, etc.)
│   ├── engine/
│   │   ├── __init__.py
│   │   └── policy_engine.py         # Policy lifecycle engine
│   ├── storage/
│   │   ├── __init__.py
│   │   └── policy_store.py          # Policy persistence (in-memory for MVP)
│   └── api/
│       ├── __init__.py
│       └── app.py                   # FastAPI application
└── tests/
    └── test_policy_service.py       # Unit tests
```

## Features

- **Policy Lifecycle**: Draft → Pending Bind → Active → Endorsement → Cancelled → Expired
- **Bind Flow**: AI prepares bind request → human approval → policy bound → blockchain commitment
- **Audit Packets**: SHA-256 commitment hashes for blockchain storage
- **Human Approval**: Approval requests with expiration and comments
- **Policy Documents**: Declaration, certificate, endorsement, cancellation, renewal
- **State Machine**: Valid transitions enforced by PolicyEngine

## Policy Lifecycle

```
draft ──→ pending_bind ──→ active ──→ endorsement ──→ active
                                  │              ↓
                                  │            active
                                  ↓
                              cancelled ←── expired
                              ↑
                              draft (reactivate)
```

## API Endpoints

### POST /policies/bind
Create a bind request from a quote.

**Request:**
```json
{
  "quote_id": "uuid",
  "effective_date": "2026-06-01T00:00:00",
  "expiration_date": "2027-06-01T00:00:00",
  "bind_method": "human_approval",
  "ai_confidence": 0.85
}
```

**Response:**
```json
{
  "bind_request": { ... },
  "approval_request": { ... },
  "message": "Bind request created. Approval required."
}
```

### POST /policies/{policy_id}/approve
Process a human approval decision.

**Request:**
```json
{
  "approval_status": "approved",
  "approver": "underwriter_1",
  "comments": "All checks passed"
}
```

### POST /policies/{policy_id}/transition
Transition a policy to a new state.

**Request:**
```json
{
  "target_state": "active"
}
```

### GET /policies/{policy_id}
Get a policy by ID.

### GET /policies
List policies, optionally filtered by state.

### POST /policies/{policy_id}/documents
Add a policy document.

### GET /policies/{policy_id}/documents
Get all documents for a policy.

### GET /health
Health check endpoint.

## Configuration

Environment variables (prefix: `POLICY_SERVICE_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./policy-service.db` | Database URL |
| `LOG_LEVEL` | `INFO` | Logging level |
| `BIND_REQUEST_EXPIRY_HOURS` | 24 | Bind request expiry (hours) |
| `APPROVAL_REQUEST_EXPIRY_HOURS` | 24 | Approval request expiry (hours) |
| `BLOCKCHAIN_GATEWAY_URL` | `http://localhost:8545` | Blockchain gateway URL |

## Running Tests

```bash
cd services/policy-service
pip install -e ".[dev]"
pytest
```

## Development

1. Install dependencies: `pip install -e ".[dev]"`
2. Run FastAPI: `uvicorn policy_service.api.app:app --reload`
3. Tests: `pytest`
