# Remaining Gap Register and Execution Plan

Owner: Platform Engineering  
Audience: engineering, product, compliance, operations, security  
Last reviewed: 2026-05-29  
Status: active implementation gap register and delivery plan

## Purpose

This document turns the remaining gaps into a concrete execution plan. Each item includes current state, target outcome, implementation steps, deliverables, acceptance criteria, test requirements, dependencies, and definition of done.

Priority definitions:

- **P0**: blocks production credibility, tenant safety, or safe regulated workflow.
- **P1**: required for complete MVP operations.
- **P2**: required for scale, automation, capital operations, or advanced regulated workflows.
- **P3**: optimization, analytics, or future platform leverage.

## P0 — Production credibility and safety blockers

### P0.1 Customer/account service

**Current state**: `tenant_id` and `customer_id` are carried in actor context and stamped onto quote, policy, and claim records. There is no authoritative customer/account service.

**Target outcome**: A customer-service becomes the source of truth for tenants, accounts, customers, contacts, addresses, and identity-provider links. All business services can validate tenant/customer ownership against it.

**Implementation steps**:

1. Create `services/customer-service` FastAPI package.
2. Add SQLAlchemy models: `TenantRecord`, `AccountRecord`, `CustomerRecord`, `ContactRecord`, `AddressRecord`, `IdentityLinkRecord`, `CustomerEventRecord`.
3. Add repository methods for tenant creation, account creation, customer creation, customer lookup, identity-link lookup, and scoped search.
4. Add APIs:
   - `POST /tenants`
   - `POST /accounts`
   - `POST /customers`
   - `GET /customers/{customer_id}`
   - `GET /customers/search`
   - `GET /identity-links/{provider}/{subject}`
   - `GET /customers/{customer_id}/summary`
5. Add tenant/customer ownership middleware or helper used by quote, policy, and claims.
6. Add migration baseline and Alembic scaffold.
7. Add Dockerfile, compose entry, `.env.example` entries, and CI/Postgres CI tests.
8. Update orchestration client to resolve customer context before quote/bind/claim workflows.

**Deliverables**:

- customer-service package
- database models and migrations
- customer/account APIs
- ownership validation helper/client
- event outbox records
- repository/API tests
- Compose and CI integration

**Acceptance criteria**:

- customer search is scoped by tenant and role;
- customer detail rejects cross-tenant access;
- quote, policy, and claims can validate customer existence;
- identity-provider subject can resolve to customer/tenant;
- lifecycle events are emitted for tenant/account/customer creation.

**Required tests**:

- customer creation persists tenant/account/customer records;
- cross-tenant customer read is rejected;
- customer search returns only actor-scoped records;
- identity-link lookup works for JWT subject;
- Postgres repository tests pass.

**Dependencies**:

- existing `packages/security` ActorContext
- existing ownership fields in quote/policy/claims

**Definition of done**:

Customer-service is part of compose and CI; quote/policy/claims have a documented integration path for ownership validation.

### P0.2 UI foundation

**Current state**: no production frontend exists. Backend services are API-first and have no staff/customer workflow surface.

**Target outcome**: `apps/web` provides a role-aware app shell and first operational screens for customer, agent, underwriter, and claims workflows.

**Implementation steps**:

1. Create `apps/web` using React/Next.js or Vite React.
2. Add route groups:
   - `/customer`
   - `/agent`
   - `/underwriting`
   - `/claims`
   - `/admin`
3. Add typed API client for quote, risk, policy, claims, and future customer-service.
4. Add auth/session abstraction with dev-token and JWT modes.
5. Add global app shell: sidebar, environment banner, tenant selector, role indicator, request ID display.
6. Add shared components:
   - `AuditTimeline`
   - `StatusBadge`
   - `PIIRevealControl`
   - `ApprovalPanel`
   - `QuotePremiumBreakdown`
   - `RiskScoreCard`
   - `ClaimEvidenceTable`
   - `ReserveApprovalPanel`
   - `DocumentDraftViewer`
7. Add mock fixtures for quote, bind, claim, reserve, and denial-review flows.
8. Add component tests and route smoke tests.

**Deliverables**:

- `apps/web`
- design system components
- API client package/module
- role-aware navigation
- initial customer/agent/underwriter/claims screens
- UI test setup

**Acceptance criteria**:

- user can navigate to all major workspaces;
- role-gated actions are disabled and explain required role;
- PII is masked by default;
- every page shows environment and request ID;
- first quote, bind, and claim workflows are represented with mock or real API calls.

