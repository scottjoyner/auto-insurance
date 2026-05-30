# Auto Insurance Operating System

Owner: Platform Engineering  
Audience: engineering, product, compliance, operations, security  
Last reviewed: 2026-05-29  
Status: active production-grade architecture and implementation guide

## Vision

This repository is the foundation for a production-grade insurance operating system. The goal is to support the complete lifecycle of a regulated insurance business: customer/account management, quote, risk appetite, underwriting, bind, policy administration, claims, compliance communications, event audit, treasury/float controls, and blockchain-backed proof of critical commitments.

The system is blockchain-first, but not blockchain-only. Blockchain should provide cryptographic proof for commitments, state transitions, selected payment/audit events, and governance checkpoints. Regulated workflows, PII, customer evidence, actuarial models, rating logic, documents, and sensitive records remain off-chain in auditable service databases.

## Product guardrails

This repository is not a filed insurance product and must not be used to sell real policies without regulatory, actuarial, legal, compliance, and security review.

Production use requires:

- filed and jurisdiction-specific rates, rules, forms, notices, and endorsements;
- deterministic, versioned rating logic;
- human approval for bind, decline, claims denial, treasury, and smart-contract actions;
- solvency, reserve, liquidity, and risk-appetite gates;
- tenant/customer ownership enforcement on all customer data;
- PII redaction in logs, events, and external outputs;
- immutable audit trails for material decisions;
- legally reviewed policy forms and adverse-action templates;
- secure identity provider integration through JWT/JWKS;
- Postgres migrations and production secret management.

## Current implementation status

The repository now contains a local, testable multi-service foundation.

| Area | Status | Notes |
|---|---|---|
| Shared security | Implemented foundation | Dev tokens plus JWT/JWKS production path, RBAC, tenant/customer context. |
| Customer service | Implemented P0 foundation | Tenant, account, customer, contact, address, identity-link, scoped search, ownership checks. |
| Quote service | Implemented foundation | Quote generation, persistence, explainability, acceptance, ownership enforcement, optional customer-service validation. |
| Risk appetite service | Implemented foundation | Risk assessments, policy version lifecycle, activation guardrails, persisted assessments. |
| Policy service | Implemented foundation | Bind requests, approval workflow, idempotency, compliance guard, issued policy records, optional customer-service validation. |
| Claims service | Implemented foundation | FNOL, claim ownership, evidence metadata, reserve approval, denial review, adverse-action draft, optional customer-service validation. |
| Events | Implemented scaffold | Outbox records and publisher abstraction; production broker adapter still needed. |
| Documents | Implemented scaffold | Policy packet and adverse-action draft renderers; legal templates still needed. |
| Observability | Implemented scaffold | Correlation IDs and redaction helpers; OpenTelemetry exporter still needed. |
| Database | Implemented foundation | SQL migrations, Alembic scaffolds, SQLite local mode, Postgres CI scaffold. |
| E2E ownership tests | Implemented P0 starter | Customer -> quote -> bind -> policy -> claim ownership workflow is covered. |
| Blockchain | Design target | Registry/audit commitment design remains to be built out into deployable gateway. |
| Treasury/float | Design target | Needs reserve/liquidity/IPS/counterparty/approval implementation. |
| UI | Design gap | Needs production console, customer portal, agent desktop, claims workspace, and admin/security views. |

## Service map

```text
auto-insurance/
  packages/
    rating-dsl/             Deterministic rating DSL and golden tests
    security/               RBAC, dev auth, JWT/JWKS auth, ActorContext
    orchestration/          Quote -> risk -> bind workflow client
    events/                 Event publisher abstractions
    documents/              Policy packet and adverse-action draft renderers
    observability/          Correlation IDs and PII redaction
    secrets/                Secret-provider abstractions
  services/
    customer-service/       Tenant/account/customer ownership source of truth
    quote-service/          Quote generation, persistence, explainability, accept
    risk-appetite-service/  Risk policy lifecycle and assessments
    policy-service/         Bind request, approval, policy issuance
    claims-service/         FNOL, evidence, reserves, denial-review workflow
  tests/e2e/                Cross-service ownership workflow tests
  docs/                     Architecture, operating guides, gap registers, PR plans
  scripts/                  Migration and outbox utilities
  docker-compose.yml        Local stack
  docker-compose.customer.yml Optional customer-service compose override
```

## Local development

Copy local env values:

```bash
cp .env.example .env
```

Run the base stack:

```bash
docker compose build
docker compose up
```

Run with customer-service override:

```bash
docker compose -f docker-compose.yml -f docker-compose.customer.yml build customer-service
docker compose -f docker-compose.yml -f docker-compose.customer.yml up customer-service
```

Default local service ports:

| Service | Port |
|---|---:|
| quote-service | 8001 |
| risk-appetite-service | 8002 |
| policy-service | 8003 |
| claims-service | 8004 |
| customer-service | 8005 |
| postgres | 5432 |

## Authentication modes

Local development may use development bearer tokens:

```text
Bearer dev:<actor_id>:<ROLE>[,<ROLE>...]:<tenant_id>:<customer_id>
Bearer system:<actor_id>
```

Production should use JWT/JWKS:

```bash
INSURANCE_AUTH_MODE=jwt
INSURANCE_ALLOW_DEV_TOKENS=false
INSURANCE_JWT_ALGORITHM=RS256
INSURANCE_JWT_JWKS_URL=https://your-idp/.well-known/jwks.json
INSURANCE_JWT_ISSUER=https://your-idp/
INSURANCE_JWT_AUDIENCE=auto-insurance-api
```

Required claims:

- `sub`
- `roles`
- `tenant_id`
- `customer_id`

## Customer validation mode

Quote, policy, and claims services support optional customer-service validation. It is disabled by default for local development.

```bash
QUOTE_SERVICE_VALIDATE_CUSTOMER=false
POLICY_SERVICE_VALIDATE_CUSTOMER=false
CLAIMS_SERVICE_VALIDATE_CUSTOMER=false
```

When enabled, the services fail closed if the current actor's tenant/customer context cannot be validated by customer-service.

## Core workflow vision

### Quote to policy

1. Customer or agent creates an intake.
2. Quote service optionally validates tenant/customer ownership against customer-service.
3. Quote service generates deterministic quote from versioned rating rules.
4. Risk service evaluates quote against active risk appetite policy.
5. Policy service optionally validates tenant/customer ownership against customer-service.
6. Policy service creates bind request from quote/risk snapshots.
7. Human underwriter approves bind.
8. Policy service issues active policy record.
9. Policy packet draft is generated from approved templates.
10. Event outbox publishes lifecycle events.
11. Blockchain gateway commits approved policy/audit hashes only, never PII.

### Claims

1. Customer, agent, or claims staff creates FNOL.
2. Claims service optionally validates tenant/customer ownership against customer-service.
3. Claim ownership is stamped from tenant/customer context.
4. Claim is triaged into queue and severity.
5. Evidence metadata is collected with checksum/source/visibility.
6. Adjuster recommends reserves.
7. Claims Manager approves reserves and denial review.
8. Denial review generates adverse-action/claim denial draft only.
9. Approved communication uses legally reviewed templates.
10. Event outbox records material claim transitions.

### AI authority model

AI may assist with intake, explanations, summarization, routing, and draft communications. AI must not independently bind policies, decline risks, deny claims, modify rating logic, approve treasury actions, approve product/rate/form changes, or execute smart-contract administration.

## Production-grade system vision

A complete production implementation should include these user-facing applications:

- **Customer portal**: intake, quotes, policies, billing, documents, FNOL, claim status, secure messages.
- **Agent desktop**: customer search, quote workflow, underwriting referrals, bind request prep, document collection.
- **Underwriter console**: risk queue, appetite limits, quote/risk explainability, bind approvals, decline review.
- **Claims workspace**: FNOL, evidence, coverage review, reserves, manager approvals, denial review, communications.
- **Policy admin console**: endorsements, cancellations, reinstatements, renewals, forms, templates, audit timeline.
- **Treasury/float console**: premium allocation, reserves, liquidity ladder, IPS controls, counterparty limits, approvals.
- **Compliance console**: adverse-action notices, filings, template versions, audit exports, complaint tracking.
- **Security/admin console**: tenants, users, roles, IdP config, secrets status, service health, event replay.
- **Blockchain/audit console**: commitments, event hashes, registry state, signer approvals, chain health.

See `docs/12_production_ui_design.md` and `docs/13_remaining_gap_register.md` for the next implementation plan.

## CI and quality gates

Current CI validates:

- required documentation metadata;
- rating DSL golden tests;
- security tests;
- orchestration tests;
- events/documents/observability tests;
- quote/risk/policy/claims/customer API and repository tests;
- customer-validation tests for quote, policy, and claims;
- customer -> quote -> bind -> policy -> claim e2e ownership workflow;
- SQL migration baselines;
- Alembic baseline syntax;
- compose configuration;
- Postgres integration scaffold.

## Current high-priority gaps

1. UI applications and design-system implementation.
2. Full end-to-end workflow coverage beyond the first ownership path.
3. Real IdP RS256/JWKS fixture tests and production startup validation.
4. Real event broker adapter and dead-letter handling.
5. Production OpenTelemetry exporter.
6. Legal-approved document templates and document-service.
7. Blockchain gateway implementation.
8. Treasury/float service implementation.
9. Policy admin lifecycle beyond initial bind.
10. Production-grade deployment manifests, secret management, and operational runbooks.

## Documentation map

- `docs/00_documentation_index.md` — documentation entry point.
- `docs/05_production_gap_closure.md` — production hardening status.
- `docs/07_employee_operating_manual.md` — employee operating procedures.
- `docs/08_claims_crm_operating_guide.md` — claims CRM target workflow.
- `docs/11_next_pr_review_plan.md` — PR review sequence.
- `docs/12_production_ui_design.md` — production UI design target.
- `docs/13_remaining_gap_register.md` — remaining implementation gap register.
