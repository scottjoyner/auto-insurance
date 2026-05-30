# Remaining Implementation Gap Register

Owner: Platform Engineering  
Audience: engineering, product, compliance, operations, security  
Last reviewed: 2026-05-29  
Status: active implementation gap register

## Purpose

This register tracks the remaining work required to evolve the repository from a local, testable foundation into a production-grade insurance operating system.

Severity definitions:

- **P0**: blocks production credibility or safe regulated workflow.
- **P1**: required for complete MVP operations.
- **P2**: required for scale, automation, or advanced operations.
- **P3**: optimization, analytics, or future platform leverage.

## P0 gaps

### P0.1 Customer/account service

Current state: tenant/customer IDs are carried in auth context and stamped on service records, but there is no customer/account service as source of truth.

Required deliverables:

- customer-service package
- Customer, Account, Tenant, Contact, Address, IdentityLink models
- ownership lookup API
- customer 360 API
- tenant isolation tests
- migration baseline
- Docker/Compose/CI integration

Acceptance criteria:

- quote, policy, and claims can validate customer/tenant existence;
- customer search is role-scoped;
- cross-tenant access is denied;
- account/customer lifecycle events are emitted.

### P0.2 UI foundation

Current state: no production frontend exists.

Required deliverables:

- `apps/web` app
- role-aware app shell
- typed API client
- shared design system
- customer portal routes
- agent desktop routes
- underwriter console routes
- claims workspace routes
- PII masking component
- approval controls

Acceptance criteria:

- user can navigate quote, bind, and claim flows with mock/real APIs;
- regulated actions are visibly role-gated;
- every screen shows environment and request ID;
- PII masking is default for sensitive fields.

### P0.3 Real identity provider readiness

Current state: JWT/JWKS validation exists, but no IdP integration guide or e2e test with real JWKS fixture.

Required deliverables:

- static JWKS test fixture
- RS256 positive and negative tests
- IdP setup guide
- required claims contract
- production env validation on service startup

Acceptance criteria:

- dev tokens rejected in production mode;
- RS256 tokens validate against JWKS;
- wrong issuer/audience/kid fails closed;
- missing tenant/customer claims fails for customer-facing endpoints.

### P0.4 End-to-end workflow tests

Current state: service tests exist, orchestration client has mock transport, but no full service e2e test.

Required deliverables:

- e2e test harness
- quote -> risk -> bind -> approve -> policy flow
- policy -> FNOL -> evidence -> reserve -> denial-review flow
- event outbox validation

Acceptance criteria:

- e2e tests pass in CI or scheduled workflow;
- all generated records preserve tenant/customer ownership;
- duplicate bind requests are idempotent.

### P0.5 Production documentation enforcement

Current state: required docs are present and CI enforces headers inline.

Required deliverables:

- restore strict standalone `scripts/validate_docs.py` or keep inline enforcement permanently documented;
- remove stale phrases from old docs or mark archived;
- docs index points to current source of truth.

Acceptance criteria:

- missing required docs fail CI;
- missing required headers fail CI;
- stale docs are tracked in cleanup register.

## P1 gaps

### P1.1 Policy administration lifecycle

Current state: bind and issued policy records exist, but endorsements/cancellations/reinstatements/renewals are not implemented.

Required deliverables:

- endorsement requests
- cancellation workflow
- reinstatement workflow
- renewal workflow
- policy document packets
- policy lifecycle timeline

### P1.2 Document service

Current state: document renderers are package-level scaffolds.

Required deliverables:

- document-service
- template version storage
- jurisdiction/product template selection
- draft/review/approved statuses
- PDF generation pipeline
- delivery audit fields

### P1.3 Event broker adapter

Current state: event publisher abstraction exists with stdout/JSONL publishers.

Required deliverables:

- Kafka/SNS/PubSub adapter
- retry/backoff
- dead-letter queue
- idempotent publish marking
- event schema registry

### P1.4 OpenTelemetry and production logging

Current state: correlation IDs and redaction helper exist.

Required deliverables:

- JSON logging config
- service name/version injection
- OpenTelemetry FastAPI instrumentation
- trace propagation across orchestration client
- metrics endpoint
- PII redaction in event/log pipeline

### P1.5 Claims coverage and payments

Current state: claims support FNOL, evidence, reserve approval, denial-review draft.

Required deliverables:

- coverage check adapter to policy service
- claim payment recommendation
- claim payment manager approval
- evidence storage adapter
- claim assignment and SLA timers
- fraud/litigation referral status

### P1.6 Risk and underwriting operations

Current state: risk policy lifecycle exists, assessments are persisted.

Required deliverables:

- underwriting referral queue
- appetite utilization dashboard
- portfolio concentration view
- reinsurance impact view
- decline review workflow
- adverse-action draft for declined risks

## P2 gaps

### P2.1 Blockchain gateway

Current state: blockchain-first design exists, but gateway implementation is not built out.

Required deliverables:

- blockchain-gateway service
- local Anvil/Hardhat contracts
- PolicyRegistry
- AuditEventRegistry
- commitment writer
- signer approval workflow
- reconciliation report

Rules:

- never write PII to chain;
- commit hashes/proofs only;
- human signer approval required for admin actions.

### P2.2 Treasury and float service

Current state: not implemented.

Required deliverables:

- premium allocation records
- reserve snapshots
- liquidity ladder
- investment policy statement constraints
- counterparty limits
- treasury approval workflow
- board approval checkpoints

### P2.3 Billing and payments

Current state: not implemented.

Required deliverables:

- invoice schedules
- payment provider abstraction
- payment events
- refund/cancellation accounting
- delinquency workflow
- reconciliation reports

### P2.4 Customer communications

Current state: messages are design target only.

Required deliverables:

- message-service
- secure inbox
- outbound email/SMS provider abstraction
- template versions
- delivery status
- opt-out/compliance preferences

## P3 gaps

### P3.1 Advanced AI assistant

Required deliverables:

- tool registry
- policy-enforced tool permissions
- retrieval over operating docs
- customer support assistant
- underwriter assistant
- claims summarizer
- compliance draft assistant

Hard rule: AI never has final authority for regulated decisions.

### P3.2 Analytics and reporting

Required deliverables:

- operational dashboards
- quote conversion analytics
- claim severity analytics
- loss ratio reporting
- reserve adequacy reporting
- underwriting referral analytics

### P3.3 Multi-product expansion

Required deliverables:

- product registry
- versioned rate/rule/form sets
- jurisdiction configuration
- product lifecycle approval workflow

## Immediate next build recommendation

1. Build customer-service as P0.1.
2. Build UI foundation as P0.2.
3. Add full e2e workflow test harness as P0.4.
4. Add RS256/JWKS fixture tests as P0.3.
5. Add document-service as P1.2.

## Definition of production readiness

The system should not be called production-ready until:

- customer/account ownership is centralized;
- UI supports complete staff/customer workflows;
- JWT/JWKS production auth is mandatory;
- Postgres migrations are managed through Alembic;
- broker-backed event publishing exists;
- legal-approved templates exist;
- treasury and capital controls exist;
- blockchain commitments are PII-safe and reconciled;
- full e2e tests pass;
- security/compliance review is complete.
