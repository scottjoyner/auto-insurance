# Services

Service implementations for the insurance operating system.

## Services

| # | Service | Status | Description |
|---|---------|--------|-------------|
| 1 | [quote-service](quote-service/) | ✅ MVP | Quote generation, recalculation, explainability |
| 2 | [risk-appetite-service](risk-appetite-service/) | ✅ MVP | Risk appetite policy evaluation, exposure checks, capital/reserve impact |
| 3 | policy-service | 📋 Planned | Policy lifecycle, bind flow, audit packets |
| 4 | claims-service | 📋 Planned | FNOL intake, coverage check, claim processing |
| 5 | treasury-service | 📋 Planned | Premium allocation, reserve snapshots, treasury management |
| 6 | ai-agent-orchestrator | 📋 Planned | AI session management, tool permissions, model routing |
| 7 | blockchain-gateway | 📋 Planned | Policy commitment, audit events, smart contracts |

## Shared Dependencies

All services depend on:
- **shared-types**: Shared Python types for the platform
- **rating-dsl**: Rating DSL engine for deterministic rating

## Service Communication

Services communicate via:
- **REST API** (FastAPI) for synchronous requests
- **Event streaming** (future) for async communication
- **Shared event schemas** in `shared-types/` for event contracts

## Running Services

Each service has its own `pyproject.toml` and can be run independently:

```bash
# Quote Service
cd services/quote-service
pip install -e ".[dev]"
uvicorn quote_service.api.app:app --reload

# Risk Appetite Service
cd services/risk-appetite-service
pip install -e ".[dev]"
uvicorn risk_appetite_service.api.app:app --reload
```

## Service Registry

Service discovery is managed via:
- Local dev: docker-compose (future)
- Production: Kubernetes service mesh (future)
