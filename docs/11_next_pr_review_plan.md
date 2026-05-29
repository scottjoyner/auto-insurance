# Next PR Review Plan

Owner: Platform Engineering  
Audience: engineering, security, compliance, operations  
Last reviewed: 2026-05-29  
Status: active implementation review plan

## Purpose

This document defines the next reviewable PR sequence after the Phase 1 and production-hardening work. Each PR should be small enough to review independently and must keep CI green.

## PR 1 — Restore strict documentation requirements

### Scope

- Keep `scripts/validate_docs.py` or an equivalent CI check enforcing required documentation.
- Required documents:
  - `docs/00_documentation_index.md`
  - `docs/07_employee_operating_manual.md`
  - `docs/08_claims_crm_operating_guide.md`
  - `docs/09_blockchain_security_review.md`
  - `docs/10_markdown_cleanup_register.md`
- Required header fields:
  - `Owner:`
  - `Audience:`
  - `Last reviewed:`
  - `Status:`

### Acceptance criteria

- CI fails when a required doc is missing.
- CI fails when a required header is missing.
- CI passes with the current required docs.

## PR 2 — Tenant/customer ownership enforcement hardening

### Scope

- Keep ownership enforcement in quote endpoints.
- Keep ownership enforcement in policy endpoints.
- Add repository-level query helpers where endpoint logic is still doing direct session access.
- Add tests for cross-tenant and cross-customer reads, lists, accepts, and approvals.

### Acceptance criteria

- A customer cannot read another customer's quote.
- A customer cannot see another customer's quote in list results.
- A customer or agent cannot read another tenant's bind request or policy.
- Privileged roles are explicitly tested.

## PR 3 — Production identity provider readiness

### Scope

- Validate HS256 mode for internal/test deployments.
- Validate RS256/JWKS mode for external identity providers.
- Document required claims: `sub`, `roles`, `tenant_id`, `customer_id`.
- Add negative tests for missing role, wrong issuer, wrong audience, and disabled dev tokens.

### Acceptance criteria

- `INSURANCE_AUTH_MODE=jwt` rejects dev tokens when `INSURANCE_ALLOW_DEV_TOKENS=false`.
- Invalid issuer/audience is rejected.
- Missing role is rejected.
- Tenant/customer claims propagate into `ActorContext`.

## PR 4 — Postgres integration hardening

### Scope

- Run repository tests against Postgres in CI.
- Confirm SQLite-only types/assumptions are removed or isolated.
- Apply baseline SQL migrations to Postgres or replace them with Alembic revisions.

### Acceptance criteria

- Postgres CI starts Postgres 16.
- Quote, risk, and policy repository tests pass against Postgres.
- Migration validation fails on invalid SQL.

## PR 5 — Event outbox publisher

### Scope

- Replace prototype JSONL-only outbox behavior with publisher abstraction usage.
- Add broker adapter interface for Kafka/SNS/PubSub.
- Add retry/backoff and dead-letter behavior.
- Add event publication audit records.

### Acceptance criteria

- Quote events can be drained once.
- Policy events can be drained once.
- Failed publish attempts are retryable.
- Published event payloads are redacted where needed.

## PR 6 — Document generation and compliance notices

### Scope

- Promote policy packet and adverse-action notice renderers from scaffold to versioned template interfaces.
- Add template version IDs.
- Add compliance review status fields.
- Add tests for required reason-code inclusion.

### Acceptance criteria

- Declined risk can generate an adverse-action draft.
- Issued policy can generate a policy packet draft.
- No draft is marked deliverable without review status.

## PR 7 — Observability and redaction

### Scope

- Ensure all services use correlation-ID middleware.
- Add structured JSON logging config.
- Add OpenTelemetry hooks.
- Add PII redaction tests for logs and event payloads.

### Acceptance criteria

- Every response includes `X-Request-ID`.
- Logs include request ID, service name, route, status, and duration.
- Sensitive fields are redacted in structured logs.

## PR 8 — Service orchestration

### Scope

- Use the orchestration package to execute quote → risk → bind workflow.
- Add idempotency propagation.
- Add retry behavior for transient service failures.
- Add audit traces for each service call.

### Acceptance criteria

- Workflow produces quote snapshot, risk assessment, and bind request.
- Duplicate workflow request does not create duplicate bind request.
- Failed risk assessment does not create bind request.

## Merge discipline

- Each PR must keep both Phase 1 CI and Postgres Integration CI green.
- Each PR must include tests for changed behavior.
- Security or compliance-affecting PRs require human review from the responsible owner.
- Documentation updates must be included when behavior changes.