**Required tests**:

- route smoke tests;
- PII masking tests;
- role gating tests;
- API client serialization tests.

**Dependencies**:

- docs/12 production UI spec
- current quote/policy/risk/claims APIs
- future customer-service for customer search

**Definition of done**:

CI runs frontend tests; app renders role-aware shell and first workflow screens.

### P0.3 Real identity provider readiness

**Current state**: JWT/JWKS validation exists, HS256 and JWKS paths exist, and negative tests cover bad issuer/audience/missing roles. There is no static RS256 JWKS fixture or startup validation contract.

**Target outcome**: production identity mode is testable, documented, and fails closed.

**Implementation steps**:

1. Add RS256 keypair/JWKS test fixture under `packages/security/tests/fixtures`.
2. Add tests for valid RS256 token, invalid `kid`, wrong issuer, wrong audience, expired token, missing `roles`, missing `tenant_id`, and missing `customer_id`.
3. Add service startup validation that fails if `INSURANCE_AUTH_MODE=jwt` and required JWT settings are missing.
4. Add production IdP configuration guide.
5. Add optional role-claim mapping support if external IdP roles are namespaced.

**Deliverables**:

- JWKS fixture
- RS256 tests
- production auth configuration guide
- startup settings validator

**Acceptance criteria**:

- dev tokens are rejected when `INSURANCE_AUTH_MODE=jwt` and `INSURANCE_ALLOW_DEV_TOKENS=false`;
- RS256 tokens validate against fixture JWKS;
- invalid `kid`, issuer, audience, or missing claims fail closed;
- customer-facing endpoints reject tokens without tenant/customer claims.

**Required tests**:

- HS256 positive/negative tests;
- RS256 positive/negative tests;
- endpoint test for missing customer claims;
- startup validation unit test.

**Dependencies**:

- `packages/security`
- service settings modules

**Definition of done**:

Security CI proves both internal and external IdP modes, and production mode cannot start misconfigured.

### P0.4 End-to-end workflow tests

**Current state**: unit/API/repository tests exist. Orchestration client has mock-transport tests. There is no full service-level end-to-end test harness.

**Target outcome**: a reproducible CI workflow validates cross-service behavior and ownership preservation.

**Implementation steps**:

1. Add `tests/e2e` or `integration/e2e` suite.
2. Add docker compose test profile or TestClient-based multi-service harness.
3. Implement quote -> risk -> bind -> approve -> policy flow.
4. Implement policy -> FNOL -> evidence -> reserve -> approve -> denial-review flow.
5. Validate event outbox rows for each lifecycle stage.
6. Validate tenant/customer ownership across all created records.
7. Validate duplicate bind idempotency.

**Deliverables**:

- e2e test harness
- e2e workflow fixtures
- CI workflow or scheduled workflow
- failure troubleshooting doc

**Acceptance criteria**:

- e2e test produces quote, risk assessment, bind request, policy, claim, evidence, reserve, denial-review draft;
- all records preserve tenant/customer ownership;
- duplicate bind request does not create duplicate policy workflow;
- failed risk assessment does not create bind request.

**Required tests**:

- happy-path e2e;
- duplicate bind e2e;
- cross-tenant denial e2e;
- event outbox e2e.

**Dependencies**:

- quote/risk/policy/claims APIs
- orchestration client
- customer-service once implemented

**Definition of done**:

E2E suite runs in CI or scheduled CI and blocks regressions in regulated workflows.

### P0.5 Documentation enforcement and stale-doc cleanup

**Current state**: required docs exist and CI enforces required metadata inline. Some older docs may still contain stale implementation statements.

**Target outcome**: documentation validation is strict, standalone, and aligned with the current implementation state.

**Implementation steps**:

1. Restore or replace `scripts/validate_docs.py` with strict required-doc validation.
2. Ensure required docs include `Owner`, `Audience`, `Last reviewed`, and `Status`.
3. Add stale-doc classifications to `docs/10_markdown_cleanup_register.md`.
4. Remove or mark stale phrases from older docs.
5. Add docs update requirement to PR template.

**Deliverables**:

- strict standalone docs validator
- updated cleanup register
- no untracked stale required docs

**Acceptance criteria**:

- missing required docs fail CI;
- missing headers fail CI;
- stale phrases are warnings or explicit failures depending on flag;
- docs index points to current source of truth.

**Required tests**:

- CI validation step;
- optional unit tests for validator.

