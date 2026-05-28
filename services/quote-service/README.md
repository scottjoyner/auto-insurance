# Quote Service

Insurance quote generation, recalculation, and explainability service.

## Architecture

```
quote-service/
├── pyproject.toml
├── data/
│   ├── sample-products/
│   │   └── sample_personal_auto_v1.yml    # Sample product YAML
│   └── risk-appetite-policy.yml           # Risk appetite policy
├── quote_service/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                    # Configuration
│   ├── domain/
│   │   ├── __init__.py
│   │   └── models.py                      # Domain models
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── quote_engine.py                # Core rating engine
│   │   ├── explainability.py              # Explainability reports
│   │   └── expiration_handler.py          # Quote expiration
│   ├── storage/
│   │   ├── __init__.py
│   │   └── quote_store.py                 # Quote persistence (in-memory)
│   └── api/
│       ├── __init__.py
│       └── app.py                         # FastAPI application
└── tests/
    └── test_quote_service.py              # Unit tests
```

## Features

- **Quote Generation**: Generate insurance quotes from product YAML definitions
- **Quote Recalculation**: Recalculate quotes with updated applicant data
- **Explainability**: Comprehensive explainability reports (JSON + text)
- **Quote Expiration**: Automatic quote expiration management
- **Risk Appetite Integration**: Integrated risk assessment via Risk Appetite Service

## API Endpoints

### POST /quotes
Generate a new insurance quote.

**Request:**
```json
{
  "applicant_data": {
    "age": 35,
    "vehicle_year": 2023,
    "coverage_type": "full",
    "jurisdiction": "SAMPLE"
  },
  "product_id": "sample_personal_auto_v1",
  "validity_days": 30
}
```

**Response:**
```json
{
  "quote_id": "uuid",
  "total_premium": 1200.0,
  "coverages": {"liability": 500.0, "collision": 400.0, "comprehensive": 300.0},
  "bind_eligible": true,
  "expires_at": "2026-06-27T00:00:00"
}
```

### POST /quotes/{quote_id}/recalculate
Recalculate a quote with updated data.

### GET /quotes/{quote_id}/explain
Get an explainability report for a quote.

### GET /health
Service health check.

## Configuration

Environment variables (prefix: `QUOTE_SERVICE_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_PRODUCT_YAML` | `data/sample-products/sample_personal_auto_v1.yml` | Default product YAML |
| `DEFAULT_VALIDITY_DAYS` | 30 | Default quote validity |
| `LOG_LEVEL` | INFO | Logging level |
| `AI_CONFIDENCE_THRESHOLD` | 0.7 | AI confidence threshold |

## Running Tests

```bash
cd services/quote-service
pip install -e ".[dev]"
pytest
```

## Development

1. Install dependencies: `pip install -e ".[dev]"`
2. Run FastAPI: `uvicorn quote_service.api.app:app --reload`
3. Tests: `pytest`
