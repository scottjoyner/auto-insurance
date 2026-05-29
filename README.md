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
| Quote service | Implemented foundation | Quote generation, persistence, explainability, acceptance, ownership enforcement, lifecycle records. |
| Risk appetite service | Implemented foundation | Risk assessments, policy version lifecycle, activation guardrails, persisted assessments. |
| Policy service | Implemented foundation | Bind requests, approval workflow, idempotency, compliance guard, issued policy records, ownership enforcement. |
| Claims service | Implemented foundation | FNOL, claim ownership, evidence metadata, reserve approval, denial review, adverse-action draft. |
| Events | Implemented scaffold | Outbox records and publisher abstraction; production broker adapter still needed. |
| Documents | Implemented scaffold | Policy packet and adverse-action draft renderers; legal templates still needed. |
| Observability | Implemented scaffold | Correlation IDs and redaction helpers; OpenTelemetry exporter still needed. |
| Database | Implemented foundation | SQL migrations, Alembic scaffolds, SQLite local mode, Postgres CI scaffold. |
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
    quote-service/          Quote generation, persistence, explainability, accept
    risk-appetite-service/  Risk policy lifecycle and assessments
    policy-service/         Bind request, approval, policy issuance
    claims-service/         FNOL, evidence, reserves, denial-review workflow
  docs/                     Architecture, operating guides, gap registers, PR plans
  scripts/                  Migration and outbox utilities
  docker-compose.yml        Local stack
```

## Local development

Copy local env values:

```bash
cp .env.example .env
```

Run the stack:

```bash
docker compose build
docker compose up
```

Default local service ports:

| Service | Port |
|---|---:|
| quote-service | 8001 |
| risk-appetite-service | 8002 |
| policy-service | 8003 |
| claims-service | 8004 |
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

## Core workflow vision

### Quote to policy

1. Customer or agent creates an intake.
2. Quote service generates deterministic quote from versioned rating rules.
3. Risk service evaluates quote against active risk appetite policy.
4. Policy service creates bind request from quote/risk snapshots.
5. Human underwriter approves bind.
6. Policy service issues active policy record.
7. Policy packet draft is generated from approved templates.
8. Event outbox publishes lifecycle events.
9. Blockchain gateway commits approved policy/audit hashes only, never PII.

### Claims

1. Customer, agent, or claims staff creates FNOL.
2. Claim ownership is stamped from tenant/customer context.
3. Claim is triaged into queue and severity.
4. Evidence metadata is collected with checksum/source/visibility.
5. Adjuster recommends reserves.
6. Claims Manager approves reserves and denial review.
7. Denial review generates adverse-action/claim denial draft only.
8. Approved communication uses legally reviewed templates.
9. Event outbox records material claim transitions.

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
- quote/risk/policy/claims repository and API tests;
- SQL migration baselines;
- compose configuration;
- Postgres integration scaffold.

## Current high-priority gaps

1. Full customer/account service as ownership source of truth.
2. UI applications and design-system implementation.
3. Real event broker adapter and dead-letter handling.
4. Production OpenTelemetry exporter.
5. Legal-approved document templates.
6. Blockchain gateway implementation.
7. Treasury/float service implementation.
8. Policy admin lifecycle beyond initial bind.
9. End-to-end integration tests across quote, risk, policy, claims, events, and documents.
10. Production-grade deployment manifests, secret management, and operational runbooks.

## Documentation map

- `docs/00_documentation_index.md` — documentation entry point.
- `docs/05_production_gap_closure.md` — production hardening status.
- `docs/07_employee_operating_manual.md` — employee operating procedures.
- `docs/08_claims_crm_operating_guide.md` — claims CRM target workflow.
- `docs/11_next_pr_review_plan.md` — PR review sequence.
- `docs/12_production_ui_design.md` — production UI design target.
- `docs/13_remaining_gap_register.md` — remaining implementation gap register.
