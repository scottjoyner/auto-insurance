# Current State Assessment and P0 Plan

## Status

This repository is an architecture prototype with partial service drafts. It is not production-ready and must not be used to sell, bind, administer, or adjudicate real insurance products.

## Current implementation reality

Implemented in draft form:

- Rating DSL parser and evaluator models for the sample personal auto product.
- Quote service FastAPI draft with a quote generation endpoint.
- Risk appetite service FastAPI draft with an assessment endpoint.
- In-memory quote store and helper tests.
- Governance YAMLs for AI authority, risk appetite, treasury, and product approval.
- Architecture documentation for future policy, blockchain, AI, claims, treasury, CRM, compliance, and analytics services.

Not yet operational:

- Durable quote, risk, policy, claim, or audit persistence.
- Production authentication and authorization.
- Customer or session management.
- Quote-to-bind workflow.
- Human approval workflow.
- Payment collection.
- Policy issuance.
- Claims adjudication.
- Blockchain gateway.
- Treasury allocation.
- Regulatory filing workflow.
- Production secrets management.

## Material gaps found

Security gaps:

- No production identity provider or JWT signature verification.
- No tenant or customer ownership enforcement.
- Risk policy update endpoint was originally mutable at runtime.
- Quote service previously allowed wildcard CORS.
- No rate limiting, request-size limits, or abuse controls.
- No PII redaction or field-level data classification enforcement.

Logic gaps:

- Quote recalculation still lacks durable quote lookup, so old/new delta values are incomplete.
- Quote explain and quote health lookup still require durable storage.
- Rating DSL JSON Schema and YAML/parser contract are inconsistent.
- Risk appetite assessments are not persisted and do not record the policy version used.
- Underwriting referral and approval state machines are not implemented.

Operational gaps:

- No root docker-compose.yml existed before the P0 pass.
- Service Dockerfiles still need a production-grade monorepo build pattern.
- No CI workflow enforces tests, lint, schema validation, secret scans, or Docker builds.
- No database migrations.
- No event outbox.
- No observability baseline.

## P0 implementation cycle

### P0.1 Repository truth and planning

- Keep README explicit that the repo is a prototype.
- Add this current-state assessment.
- Reconcile milestone status in docs.
- Track completed versus planned endpoints.

### P0.2 Shared security scaffold

- Add `packages/security` with a FastAPI RBAC dependency.
- Require authenticated actor context for business endpoints.
- Use deny-by-default role checks.
- Treat the current token format as development-only.

### P0.3 Service hardening defaults

- Remove wildcard CORS.
- Make allowed origins configurable by environment.
- Keep `/health` unauthenticated.
- Add request and actor logging to protected endpoints.
- Disable runtime policy mutation unless explicitly enabled for local development.

### P0.4 Rating correctness

- Fix `base_rates` lookup for variable coverage base amounts.
- Fail unknown coverage tiers instead of defaulting silently.
- Carry reason codes for eligibility failures.
- Add golden premium tests in the next pass.

### P0.5 Deployability baseline

- Add a root `docker-compose.yml` for currently drafted services and Postgres.
- Add `.env.example`.
- Add `SECURITY.md`.

## P1.1 Quote service deliverables

- Postgres-backed quote store.
- Alembic migrations.
- Quote versioning.
- Quote status history.
- Quote rating trace table.
- Quote event outbox.
- Complete APIs: create, retrieve, explain, recalculate, accept, expire, list.
- Integration tests with Postgres.

## P1.2 Risk appetite deliverables

- Versioned risk policy store.
- Draft, submit, approve, and activate workflow.
- Persisted risk assessment records.
- Policy diff and rollback endpoints.
- Immutable policy versions with effective dates.

## P1.3 Policy bind deliverables

- Policy service skeleton.
- Bind request lifecycle.
- Human approval workflow.
- Quote-to-policy integration.
- Audit packet generation.

## P2 and later deliverables

- Blockchain commitment gateway with local Anvil.
- Claims FNOL and coverage check service.
- Treasury reserve and allocation stubs.
- AI orchestrator with audited tool permission enforcement.
- Compliance and data protection enforcement.