**Dependencies**:

- current docs index and PR template

**Definition of done**:

Documentation requirements cannot be bypassed by changing CI expectations instead of satisfying the docs.

## P1 — Complete MVP operations

### P1.1 Policy administration lifecycle

**Current state**: policy-service supports bind requests, approvals, and issued policy records. It does not support endorsements, cancellations, reinstatements, renewals, or full policy lifecycle timelines.

**Target outcome**: policy-service manages post-bind policy administration workflows with human approval and audit history.

**Implementation steps**:

1. Add ORM models: `PolicyChangeRequest`, `EndorsementRecord`, `CancellationRecord`, `ReinstatementRecord`, `RenewalRecord`, `PolicyLifecycleEventRecord`.
2. Add endpoints:
   - `POST /policies/{policy_id}/endorsements`
   - `POST /policies/{policy_id}/cancellations`
   - `POST /policies/{policy_id}/reinstatements`
   - `POST /policies/{policy_id}/renewals`
   - `GET /policies/{policy_id}/timeline`
3. Add approval workflow for material changes.
4. Add document packet hooks for endorsements/cancellations/renewals.
5. Add event outbox events for all lifecycle transitions.

**Deliverables**:

- policy admin models and migration
- API endpoints
- approval workflow
- lifecycle timeline
- tests and docs

**Acceptance criteria**:

- all lifecycle changes preserve tenant/customer ownership;
- material changes require underwriter/admin approval;
- timeline shows bind, endorsement, cancellation, reinstatement, and renewal events;
- duplicate lifecycle requests are idempotent when request key is provided.

**Required tests**:

- endorsement creation and approval;
- cancellation creation and approval;
- renewal creation;
- cross-customer denial;
- timeline ordering.

**Dependencies**:

- policy-service
- document-service P1.2
- customer-service P0.1

**Definition of done**:

Policy-service can administer a policy after initial bind with auditable lifecycle records.

### P1.2 Document service

**Current state**: `packages/documents` provides plain-text scaffolds for policy packets and adverse-action notices. There is no service for template storage, review, rendering, approval, or delivery audit.

**Target outcome**: document-service manages versioned templates and controlled document generation.

**Implementation steps**:

1. Create `services/document-service`.
2. Add models: `TemplateRecord`, `TemplateVersionRecord`, `DocumentDraftRecord`, `DocumentApprovalRecord`, `DocumentDeliveryRecord`.
3. Add template APIs for upload, version, review, approve, retire.
4. Add render APIs for policy packet, endorsement, cancellation, renewal, adverse action, claim denial notice.
5. Add draft/review/approved statuses.
6. Add PDF generation interface with HTML/text fallback.
7. Add delivery audit interface without enabling unreviewed delivery.

**Deliverables**:

- document-service package
- template version storage
- draft generation APIs
- approval workflow
- migration and tests

**Acceptance criteria**:

- no generated draft is marked deliverable until template version is approved;
- every document has template version, jurisdiction, product, actor, and timestamp;
- adverse-action and denial drafts include reason codes;
- document events are emitted.

**Required tests**:

- template version lifecycle;
- render policy packet draft;
- render adverse-action draft;
- block delivery of unapproved template;
- cross-tenant document access denial.

**Dependencies**:

- packages/documents
- policy-service
- claims-service
- compliance review process

**Definition of done**:

Document generation becomes auditable and template-version controlled.

### P1.3 Event broker adapter

**Current state**: `packages/events` has publisher abstraction and stdout/JSONL publishers. Service outbox tables exist.

**Target outcome**: event publishing is broker-backed, retryable, idempotent, and observable.

**Implementation steps**:

1. Add broker publisher adapters for Kafka, SNS, or Pub/Sub.
2. Add event schema envelope: event ID, aggregate ID, type, version, tenant ID, actor ID, correlation ID, payload hash.
3. Add outbox worker service or script with polling, publish, mark-published, retry count, and dead-letter state.
4. Add idempotency handling for duplicate publish attempts.
5. Add event schema registry docs.
6. Add redaction pass before publish.

**Deliverables**:

- broker adapter
- outbox worker
- event schema definitions
- dead-letter handling
- tests

**Acceptance criteria**:

- quote/policy/claims/customer events publish exactly once from outbox perspective;
- failed publishes are retried and eventually dead-lettered;
- PII-sensitive fields are redacted where required;
- event publish status is auditable.

**Required tests**:

