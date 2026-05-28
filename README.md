# Insurance Operating System — Architecture Prototype

## Status

**Phase**: Architecture Foundation (Phase 0)
**Version**: 2026.05.27
**Last Updated**: 2026-05-27

## What This Is

An architecture prototype for an MGA-style insurance operating system. It defines the design, governance, and implementation plan for a platform that combines deterministic rating, AI-assisted workflows, blockchain audit commitment, and treasury management.

## What This Is NOT

- NOT a real filed insurance product
- NOT a regulatory filing
- NOT a production system
- NOT a business plan
- NOT a financial product

All values in this repository are architecture test data.

## Decisions Made (2026-05-26)

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
- **Customer wallet**: Wallet abstraction (customers don't see blockchain)

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

```
auto-insurance/
  docs/                          # Architecture documentation
    01_vision.md                 # Vision and scope
    02_architecture.md           # System architecture
    03_execution_plan.md         # Revised execution plan (updated 2026-05-26)
    04_product_strategy.md       # Product strategy (updated 2026-05-26)
    05_risk_appetite.md          # Risk appetite framework
    06_quote_engine.md           # Quote engine design
    07_policy_admin.md           # Policy administration
    08_claims.md                 # Claims management
    09_blockchain.md             # Blockchain strategy
    10_treasury.md               # Treasury governance
    11_data_model.md             # Data model
    12_event_model.md            # Event model
    13_ai_agent_architecture.md  # AI agent architecture
    14_api_contracts.md          # API contracts
    15_compliance_controls.md    # Compliance controls
    16_testing_strategy.md       # Testing strategy
    17_open_questions.md         # Open questions (RESOLVED 2026-05-26)
    README.md                    # Documentation index
  governance/                    # Governance policies
    risk_appetite_policy.yml     # Risk appetite policy (updated 2026-05-26)
    treasury_policy.yml          # Treasury policy (updated 2026-05-26)
    ai_tools.yml                 # AI tool interface (updated 2026-05-26)
    product_approval_matrix.yml  # Product approval matrix (updated 2026-05-26)
    adverse_action_reason_codes.yml  # Adverse action codes
    ai_model_inventory.yml       # AI model inventory
  data/                          # Product data
    sample-products/             # Sample product configs (created 2026-05-26)
      sample_personal_auto_v1.yml  # Sample personal auto (created 2026-05-26)
  packages/                      # Shared packages
    rating-dsl/                  # Rating DSL (created 2026-05-26)
      README.md                  # DSL syntax and example
      schema/
        rating-dsl-schema.json   # JSON Schema for validation
    shared-types/                # Shared types (created 2026-05-26)
      README.md                  # Core types: Party, Product, Quote, Risk, Policy, Claim, Event
    event-schemas/               # Event schemas (created 2026-05-26)
      README.md                  # All domain event types
  services/                      # Service implementations (future)
  infra/                         # Infrastructure
    README.md                    # Docker Compose local dev (updated 2026-05-26)
  tests/                         # Test suites (future)
  docs/                          # Additional docs
    README.md                    # Docs index
  IMPLEMENTATION.md              # Implementation roadmap (future)
  README.md                      # This file
```

## Execution Plan

See docs/03_execution_plan.md for the detailed 8-milestone plan.

### Milestone 1: Shared Foundation (Current)
- Rating DSL defined with syntax, schema, and example
- Sample product config created
- AI tool interface and authority model defined
- Shared-types core types defined
- Event schemas defined for all domains
- Governance YAMLs updated
- Open questions resolved
- Product strategy updated
- Infrastructure defined

### Milestone 2: Quote Service MVP (COMPLETED 2026-05-27)
- Quote service with deterministic rating engine
- Integration with rating DSL evaluator
- Integration with risk appetite evaluation
- Explainability reports (JSON + text)
- Quote expiration handler
- In-memory quote store
- FastAPI application with full CRUD
- Comprehensive test suite

### Milestone 3: Risk Appetite Service MVP (COMPLETED 2026-05-27)
- YAML policy loader
- Risk evaluation endpoint
- Exposure summary endpoint
- Capital/reserve impact estimation
- Reinsurance capacity checks
- Dynamic policy updates
- Comprehensive test suite

### Milestone 4: Policy Service MVP
- Bind flow with audit packet
- Policy lifecycle state machine
- Human approval workflow

### Milestone 5: Blockchain Gateway MVP
- PolicyRegistry + AuditEventRegistry contracts
- Local Anvil deployment
- Policy commitment flow

### Milestone 6: AI Agent Orchestrator MVP
- Session management
- Tool permission enforcement
- AI service integration

### Milestone 7: Claims Service MVP
- FNOL intake
- Coverage check

### Milestone 8: Treasury Service MVP
- Premium allocation stub
- Reserve snapshot stub

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

1. AI cannot modify rating logic
2. AI cannot bind policies (prepares bind request only)
3. AI cannot decline risks (refers to underwriter only)
4. AI cannot deny claims (summarizes FNOL only)
5. AI cannot execute treasury actions
6. AI cannot modify governance policies
7. AI cannot approve products
8. All AI tool calls are audited

## Rating DSL

The rating DSL defines deterministic, versioned, testable rating logic. See `packages/rating-dsl/README.md` for full syntax and example.

### Key Principles

1. Rating is deterministic: same inputs + same version = same output
2. Rating is versioned: every change creates a new version
3. Rating is auditable: every factor is stored with the quote
4. Rating is testable: every configuration can be validated with tests
5. Rating is explainable: every output includes factor breakdown

## Blockchain Strategy

### MVP Scope

- Local Anvil EVM only
- PolicyRegistry contract (hash commitments)
- AuditEventRegistry contract (event log)
- Policy commitments on bind
- Policy endorsements on endorsement
- Policy cancellations on cancel

### Future Scope (Phase 4+)

- PremiumEscrow contract
- ClaimsEscrow contract
- ReserveAttestation contract
- TreasuryPolicy contract
- GovernanceMultisig contract
- OracleRegistry contract
- Public chain deployment

### Privacy

- Customer data is NEVER stored on-chain
- Only policy_id, commitment_hash, status, committed_at are on-chain
- Customer name, address, driver license, VIN, documents, evidence are off-chain
- Blockchain commitments provide auditability, not customer data

## AI Agent Architecture

### Tool Interface

See `governance/ai_tools.yml` for the complete tool interface and permissions.

### Authority Model

- **Allowed by default**: 11 tools (collect_intake, explain_product, explain_quote, etc.)
- **Restricted by default**: 8 tools (execute_bind, execute_decline, etc.)
- All restricted tools require specific approval roles
- All tool calls are audited with full input/output snapshots

### AI Model

- Model provider: TBD
- Model name: TBD
- Model version: TBD
- Status: not_deployed

## Compliance Controls

10 control families:
1. product_governance
2. quote_reproducibility
3. risk_appetite
4. policy_authority
5. claims_authority
6. ai_governance
7. treasury_governance
8. blockchain_privacy
9. auditability
10. security_access

See docs/15_compliance_controls.md for detailed control specifications.

## Testing Strategy

See docs/16_testing_strategy.md for the complete testing strategy.

### Test Categories

- unit
- integration
- e2e
- contract
- security
- compliance
- model-eval
- load
- reconciliation

### MVP Testing Requirements

- Rating factor calculations must be tested with every rating change
- Quote eligibility rules must be tested with every eligibility change
- Quote expiration rules must be tested with every expiration change
- Risk appetite decisions must be tested with every policy change
- Policy lifecycle transitions must be tested with every transition change
- Premium allocation math must be tested with every allocation change
- Reserve snapshot hashing must be tested with every snapshot change
- Treasury policy evaluation must be tested with every policy change
- Event schema validation must be tested with every schema change

## Open Questions

All open questions have been resolved. See docs/17_open_questions.md for the complete resolution log.

## Contributing

This is an architecture prototype. Contributions welcome for:
- Architecture documentation improvements
- Rating DSL syntax improvements
- Shared types improvements
- Event schema improvements
- Governance policy improvements
- Implementation code (after architecture is approved)

## License

Architecture prototype. See LICENSE file for terms.
