# Phase 1: Implementation Plan

## Phase 1: Core Services Implementation

### Overview

Phase 1 implements the core insurance services: Policy Service, Claims Service, and Treasury Service. These services form the operational backbone of the insurance operating system.

### Milestones

#### Milestone 4: Policy Service MVP (Target: Week 1-2)

**Goals:**
- Policy lifecycle state machine
- Bind flow with audit packet
- Human approval workflow
- Policy persistence (SQLite)

**Deliverables:**
- `services/policy-service/` directory
- Policy domain models
- Policy engine with state machine
- Bind flow implementation
- Audit packet generation
- Human approval workflow
- FastAPI application
- Comprehensive test suite

**Key Design Decisions:**
1. Policy lifecycle: `draft → pending_bind → active → endorsement → cancelled → expired`
2. Bind flow: AI prepares bind request → human approves → policy bound → blockchain commitment
3. Audit packet: JSON + hash commitment for blockchain storage
4. Persistence: SQLite for MVP, PostgreSQL for production

#### Milestone 5: Blockchain Gateway MVP (Target: Week 3-4)

**Goals:**
- PolicyRegistry + AuditEventRegistry contracts
- Local Anvil deployment
- Policy commitment flow

**Deliverables:**
- `packages/blockchain-gateway/` directory
- Hardhat contract deployment
- Policy commitment flow
- Audit event logging
- Local Anvil configuration
- Integration tests

**Key Design Decisions:**
1. Policy representation: Registry records (not NFTs)
2. On-chain data: policy_id, commitment_hash, status, committed_at only
3. Off-chain data: All customer data, documents, evidence
4. Privacy: Customer data never stored on-chain

#### Milestone 6: AI Agent Orchestrator MVP (Target: Week 5-6)

**Goals:**
- Session management
- Tool permission enforcement
- AI service integration

**Deliverables:**
- `services/ai-agent-orchestrator/` directory
- Session management
- Tool permission enforcement
- AI model routing
- Integration with quote service
- Integration with risk appetite service
- Comprehensive test suite

**Key Design Decisions:**
1. AI authority model: Allow/restrict by tool
2. Tool permissions: Enforced at orchestrator level
3. Model routing: Configurable per task
4. Audit: All AI tool calls audited

#### Milestone 7: Claims Service MVP (Target: Week 7-8)

**Goals:**
- FNOL intake
- Coverage check
- Claim processing

**Deliverables:**
- `services/claims-service/` directory
- FNOL intake API
- Coverage check against policy
- Claim processing workflow
- Integration with policy service
- Comprehensive test suite

**Key Design Decisions:**
1. FNOL: AI collects intake → human reviews → claim processed
2. Coverage check: Against active policy
3. Claim status: `intake → under_review → approved → denied → paid`

#### Milestone 8: Treasury Service MVP (Target: Week 9-10)

**Goals:**
- Premium allocation stub
- Reserve snapshot stub
- Treasury policy evaluation

**Deliverables:**
- `services/treasury-service/` directory
- Premium allocation
- Reserve snapshot
- Treasury policy evaluation
- Integration with policy service
- Comprehensive test suite

**Key Design Decisions:**
1. Premium allocation: Stub for MVP
2. Reserve snapshot: Stub for MVP
3. Treasury policy: Configurable via YAML

### Service Dependencies

```
quote-service ──→ risk-appetite-service
                    ↓
            policy-service
                    ↓
            blockchain-gateway
                    ↓
            treasury-service
                    ↓
            ai-agent-orchestrator
                    ↓
            claims-service
```

### Testing Requirements

Each service must have:
- Unit tests: 80%+ coverage
- Integration tests: Service communication
- Contract tests: API compatibility
- Security tests: Authorization, input validation
- Compliance tests: Regulatory requirements

### Deployment

#### Local Development
- docker-compose for all services
- Local Anvil for blockchain
- SQLite for persistence

#### Production
- Kubernetes (future)
- PostgreSQL (future)
- Public chain (future)