- JSONL/stdout tests remain;
- broker adapter mock tests;
- retry/dead-letter tests;
- redaction tests;
- idempotent publish tests.

**Dependencies**:

- packages/events
- outbox tables in services
- observability package

**Definition of done**:

Local and CI can test publish logic without external broker, and production can configure a broker adapter.

### P1.4 OpenTelemetry and production logging

**Current state**: correlation ID middleware and redaction helpers exist. There is no full OpenTelemetry exporter or structured JSON logging configuration.

**Target outcome**: every service emits structured logs, metrics, and distributed traces with correlation IDs and PII redaction.

**Implementation steps**:

1. Add `insurance_observability.logging` JSON logging config.
2. Add OpenTelemetry FastAPI instrumentation helper.
3. Add trace propagation to orchestration client.
4. Add metrics endpoint or Prometheus instrumentation.
5. Add log redaction middleware/helper for request/response/event payloads.
6. Add service name/version/environment fields.

**Deliverables**:

- JSON logging setup
- OpenTelemetry helper
- metrics integration
- trace propagation
- tests and docs

**Acceptance criteria**:

- all service responses include `X-Request-ID`;
- logs include request ID, service, route, status, duration;
- sensitive fields are redacted;
- orchestration calls propagate trace/request context.

**Required tests**:

- middleware request ID test;
- redaction test;
- trace header propagation test;
- logging config smoke test.

**Dependencies**:

- packages/observability
- orchestration client

**Definition of done**:

Operators can correlate a customer workflow across services without exposing PII.

### P1.5 Claims coverage and payments

**Current state**: claims-service supports FNOL, claim list/detail, evidence metadata, reserve recommendation/approval, denial review, and adverse-action draft.

**Target outcome**: claims-service supports coverage checks, assignment, SLA, payment recommendations, payment approvals, and fraud/litigation routing.

**Implementation steps**:

1. Add policy-service coverage check adapter.
2. Add `ClaimCoverageReviewRecord`.
3. Add claim assignment fields and endpoints.
4. Add SLA timers and queue aging.
5. Add `ClaimPaymentRecommendationRecord` and approval workflow.
6. Add evidence storage adapter interface.
7. Add fraud/litigation referral states.

**Deliverables**:

- coverage check endpoint/client
- assignment workflow
- SLA fields and queries
- payment recommendation/approval workflow
- evidence storage abstraction
- tests

**Acceptance criteria**:

- claim cannot proceed to payment without coverage review;
- payment approval requires Claims Manager;
- denied claims require denial-review workflow;
- evidence records are immutable except classification/visibility changes;
- fraud/litigation referrals route to dedicated queues.

**Required tests**:

- coverage in force positive/negative;
- payment recommendation and manager approval;
- customer isolation;
- SLA queue filters;
- fraud referral routing.

**Dependencies**:

- claims-service
- policy-service
- document-service P1.2

**Definition of done**:

Claims can progress from FNOL through coverage review and manager-approved payment/denial decision.

### P1.6 Risk and underwriting operations

**Current state**: risk-service supports policy lifecycle and assessment persistence. There is no dedicated underwriting queue or operational dashboard data.

**Target outcome**: underwriting has queue-based workflows for referrals, appetite utilization, concentration, decline review, and adverse-action drafts.

**Implementation steps**:

1. Add underwriting referral records.
2. Add referral queue endpoints.
3. Add appetite utilization query APIs.
4. Add portfolio concentration snapshots.
5. Add decline review workflow.
6. Add adverse-action draft integration with document-service.

**Deliverables**:

- referral queue models/API
- appetite utilization API
- concentration report API
- decline review workflow
- tests

**Acceptance criteria**:

- referred risks enter underwriting queue;
- underwriter can approve, decline, or request more information;
- decline generates draft adverse-action notice;
- appetite dashboard can show active limits and utilization.

**Required tests**:

- referral creation;
- queue filtering;
- decline approval human gate;
- adverse-action draft creation;
- ownership and role enforcement.

**Dependencies**:

- risk-service
- quote-service
- document-service P1.2
- UI P0.2

**Definition of done**:

Underwriting has an operational queue instead of isolated risk assessment records.

## P2 — Scale, capital operations, and blockchain-backed audit

### P2.1 Blockchain gateway

**Current state**: blockchain-first design exists. No deployable blockchain-gateway service or contracts are currently implemented.

**Target outcome**: a gateway commits non-PII hashes/proofs for selected material events to local chain first, then production chain later after security review.

