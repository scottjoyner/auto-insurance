# Insurance Operating System — Architecture Prototype

## Status

**Phase**: P0 implementation hardening started  
**Version**: 2026.05.29  
**Last Updated**: 2026-05-29

## What This Is

An architecture prototype for an MGA-style insurance operating system. It defines the design, governance, and implementation plan for a platform that combines deterministic rating, AI-assisted workflows, blockchain audit commitment, and treasury management.

## What This Is NOT

- NOT a real filed insurance product
- NOT a regulatory filing
- NOT a production system
- NOT a business plan
- NOT a financial product

All values in this repository are architecture test data.

## Current State

See `docs/00_current_state_assessment.md` for the implementation-cycle assessment and prioritized P0/P1/P2 plan.

The repository now includes the beginning of a P0 implementation pass:

- Shared `packages/security` FastAPI RBAC scaffold for development-only actor context.
- Quote service CORS hardening and protected business endpoints.
- Rating engine fix for `base_rates` lookup and unknown coverage-tier handling.
- Root `docker-compose.yml` baseline for local service orchestration.
- `.env.example` for local development settings.
- Expanded `SECURITY.md` with non-production constraints and required production hardening.

## Decisions Made

### Product
- **Product**: Sample personal auto insurance
- **Status**: `architecture_sample_only`
- **Jurisdiction**: SAMPLE (modeled on NC regulations)
- **Target**: Architecture prototype / MGA-style operating layer

### Service Stack
- **Language**: Python 3.12+, FastAPI, SQLAlchemy, Pydantic v2
- **Blockchain gateway**: TypeScript, ethers.js, Hardhat
- **Testing**: pytest, hypothesis, pytest-asyncio
- **Docker**: docker-compose for local dev

### Blockchain
- **MVP**: Local Anvil only (no public chain)
- **Contracts**: PolicyRegistry + AuditEventRegistry only for MVP
- **Policy representation**: Registry records (not NFTs)
- **Customer wallet**: Wallet abstraction (customers do not see blockchain)

### AI Authority
- **Allowed**: collect_intake, explain_product, explain_quote, prepare_quote_request, route_to_human_review, draft_customer_communication
- **Restricted (requires human approval)**: execute_bind, execute_decline, execute_claim_decision, execute_treasury_action, modify_rating_logic, approve_product, modify_governance_policy, execute_smart_contract_admin
- **AI can bind**: NO — AI prepares bind requests only, human approval required

### Rating
- **Approach**: Deterministic rule-based via YAML rating DSL
- **ML-based**: Phase 4+ scope

### MVP Scope
- **Payment**: Fiat only, stubbed
- **Customer channel**: HTTP API (web chat) only
- **Third-party data**: None (all inputs self-reported)
- **Claims**: FNOL intake + coverage check only

## Directory Structure

```text
auto-insurance/
  docs/
    00_current_state_assessment.md
    01_vision.md
    02_architecture.md
    03_execution_plan.md
    ...
  governance/
  data/
    sample-products/
  packages/
    rating-dsl/
    security/
    shared-types/
    event-schemas/
  services/
    quote-service/
    risk-appetite-service/
  infra/
  docker-compose.yml
  .env.example
  SECURITY.md
  README.md
```

## Execution Plan

See `docs/03_execution_plan.md` and `docs/00_current_state_assessment.md` for the detailed implementation plan.

### Milestone 1: Shared Foundation
- Rating DSL defined with syntax, schema, and sample product.
- AI tool interface and authority model defined.
- Shared-types and event-schema documentation drafted.
- P0 security scaffold started.

### Milestone 2: Quote Service MVP — Partial / not complete
- Draft FastAPI quote generation endpoint exists.
- Quote explain and quote health lookup still need durable persistence.
- Recalculation is protected but still needs stored quote lookup for real deltas.
- P1.1 must implement Postgres persistence, quote versioning, event outbox, and complete API behavior.

### Milestone 3: Risk Appetite Service MVP — Partial / not complete
- Draft risk assessment endpoint exists.
- Runtime policy update must remain disabled by default until a versioned approval workflow exists.
- P1.2 must implement persisted risk assessments and versioned risk policy approval.

### Milestone 4: Policy Service MVP
- Bind flow with audit packet.
- Policy lifecycle state machine.
- Human approval workflow.

### Milestone 5: Blockchain Gateway MVP
- PolicyRegistry + AuditEventRegistry contracts.
- Local Anvil deployment.
- Policy commitment flow.

### Milestone 6: AI Agent Orchestrator MVP
- Session management.
- Tool permission enforcement.
- AI service integration.

### Milestone 7: Claims Service MVP
- FNOL intake.
- Coverage check.

### Milestone 8: Treasury Service MVP
- Premium allocation stub.
- Reserve snapshot stub.

## Key Governance Decisions

### Who Can Do What

| Action | AI Agent | Underwriter | Claims Manager | Treasury Approver | Smart Contract Signer |
|---|---|---|---|---|---|
| Collect intake | YES | YES | NO | NO | NO |
| Explain product | YES | YES | NO | NO | NO |
| Generate quote | YES (via service) | YES (via service) | NO | NO | NO |
| Evaluate risk | YES (via service) | YES (via service) | NO | NO | NO |
| Approve bind | NO (prepares only) | YES | NO | NO | NO |
| Decline risk | NO (refers only) | YES | NO | NO | NO |
| Approve claim | NO (summarizes only) | NO | YES | NO | NO |
| Allocate premium | NO | NO | NO | YES | NO |
| Deploy contracts | NO | NO | NO | NO | YES |
| Modify rating | NO | NO | NO | NO | NO |
| Approve product | NO | NO | NO | NO | NO |

### AI Agent Restrictions

1. AI cannot modify rating logic.
2. AI cannot bind policies.
3. AI cannot decline risks.
4. AI cannot deny claims.
5. AI cannot execute treasury actions.
6. AI cannot modify governance policies.
7. AI cannot approve products.
8. All AI tool calls must be audited.

## Rating DSL

The rating DSL defines deterministic, versioned, testable rating logic. See `packages/rating-dsl/README.md` for full syntax and example.

### Key Principles

1. Rating is deterministic: same inputs + same version = same output.
2. Rating is versioned: every change creates a new version.
3. Rating is auditable: every factor is stored with the quote.
4. Rating is testable: every configuration can be validated with tests.
5. Rating is explainable: every output includes factor breakdown.
