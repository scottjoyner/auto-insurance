# Production Hardening Runbook

## Goal

This runbook captures the final production-hardening steps for the auto-insurance platform after the repository-level scaffolds are in place.

## Required authentication settings

Production deployments must disable dev tokens:

```bash
INSURANCE_AUTH_MODE=jwt
INSURANCE_ALLOW_DEV_TOKENS=false
INSURANCE_JWT_ALGORITHM=RS256
INSURANCE_JWT_JWKS_URL=https://<idp>/.well-known/jwks.json
INSURANCE_JWT_ISSUER=https://<idp>/
INSURANCE_JWT_AUDIENCE=auto-insurance-api
```

HS256 is acceptable only for local integration or controlled internal test environments.

## Database migration validation

SQLite smoke validation:

```bash
python scripts/apply_sql_migrations.py --database /tmp/quote.db --migrations services/quote-service/migrations
python scripts/apply_sql_migrations.py --database /tmp/risk.db --migrations services/risk-appetite-service/migrations
python scripts/apply_sql_migrations.py --database /tmp/policy.db --migrations services/policy-service/migrations
```

Postgres validation:

```bash
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/auto_insurance_test
python scripts/apply_sql_migrations_sqlalchemy.py --database-url "$DATABASE_URL" --service quote --migrations services/quote-service/migrations
python scripts/apply_sql_migrations_sqlalchemy.py --database-url "$DATABASE_URL" --service risk --migrations services/risk-appetite-service/migrations
python scripts/apply_sql_migrations_sqlalchemy.py --database-url "$DATABASE_URL" --service policy --migrations services/policy-service/migrations
```

## Alembic next step

Each service has an Alembic scaffold. The next local step is to generate real revision files after installing service dependencies:

```bash
cd services/quote-service && alembic revision --autogenerate -m "phase1 quote baseline"
cd ../risk-appetite-service && alembic revision --autogenerate -m "phase1 risk baseline"
cd ../policy-service && alembic revision --autogenerate -m "phase1 policy baseline"
```

Review generated revisions manually before applying.

## Ownership enforcement

Quote and policy APIs now enforce actor-scoped access using tenant/customer claims from `ActorContext`.

Required JWT claims for customer-scoped access:

```json
{
  "sub": "user-id",
  "roles": ["CUSTOMER"],
  "tenant_id": "tenant-1",
  "customer_id": "customer-1"
}
```

Agents should include `tenant_id`; customer-specific workflows should include `customer_id` when available.

## Event broker adapters

The events package now includes:

- `StdoutPublisher`
- `JsonlPublisher`
- `KafkaPublisher`
- `SnsPublisher`
- `PubSubPublisher`

Production deployment must pick one broker-backed adapter and run an outbox worker process.

Recommended order:

1. Kafka for internal event streaming.
2. SNS for AWS-native fanout.
3. Pub/Sub for GCP-native fanout.

## Secret providers

The secrets package now includes:

- `EnvSecretProvider`
- `FileSecretProvider`
- `AwsSecretsManagerProvider`
- `VaultSecretProvider`

Production should use AWS Secrets Manager or Vault. Environment variables are acceptable only for local development and CI.

## Observability

Set the OTLP endpoint to enable tracing:

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318/v1/traces
```

Services should call:

```python
from insurance_observability.otel import configure_opentelemetry, instrument_fastapi

configure_opentelemetry("quote-service")
instrument_fastapi(app)
```

PII-bearing log payloads must pass through `redact_mapping` before logging.

## Compliance documents

The document package includes draft renderers for:

- adverse-action notices
- policy packets

These are scaffolds only. Do not send generated notices or policy packets to customers until templates have been reviewed by counsel and mapped to filed forms per jurisdiction.

## Pre-production acceptance checklist

- [ ] CI green on Phase 1 workflow.
- [ ] CI green on Postgres workflow.
- [ ] Dev tokens disabled in production.
- [ ] JWT issuer/audience/JWKS configured.
- [ ] Postgres migrations applied.
- [ ] Outbox worker deployed.
- [ ] Broker adapter configured.
- [ ] Secret manager configured.
- [ ] OTLP tracing configured.
- [ ] PII redaction verified.
- [ ] Ownership tests passing.
- [ ] Bind approval workflow tested end-to-end.
- [ ] Policy/adverse-action templates reviewed by counsel.