**Implementation steps**:

1. Create `services/blockchain-gateway`.
2. Add Hardhat/Foundry workspace.
3. Implement `PolicyRegistry` and `AuditEventRegistry` contracts.
4. Add commitment envelope format.
5. Add signer approval workflow.
6. Add local Anvil deployment.
7. Add reconciliation report comparing DB events to chain commitments.
8. Add security review checklist and test coverage.

**Deliverables**:

- contracts
- gateway API
- local chain compose profile
- commitment writer
- reconciliation script
- signer approval workflow

**Acceptance criteria**:

- no PII can be written to chain;
- commitment hash can be traced to off-chain event;
- admin actions require smart-contract signer role;
- reconciliation identifies missing or mismatched commitments.

**Required tests**:

- contract unit tests;
- no-PII commitment payload tests;
- signer role enforcement;
- reconciliation tests.

**Dependencies**:

- events package
- policy/claims/quote outbox events
- security roles

**Definition of done**:

Local blockchain proof workflow is usable and safe for non-PII audit commitments.

### P2.2 Treasury and float service

**Current state**: treasury/float service is not implemented.

**Target outcome**: premium allocation, reserves, liquidity, counterparty limits, and investment policy controls are auditable and human-approved.

**Implementation steps**:

1. Create `services/treasury-service`.
2. Add models for premium allocation, reserve snapshot, liquidity bucket, counterparty, IPS rule, treasury approval.
3. Add APIs for allocation proposals, reserve snapshots, liquidity reports, counterparty exposure, and approvals.
4. Add rule engine for IPS constraints.
5. Add event outbox and audit trail.

**Deliverables**:

- treasury-service package
- models/migrations/API
- approval workflow
- IPS rules
- tests

**Acceptance criteria**:

- no treasury action executes without Treasury Approver;
- proposed allocation shows reserve/liquidity impact;
- counterparty limits are enforced;
- all actions emit audit events.

**Required tests**:

- premium allocation proposal;
- approval required;
- counterparty limit violation;
- liquidity threshold violation;
- event emission.

**Dependencies**:

- policy-service premium events
- claims reserve data
- security roles

**Definition of done**:

Treasury has a controlled, auditable workflow for premium and float actions.

### P2.3 Billing and payments

**Current state**: billing/payment is not implemented.

**Target outcome**: policies can generate invoices, payments can be recorded/reconciled, and refunds/cancellations can be handled.

**Implementation steps**:

1. Create `services/billing-service`.
2. Add invoice schedule, invoice, payment, refund, delinquency, reconciliation models.
3. Add payment provider abstraction.
4. Add APIs for invoice creation, payment recording, refund request, and reconciliation.
5. Add cancellation/delinquency workflow integration with policy-service.

**Deliverables**:

- billing-service package
- payment provider interface
- invoice/payment models
- reconciliation reports
- tests

**Acceptance criteria**:

- policy can generate invoice schedule;
- payment events update invoice status;
- refund requires approval;
- delinquency can trigger policy workflow;
- reconciliation report identifies mismatches.

**Required tests**:

- invoice generation;
- payment recording;
- refund approval;
- delinquency status;
- reconciliation mismatch.

**Dependencies**:

- policy-service
- treasury-service P2.2
- event broker P1.3

**Definition of done**:

Billing can support real premium collection workflows behind provider abstraction.

### P2.4 Customer communications

**Current state**: secure messages are a UI/design target. There is no message-service.

**Target outcome**: customer/staff communications are template-controlled, auditable, and delivery-tracked.

**Implementation steps**:

1. Create `services/message-service`.
2. Add secure inbox models.
3. Add outbound provider abstraction for email/SMS.
4. Add message template version support or integrate with document-service.
5. Add delivery status tracking.
6. Add opt-out/compliance preferences.

**Deliverables**:

- message-service package
- secure inbox APIs
- outbound provider abstraction
- delivery status/audit trail
- tests

**Acceptance criteria**:

- customer can view secure messages;
- staff can send approved templates;
- delivery status is tracked;
- opt-out/compliance preferences are respected;
- messages are tenant/customer scoped.

**Required tests**:

- message creation;
- customer inbox scoping;
- outbound provider mock;
- delivery status update;
- opt-out enforcement.

**Dependencies**:

- document-service P1.2
- customer-service P0.1
- UI P0.2

**Definition of done**:

Customer communication is auditable and compliant with template/consent controls.

## P3 — Intelligence, analytics, and platform expansion

