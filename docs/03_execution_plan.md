# Execution Plan — Revised

## Goal

Move from architecture into a working implementation of the MVP quote-to-bind flow for the sample personal auto product.

## Decisions Made

- **Product**: Sample personal auto (architecture_sample_only)
- **Jurisdiction**: SAMPLE (modeled on NC regulations)
- **Service stack**: Python 3.12+, FastAPI, SQLAlchemy, Pydantic v2
- **Blockchain**: Local Anvil only for MVP. PolicyRegistry + AuditEventRegistry contracts only.
- **AI authority**: AI prepares bind requests only. Human approval required for all binds.
- **Rating**: Deterministic rule-based via YAML rating DSL. ML-based is Phase 4+.
- **Payment**: Fiat only. Stubbed payment processing for MVP.
- **Customer channel**: HTTP API (web chat) only for MVP.
- **Third-party data**: None for MVP. All inputs self-reported.

## Milestone 1: Shared Foundation (Current)

**Status**: In progress

**Completed**:
- Open questions resolved
- Rating DSL defined with syntax, schema, and example
- Sample product config created
- AI tool interface and authority model defined
- Shared-types core types defined (Party, Product, Quote, Risk, Policy, Claim, Event)
- Event schemas defined for all domains
- Risk appetite policy updated
- Product strategy updated

**Remaining**:
- Rating DSL parser implementation (packages/rating-dsl/src/parser.py)
- Rating DSL validator implementation (packages/rating-dsl/src/validator.py)
- Rating DSL evaluator implementation (packages/rating-dsl/src/evaluator.py)
- Shared-types Python implementation (packages/shared-types/src/shared_types/)
- Event schemas Python implementation (packages/event-schemas/src/event_schemas/)
- Product approval matrix update (governance/product_approval_matrix.yml)
- Treasury policy update (governance/treasury_policy.yml)

**Exit criteria**:
- Rating DSL validates against JSON Schema
- Rating DSL parser produces RatingPlan from YAML
- Rating DSL evaluator produces QuoteResult from RatingPlan + inputs
- Shared types validate via Pydantic
- Event schemas validate via Pydantic
- All tests pass

## Milestone 2: Quote Service MVP

**Status**: Not started

**Tasks**:
- Create quote-service skeleton (FastAPI app)
- Implement quote endpoint (POST /quotes)
- Integrate rating DSL evaluator
- Integrate risk appetite evaluation
- Implement quote retrieval endpoint (GET /quotes/{quote_id})
- Implement quote acceptance endpoint (POST /quotes/{quote_id}/accept)
- Add event emission for QuoteGenerated, QuoteAccepted
- Add audit logging
- Add comprehensive tests (unit, integration, regression)

**Exit criteria**:
- POST /quotes returns QuoteResult with full explainability
- GET /quotes/{quote_id} returns quote with status history
- POST /quotes/{quote_id}/accept transitions status to ACCEPTED
- All events emitted and validated
- All tests pass

## Milestone 3: Risk Appetite Service MVP

**Status**: Not started

**Tasks**:
- Create risk-appetite-service skeleton
- Implement YAML policy loader
- Implement risk evaluation endpoint (POST /risk-appetite/evaluate)
- Implement exposure summary endpoint (GET /risk-appetite/exposure-summary)
- Implement scenario endpoint (POST /risk-appetite/scenarios)
- Integrate with portfolio state (stubbed for MVP)
- Add event emission for RiskAppetiteEvaluated
- Add comprehensive tests

**Exit criteria**:
- Risk evaluation returns decision with reason codes
- Policy loading from YAML works correctly
- All tests pass

## Milestone 4: Policy Service MVP

**Status**: Not started

**Tasks**:
- Create policy-service skeleton
- Implement bind endpoint (POST /policies/bind)
- Implement policy retrieval (GET /policies/{policy_id})
- Implement policy lifecycle state machine
- Implement audit packet generation
- Implement blockchain gateway integration (stubbed)
- Add human approval workflow
- Add comprehensive tests

**Exit criteria**:
- Bind flow completes with audit packet
- Policy lifecycle transitions enforced
- All tests pass

## Milestone 5: Blockchain Gateway MVP

**Status**: Not started

**Tasks**:
- Create blockchain-gateway service (TypeScript)
- Implement PolicyRegistry contract (Solidity)
- Implement AuditEventRegistry contract (Solidity)
- Implement contract deployment scripts (Hardhat)
- Implement gateway service (ethers.js)
- Deploy to local Anvil
- Implement policy commitment flow
- Add comprehensive tests

**Exit criteria**:
- Contracts deploy to local Anvil
- Policy commitments written and verifiable
- All tests pass

## Milestone 6: AI Agent Orchestrator MVP

**Status**: Not started

**Tasks**:
- Create ai-agent-orchestrator service
- Implement session management
- Implement intent classification
- Implement tool permission enforcement
- Implement AI service integration (quote, risk, policy)
- Implement human review routing
- Implement audit logging
- Add comprehensive tests

**Exit criteria**:
- End-to-end AI-assisted quote flow works
- Tool permissions enforced
- All tests pass

## Milestone 7: Claims Service MVP

**Status**: Not started

**Tasks**:
- Create claims-service skeleton
- Implement FNOL endpoint (POST /claims)
- Implement coverage check (POST /claims/{claim_id}/coverage-check)
- Implement claim retrieval (GET /claims/{claim_id})
- Add event emission for ClaimFNOLReceived
- Add comprehensive tests

**Exit criteria**:
- FNOL creates claim with proper event
- Coverage check verifies against policy
- All tests pass

## Milestone 8: Treasury Service MVP

**Status**: Not started

**Tasks**:
- Create treasury-service skeleton
- Implement premium allocation (stubbed)
- Implement reserve snapshot (stubbed)
- Implement liquidity ladder (stubbed)
- Add event emission for PremiumAllocated, ReserveSnapshot
- Add comprehensive tests

**Exit criteria**:
- Premium allocation stubbed and audited
- Reserve snapshot stubbed and audited
- All tests pass

## Implementation Notes

- Each service has its own Dockerfile
- docker-compose.yml manages local dev stack
- Shared types and event schemas are published as local packages
- All services validate inputs via Pydantic
- All services emit events via the event system
- All services log audit events
- All services have comprehensive tests
- No real payment processing in MVP
- No real blockchain deployment in MVP
- No AI model modification of rating logic
- No AI authority to bind, decline, or deny in MVP
