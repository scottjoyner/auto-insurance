# Risk Appetite Service

Risk appetite policy evaluation for insurance quotes - exposure checks, capital/reserve impact, and reinsurance capacity.

## Architecture

```
risk-appetite-service/
├── pyproject.toml
├── data/
│   └── risk-appetite-policy.yml          # Risk appetite policy
├── risk_appetite_service/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                   # Configuration
│   ├── domain/
│   │   ├── __init__.py
│   │   └── models.py                     # Domain models
│   ├── engine/
│   │   ├── __init__.py
│   │   └── risk_engine.py                # Risk assessment engine
│   └── api/
│       ├── __init__.py
│       └── app.py                        # FastAPI application
└── tests/
    └── test_risk_appetite.py             # Unit tests
```

## Features

- **Exposure Concentration Checks**: Agency, geographic, and line-of-business concentration
- **Capital/Reserve Impact**: Estimated capital requirements and ratios
- **Reinsurance Impact**: Net retention, ceded amounts, and capacity utilization
- **Risk Scoring**: Weighted risk score across multiple categories
- **Decision Matrix**: Accept, Accept with Limits, Refer, or Decline
- **Policy Management**: Dynamic policy updates without restart

## API Endpoints

### POST /assess
Run a risk appetite assessment on a quote.

**Request:**
```json
{
  "quote_id": "uuid",
  "quote_data": {
    "total_premium": 1200.0,
    "age": 35,
    "vehicle_year": 2023,
    "claims_3yr": 0,
    "agency_id": "A001",
    "jurisdiction": "SAMPLE",
    "product_id": "personal_auto_v1"
  },
  "portfolio_state": {
    "total_agency_policies": 1000,
    "agency_counts": {"A001": 50},
    "jurisdiction_counts": {"SAMPLE": 200},
    "product_counts": {"personal_auto_v1": 400},
    "available_capital": 10000000.0,
    "capital_ratio": 0.15
  }
}
```

**Response:**
```json
{
  "assessment_id": "uuid",
  "decision": "ACCEPT",
  "risk_score": 25.0,
  "risk_level": "LOW",
  "category_breakdown": {
    "driver_age": 20.0,
    "claim_severity": 0.0,
    "vehicle_type": 10.0
  },
  "exposure_concentration": {
    "agency_concentration": {"within_limits": true},
    "geographic_concentration": {"within_limits": true}
  },
  "capital_impact": {
    "within_tolerance": true
  },
  "reinsurance_impact": {
    "within_capacity": true
  },
  "reason_codes": []
}
```

### GET /policy
Get the current risk appetite policy.

### POST /policy/update
Update the risk appetite policy dynamically.

### GET /health
Service health check.

## Risk Appetite Policy

The policy is defined in `data/risk-appetite-policy.yml`:

```yaml
version: "1.0"
categories:
  agency:
    name: "agency_concentration"
    threshold_pct: 10.0
    warning_pct: 7.0
    action_on_threshold: "REFER"
  jurisdiction:
    name: "geographic_concentration"
    threshold_pct: 15.0
    warning_pct: 10.0
    action_on_threshold: "REFER"
capital_requirements:
  min_capital_ratio: 0.05
reinsurance:
  retention_pct: 30.0
  total_capacity: 50000000.0
decision_matrix:
  low:
    max_score: 30
    decision: "ACCEPT"
  medium:
    max_score: 60
    decision: "ACCEPT_WITH_LIMITS"
  high:
    max_score: 80
    decision: "REFER"
  critical:
    max_score: 100
    decision: "DECLINE"
```

## Configuration

Environment variables (prefix: `RISK_APPETITE_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `POLICY_PATH` | `data/risk-appetite-policy.yml` | Policy YAML path |
| `PORTFOLIO_STATE_TTL` | 300 | Portfolio state TTL (seconds) |
| `LOG_LEVEL` | INFO | Logging level |

## Running Tests

```bash
cd services/risk-appetite-service
pip install -e ".[dev]"
pytest
```

## Development

1. Install dependencies: `pip install -e ".[dev]"`
2. Run FastAPI: `uvicorn risk_appetite_service.api.app:app --reload`
3. Tests: `pytest`