### P3.1 Advanced AI assistant

**Current state**: AI authority model is documented, but no assistant service/tool registry exists.

**Target outcome**: AI assists customers and staff while enforcing tool permissions and human approval boundaries.

**Implementation steps**:

1. Create AI orchestrator service.
2. Add tool registry and permission policy.
3. Add retrieval over operating docs and workflow records.
4. Add assistants for customer support, underwriting support, claims summarization, and compliance draft review.
5. Add audit log of AI tool calls and citations/evidence spans.

**Deliverables**:

- AI orchestrator service
- tool registry
- retrieval index
- audited tool calls
- assistant-specific prompts/workflows

**Acceptance criteria**:

- AI cannot call restricted tools without approval;
- every AI output labels itself as draft/suggestion;
- AI summaries cite source records;
- all tool calls are audited.

**Required tests**:

- restricted tool denial;
- allowed tool success;
- approval-required flow;
- evidence citation test.

**Dependencies**:

- service APIs
- docs index
- security roles
- event/audit system

**Definition of done**:

AI can help with workflows but cannot execute regulated decisions.

### P3.2 Analytics and reporting

**Current state**: no analytics/reporting service exists.

**Target outcome**: operational and insurance performance metrics are available to staff and leadership.

**Implementation steps**:

1. Create reporting data mart or analytics service.
2. Add event ingestion from broker/outbox.
3. Add quote conversion, bind rate, referral rate, claim severity, reserve adequacy, and loss ratio reports.
4. Add dashboard APIs.
5. Add export controls.

**Deliverables**:

- analytics/reporting service
- metric definitions
- dashboard APIs
- exports
- tests

**Acceptance criteria**:

- quote conversion metrics match source records;
- claim severity metrics match claims data;
- loss ratio calculations are reproducible;
- exports are role-gated.

**Required tests**:

- metric calculation tests;
- role-gated export tests;
- event ingestion tests.

**Dependencies**:

- event broker P1.3
- billing/claims/policy data

**Definition of done**:

Core operational reports are reproducible and available to authorized users.

### P3.3 Multi-product expansion

**Current state**: sample personal auto product exists as architecture test data.

**Target outcome**: the platform supports multiple products, jurisdictions, and versioned rate/rule/form sets.

**Implementation steps**:

1. Create product registry service or extend rating/product package.
2. Add product lifecycle states: draft, review, approved, active, retired.
3. Add jurisdiction configuration.
4. Add rate/rule/form set linking.
5. Add product approval workflow.
6. Add UI management screens.

**Deliverables**:

- product registry
- product lifecycle models/API
- jurisdiction config
- rate/rule/form version linking
- tests

**Acceptance criteria**:

- quote-service can select active product version by jurisdiction;
- inactive product versions cannot be used for new quotes;
- product changes require approval;
- product/version history is auditable.

**Required tests**:

- product version selection;
- inactive product rejection;
- approval workflow;
- jurisdiction-specific config test.

**Dependencies**:

- rating DSL
- document-service
- policy admin lifecycle

**Definition of done**:

The system can support more than one product and jurisdiction safely.

## Recommended delivery sequence

1. **P0.1 Customer/account service** — establishes source of truth for ownership.
2. **P0.2 UI foundation** — makes workflows usable and exposes approval controls.
3. **P0.4 End-to-end workflow tests** — prevents regressions across services.
4. **P0.3 Real IdP readiness** — finalizes production auth mode.
5. **P1.2 Document service** — makes regulated documents controlled and auditable.
6. **P1.1 Policy administration lifecycle** — extends beyond initial bind.
7. **P1.3 Event broker adapter** — turns outbox into production eventing.
8. **P1.5 Claims coverage and payments** — completes claims MVP.
9. **P2.2 Treasury and float service** — supports capital operations.
10. **P2.1 Blockchain gateway** — adds cryptographic audit commitments once event model is stable.

## Definition of production readiness

The system should not be called production-ready until:

- customer/account ownership is centralized;
- UI supports complete staff/customer workflows;
- JWT/JWKS production auth is mandatory and fixture-tested;
- Postgres migrations are managed through Alembic;
- broker-backed event publishing exists;
- legal-approved templates exist;
- policy administration supports endorsements/cancellations/renewals;
- claims coverage and payments are implemented;
- treasury and capital controls exist;
- blockchain commitments are PII-safe and reconciled;
- full e2e tests pass;
- security/compliance review is complete.
