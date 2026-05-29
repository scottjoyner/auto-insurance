# Production Gap Closure Report

## Status

This document tracks the best-effort production hardening pass after Phase 1.

## Completed in this pass

### Authentication

- Added JWT auth mode behind `INSURANCE_AUTH_MODE=jwt`.
- Added HS256 validation for internal/test deployments.
- Added RS256/JWKS-compatible validation through PyJWT `PyJWKClient`.
- Added issuer and audience validation settings.
- Added tenant/customer claim propagation into `ActorContext`.
- Kept dev-token mode for local development.

### Orchestration

- Added `packages/orchestration`.
- Added quote to risk to policy workflow client.
- Added orchestration test with HTTP mock transport.
- Added CI execution for orchestration tests.

### Ownership and access control

- Added tenant/customer context to `ActorContext`.
- Added quote ownership guard helper for record-level access checks.
- Added quote schema fields for tenant/customer ownership.

### Migrations

- Added SQL migration baselines for quote, risk, and policy services.
- Added lightweight migration runner for SQLite validation.
- Added Alembic environment scaffold for quote service.
- Added Alembic environment scaffold for risk appetite service.
- Added Alembic environment scaffold for policy service.

### Compliance

- Added bind compliance guard to block missing snapshots, non-bind-eligible quotes, and declined risks.
- Added policy API tests for declined-risk and non-bind-eligible rejection paths.

### Event publishing

- Added prototype outbox publisher script for quote and policy events.

## Remaining work that requires deeper local implementation

These items are not fully complete due to connector limits and the need for local test iteration:

1. Full endpoint-level tenant/customer filtering in quote service.
2. Full endpoint-level tenant/customer filtering in policy service.
3. Alembic revision files generated through `alembic revision --autogenerate`.
4. Postgres-backed integration tests that run the actual API stack against Postgres.
5. Production event broker publisher for Kafka/SNS/PubSub.
6. Secret manager integration for AWS Secrets Manager, Vault, or SOPS.
7. Policy PDF/document generation.
8. Adverse-action notice generation with jurisdiction-specific templates.
9. Full observability stack: OpenTelemetry traces, structured logs, redaction, metrics.

## Production deployment gates

Before production use, require:

- `INSURANCE_AUTH_MODE=jwt`.
- `INSURANCE_ALLOW_DEV_TOKENS=false`.
- `INSURANCE_JWT_ISSUER` configured.
- `INSURANCE_JWT_AUDIENCE` configured.
- `INSURANCE_JWT_JWKS_URL` configured for external IdP use.
- SQLite disabled for all services.
- Postgres migrations applied.
- Event outbox publisher connected to a broker.
- All PII fields classified and redacted in logs.
- Human approval enforced for bind, decline, claims, rating, treasury, and smart-contract actions.

## Recommended next local commands

```bash
python scripts/apply_sql_migrations.py --database /tmp/quote.db --migrations services/quote-service/migrations
python scripts/apply_sql_migrations.py --database /tmp/risk.db --migrations services/risk-appetite-service/migrations
python scripts/apply_sql_migrations.py --database /tmp/policy.db --migrations services/policy-service/migrations
pytest packages/security/tests
pytest packages/orchestration/tests
pytest services/quote-service/tests
pytest services/risk-appetite-service/tests
pytest services/policy-service/tests
```
