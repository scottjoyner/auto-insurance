# auto-insurance
Below is a **repo-ready architecture draft** for a new blockchain-first insurance company platform. I would treat this as the initial `/docs` package for the repo.

A key design constraint: the system should be **blockchain-first, not blockchain-only**. Insurance is still state-regulated, capital-constrained, audit-heavy, privacy-sensitive, and subject to rate/form/product approval workflows. NAIC materials describe ORSA as an internal process for evaluating insurer risk management and solvency under stress scenarios, including underwriting, credit, market, operational, and liquidity risks. ([NAIC][1]) NAIC also describes Risk-Based Capital as a core regulatory solvency mechanism for safeguarding financial stability. ([NAIC][2]) So the architecture should put blockchain at the center of auditability, policy commitments, claims events, reinsurance/treasury rails, and delegated automation, while keeping regulated decisions, PII, actuarial models, and capital controls in governed off-chain systems.

---

# 1. Repository Purpose

## Working repo name

`chain-insure-core`

## Mission

Build a blockchain-first insurance operating system that supports:

1. AI-assisted insurance quoting.
2. Policy creation and lifecycle management.
3. Risk appetite evaluation.
4. Underwriting orchestration.
5. Customer acquisition and CRM.
6. Agentic customer service.
7. Claims intake and adjudication.
8. Float, reserve, treasury, and solvency management.
9. Compliance, audit, and regulatory reporting.
10. On-chain commitments for policies, premiums, claims, reserves, and fund flows.

## Core architectural principle

The blockchain layer is the **source of cryptographic truth** for commitments, state transitions, payments, attestations, and audit logs.

The off-chain platform is the **source of operational truth** for regulated workflows, actuarial models, customer data, underwriting evidence, documents, agent interactions, and sensitive records.

---

# 2. High-Level Design

## 2.1 System Domains

The platform should be split into these major domains:

| Domain                  | Purpose                                                                                            |
| ----------------------- | -------------------------------------------------------------------------------------------------- |
| Identity & Access       | Users, customers, licensed agents, admins, underwriters, auditors, smart contract roles            |
| Customer Acquisition    | Campaigns, referrals, lead capture, web/app onboarding, AI sales agent                             |
| AI Insurance Agent      | Conversational quote intake, document collection, explanations, next-best-action                   |
| Quote Engine            | Product eligibility, rating, underwriting questions, quote packages                                |
| Risk Appetite Engine    | Decides whether a risk fits current company appetite, capacity, capital, geography, product limits |
| Policy Admin            | Bind, issue, endorse, renew, cancel, reinstate                                                     |
| Claims                  | FNOL, triage, evidence capture, adjudication, payout orchestration                                 |
| Blockchain Core         | Policy NFTs/tokens, premium escrow, claims escrow, audit events, reserve attestations              |
| Float & Treasury        | Premium allocation, reserve segmentation, investment policy controls, liquidity planning           |
| Reinsurance             | Treaty/facultative reinsurance support, ceded risk, counterparty exposure                          |
| Compliance & Governance | Rate/form controls, AI governance, model risk, consumer disclosures, audit trails                  |
| Analytics & Actuarial   | Loss ratios, pricing adequacy, risk scoring, exposure aggregation                                  |
| Data Platform           | Event store, graph store, warehouse/lakehouse, feature store, vector memory                        |
| Integrations            | KYC/KYB, payment processors, data vendors, document signing, email/SMS/voice                       |

---

## 2.2 Regulatory Design Guardrails

The repo should encode these guardrails from day one:

1. **AI cannot be treated as an ungoverned autonomous insurer.** NAIC’s AI materials state that AI techniques are used across insurance lifecycle areas including marketing, underwriting, pricing, servicing, claims, and fraud detection. ([NAIC][3]) The system should therefore include AI governance, model inventory, adverse action logging, bias/fairness monitoring, and human review thresholds.

2. **Rates/forms/products must be configurable and jurisdiction-aware.** NAIC’s SERFF materials describe SERFF as a web-based electronic filing system for rate and form filing and approval. ([NAIC][4]) The product engine should never let engineering hard-code rates without versioning, approval metadata, and jurisdiction controls.

3. **Solvency and capital constraints must gate underwriting.** Risk appetite must consider reserves, concentration, liquidity, reinsurance, and RBC/ORSA-style scenarios, not just quote profitability. NAIC ORSA guidance centers on evaluating current and future solvency under stress scenarios. ([NAIC][1])

4. **Float management cannot be a free-form trading bot.** The float system should enforce an Investment Policy Statement, liquidity ladders, reserve segmentation, counterparty limits, board approvals, and statutory accounting outputs. NAIC statutory accounting materials describe the AP&P Manual as the basis insurers use to prepare financial statements for financial regulation. ([NAIC][5])

5. **PII and sensitive underwriting evidence should not be stored directly on-chain.** Store hashes, attestations, proofs, policy IDs, encrypted references, and event commitments on-chain. Store personal data off-chain with encryption, retention controls, and access logging.

---

# 3. Target Architecture

## 3.1 Logical Architecture

```text
[Web App / Mobile App / Agent Portal]
              |
              v
[AI Insurance Agent Orchestrator]
              |
              +--> [Customer Intake Service]
              +--> [Quote Engine]
              +--> [Risk Appetite Engine]
              +--> [Policy Admin Service]
              +--> [Claims Service]
              +--> [CRM / Client Relations Service]
              +--> [Compliance Guardrail Service]
              +--> [Human Review Workbench]
              |
              v
[Event Bus / Workflow Engine / Audit Log]
              |
              +--> [Operational DB]
              +--> [Document Store]
              +--> [Feature Store]
              +--> [Vector Store]
              +--> [Graph Store]
              +--> [Analytics Warehouse]
              |
              v
[Blockchain Gateway]
              |
              +--> [Policy Registry Contract]
              +--> [Premium Escrow Contract]
              +--> [Claims Escrow Contract]
              +--> [Reserve Attestation Contract]
              +--> [Treasury Policy Contract]
              +--> [Governance / Multisig Contract]
```

---

## 3.2 Core Data Flow

### Quote-to-bind flow

```text
Lead created
  -> AI agent collects intake
  -> Product eligibility check
  -> Data enrichment
  -> Risk scoring
  -> Risk appetite check
  -> Rating engine generates quote
  -> Compliance review
  -> Customer accepts quote
  -> Payment collected
  -> Policy bind request created
  -> Policy admin issues policy
  -> On-chain policy commitment minted/registered
  -> Documents generated
  -> CRM lifecycle begins
```

### Claim flow

```text
Claim submitted
  -> AI agent collects FNOL
  -> Evidence package created
  -> Coverage verification
  -> Fraud/risk triage
  -> Adjuster or automated adjudication path
  -> Reserve estimate created
  -> Claim decision logged
  -> Payment approved
  -> On-chain claim event committed
  -> Payment released
  -> Loss data fed back into actuarial models
```

### Float management flow

```text
Premium received
  -> Premium split into earned/unearned buckets
  -> Required reserve calculated
  -> Liquidity ladder updated
  -> Investment policy constraints evaluated
  -> Treasury proposal generated
  -> Human/committee approval if threshold exceeded
  -> Execution through approved custodians/protocols
  -> On-chain reserve/fund-flow attestation committed
  -> Accounting and solvency reports updated
```

---

# 4. High-Level Components

## 4.1 AI Insurance Agent

### Purpose

The AI agent is the front door and internal operator assistant. It should not silently make regulated final decisions. It should orchestrate workflows, collect information, explain options, generate quote packages, and route cases to licensed humans when required.

### Responsibilities

* Intake conversation.
* Product recommendation.
* Underwriting question flow.
* Quote explanation.
* Customer support.
* Renewal outreach.
* Claims FNOL.
* Document collection.
* Human handoff.
* Compliance-safe response generation.
* Audit logging of every material recommendation.

### AI guardrails

The agent must:

* Use retrieval over approved product/rate/form knowledge.
* Avoid unapproved policy promises.
* Never fabricate coverage.
* Never bind without authority.
* Escalate adverse decisions.
* Explain why a quote was declined or referred.
* Log all prompts, retrieved docs, tools used, and decision traces.
* Support model version rollback.
* Support state-specific disclosures.

NAIC’s AI page notes that AI may change insurance work, but actuaries, underwriters, claims professionals, agents, and customer service representatives still play important roles in reviewing information, exercising judgment, and working with consumers. ([NAIC][6]) That should be reflected in the permission model.

---

## 4.2 Quote Engine

### Purpose

Generate compliant, versioned, explainable quotes.

### Inputs

* Applicant profile.
* Jurisdiction.
* Product line.
* Coverage selections.
* Underwriting answers.
* Third-party data.
* Loss history.
* Risk score.
* Current risk appetite.
* Filed/approved rating plan version.
* Discounts, fees, taxes, surcharges.

### Outputs

* Quote ID.
* Premium.
* Coverage terms.
* Deductibles.
* Exclusions.
* Required documents.
* Referral flags.
* Decline reasons.
* Bind eligibility.
* Explainability package.
* Quote expiration.

### Quote engine principles

* Every quote must be reproducible.
* Every quote must reference a product/rate/form version.
* All rating variables must be logged.
* Manual overrides must be permissioned and audited.
* AI can assist, but rating logic should be deterministic or formally governed.

---

## 4.3 Risk Appetite Engine

### Purpose

Decide whether the company wants to accept, decline, refer, reprice, reinsure, or limit a risk.

### Risk appetite dimensions

| Dimension      | Examples                                                                           |
| -------------- | ---------------------------------------------------------------------------------- |
| Product        | Auto, homeowners, renters, cyber, commercial general liability, parametric weather |
| Geography      | State, county, ZIP, catastrophe zone                                               |
| Exposure       | Insured value, limits, concentration                                               |
| Customer risk  | Claims history, payment behavior, fraud indicators                                 |
| Portfolio risk | Accumulation, correlated losses, concentration                                     |
| Capital        | Required reserve, RBC impact, solvency margin                                      |
| Reinsurance    | Treaty availability, retention, exhaustion                                         |
| Liquidity      | Claim payout timing, reserve adequacy                                              |
| Operational    | Claims handling complexity, legal exposure                                         |
| Regulatory     | Product approval, state restrictions, licensing                                    |

### Risk appetite decisions

```text
ACCEPT
REFER_TO_UNDERWRITER
ACCEPT_WITH_LIMITS
ACCEPT_WITH_REINSURANCE
DECLINE
WAITLIST
REQUEST_MORE_INFO
```

### Required outputs

* Decision.
* Reason codes.
* Capital impact.
* Reserve impact.
* Reinsurance impact.
* Concentration impact.
* Required approvals.
* Audit trace.

---

## 4.4 Policy Admin

### Purpose

Manage the lifecycle of a policy.

### Policy lifecycle

```text
DRAFT_QUOTE
QUOTED
ACCEPTED
BOUND
ISSUED
ACTIVE
ENDORSED
RENEWAL_PENDING
RENEWED
CANCEL_PENDING
CANCELLED
EXPIRED
REINSTATED
CLAIM_LOCKED
```

### Policy admin features

* Bind issuance.
* Endorsements.
* Cancellations.
* Renewals.
* Non-renewals.
* Document generation.
* Billing schedule.
* Commission schedule.
* Coverage verification.
* Jurisdiction-specific workflow.
* Blockchain commitment sync.

---

## 4.5 Blockchain Core

### Purpose

Provide cryptographic auditability and programmable settlement without leaking sensitive insurance data.

### On-chain objects

| Object      | On-chain representation                                        |
| ----------- | -------------------------------------------------------------- |
| Policy      | Policy commitment, hash, status, coverage metadata subset      |
| Premium     | Payment event, escrow allocation, accounting reference         |
| Claim       | Claim event commitment, payout authorization, settlement proof |
| Reserve     | Reserve attestation hash, timestamp, authorized signer         |
| Reinsurance | Risk transfer commitment, counterparty attestation             |
| Treasury    | Movement of permitted assets, IPS compliance proof             |
| Governance  | Multisig approvals, parameter changes, emergency pauses        |

### Smart contracts

1. `PolicyRegistry`
2. `PremiumEscrow`
3. `ClaimsEscrow`
4. `ReserveAttestation`
5. `ReinsuranceRegistry`
6. `TreasuryPolicy`
7. `GovernanceMultisig`
8. `OracleRegistry`
9. `ComplianceAttestation`
10. `AuditEventRegistry`

### Blockchain design rule

Never store:

* Full names.
* Addresses.
* Phone numbers.
* Emails.
* SSNs.
* Driver’s license numbers.
* Full policy PDFs.
* Claim evidence.
* Medical records.
* Sensitive risk factors.

Store:

* Hashes.
* Commitments.
* Merkle roots.
* Encrypted document pointers.
* Version IDs.
* Attestations.
* Role-based signatures.
* Minimal non-sensitive metadata.

---

## 4.6 Float and Treasury Management

### Purpose

Manage premium float, reserves, liquidity, and investment execution within approved constraints.

### Major buckets

```text
Premium received
  -> Unearned premium reserve
  -> Loss reserve
  -> Loss adjustment expense reserve
  -> Reinsurance payable
  -> Operating capital
  -> Investable surplus
  -> Restricted capital
```

### Float engine responsibilities

* Premium cashflow tracking.
* Earned/unearned premium accounting.
* Reserve calculation.
* Liquidity ladder.
* Stress testing.
* Asset allocation constraints.
* Counterparty limits.
* Reinsurance recoverable tracking.
* Investment proposal generation.
* Human approval workflow.
* Blockchain reserve attestations.
* Statutory accounting export.

### Treasury constraints

The system should support an internal Investment Policy Statement:

```yaml
investment_policy:
  max_crypto_exposure_pct: 0
  max_stablecoin_exposure_pct: 5
  min_cash_and_treasury_pct: 60
  max_duration_years: 3
  min_liquidity_30_days_pct: 25
  max_single_counterparty_pct: 10
  require_board_approval_above_usd: 250000
  prohibit_unapproved_defi_protocols: true
  require_daily_mark_to_market: true
```

For a real licensed insurer, these values would need to be set by legal, actuarial, treasury, board, and regulatory advisors.

---

## 4.7 Customer Acquisition and Client Relations

### Purpose

Build a full-funnel insurance acquisition and retention system.

### Capabilities

* Lead capture.
* Referral codes.
* Campaign attribution.
* Quote abandonment recovery.
* AI outbound follow-up.
* Renewal reminders.
* Cross-sell recommendations.
* Customer lifetime value.
* Producer/agent commissions.
* Service ticketing.
* Complaint management.
* Churn prediction.
* NPS/customer satisfaction tracking.

### CRM objects

```text
Lead
Prospect
Applicant
Customer
Household / Business
Policyholder
Claimant
Producer
Broker
Agent
ServiceCase
Campaign
Touchpoint
Consent
CommunicationPreference
```

---

# 5. Low-Level Design

## 5.1 Suggested Repo Structure

```text
chain-insure-core/
  README.md
  docs/
    00_vision.md
    01_hld.md
    02_lld.md
    03_execution_plan.md
    04_regulatory_guardrails.md
    05_ai_governance.md
    06_blockchain_architecture.md
    07_float_management.md
    08_risk_appetite.md
    09_product_rating_engine.md
    10_security_model.md
    11_data_model.md
    12_api_contracts.md
    13_testing_strategy.md
    14_open_questions.md
  apps/
    web/
    agent-console/
    underwriter-console/
    admin-console/
  services/
    ai-agent-orchestrator/
    quote-service/
    risk-appetite-service/
    policy-service/
    claims-service/
    crm-service/
    compliance-service/
    treasury-service/
    blockchain-gateway/
    document-service/
    notification-service/
    analytics-service/
  contracts/
    foundry/
      src/
      test/
      script/
  packages/
    shared-types/
    event-schemas/
    product-config/
    rating-dsl/
    authz/
    observability/
  infra/
    docker-compose.yml
    k8s/
    terraform/
    local-dev/
  data/
    seeds/
    sample-products/
    sample-rates/
  tests/
    integration/
    e2e/
    load/
    security/
  scripts/
    bootstrap-dev.sh
    run-local.sh
    seed-demo-data.py
```

---

## 5.2 Recommended Initial Tech Stack

Given your existing style, I would bias this toward Python services, typed event schemas, Neo4j for relationship-heavy insurance knowledge, and a deterministic backend for rating.

| Layer          | Recommended stack                                                           |
| -------------- | --------------------------------------------------------------------------- |
| API gateway    | FastAPI or NestJS                                                           |
| Services       | Python FastAPI for AI/risk/actuarial, TypeScript for web/API-heavy services |
| Workflow       | Temporal, Prefect, or durable queue-backed orchestration                    |
| Event bus      | Redpanda/Kafka or NATS                                                      |
| Operational DB | PostgreSQL                                                                  |
| Graph DB       | Neo4j                                                                       |
| Cache          | Redis                                                                       |
| Object store   | S3-compatible MinIO                                                         |
| Vector store   | pgvector, Qdrant, or Neo4j vector indexes                                   |
| Contracts      | Solidity + Foundry                                                          |
| Chain          | Start local Anvil; later Base, Polygon, Arbitrum, or permissioned EVM       |
| Auth           | OIDC, OAuth2, passkeys, wallet auth for blockchain roles                    |
| Secrets        | Doppler, Vault, SOPS, or cloud KMS                                          |
| Observability  | OpenTelemetry, Prometheus, Grafana, Loki                                    |
| Analytics      | DuckDB initially, later ClickHouse/BigQuery/Snowflake                       |
| Docs           | Markdown, Mermaid, OpenAPI, AsyncAPI                                        |

---

## 5.3 Service-Level Design

## AI Agent Orchestrator

### Responsibilities

* Manage conversations.
* Call tools.
* Retrieve product knowledge.
* Collect underwriting data.
* Explain quote decisions.
* Create workflow tasks.
* Escalate to humans.
* Maintain compliant conversation logs.

### API sketch

```http
POST /agent/sessions
POST /agent/sessions/{session_id}/messages
POST /agent/sessions/{session_id}/tools/quote
POST /agent/sessions/{session_id}/handoff
GET  /agent/sessions/{session_id}/audit
```

### Core tables

```sql
agent_session
agent_message
agent_tool_call
agent_retrieval_event
agent_decision_trace
agent_handoff
```

---

## Quote Service

### Responsibilities

* Validate product eligibility.
* Calculate premiums.
* Apply rating rules.
* Produce quote documents.
* Send referral cases.

### API sketch

```http
POST /quotes
GET  /quotes/{quote_id}
POST /quotes/{quote_id}/recalculate
POST /quotes/{quote_id}/accept
POST /quotes/{quote_id}/refer
POST /quotes/{quote_id}/expire
```

### Core tables

```sql
quote
quote_input_snapshot
quote_rating_result
quote_coverage_option
quote_fee_tax
quote_explainability
quote_referral
```

### Rating config example

```yaml
product_id: renters_v1
jurisdiction: NC
version: 2026.001
status: draft
base_rate: 120.00

variables:
  coverage_limit:
    type: numeric
    factor_table:
      25000: 1.00
      50000: 1.22
      100000: 1.55

  deductible:
    type: numeric
    factor_table:
      250: 1.20
      500: 1.00
      1000: 0.88

  risk_score_band:
    type: categorical
    factor_table:
      low: 0.90
      medium: 1.00
      high: 1.35

rules:
  - id: decline_high_risk_zip
    when: applicant.zip in high_risk_zips
    action: refer
    reason_code: GEO_ACCUMULATION_REVIEW
```

---

## Risk Appetite Service

### Responsibilities

* Evaluate portfolio-level constraints.
* Gate underwriting based on risk appetite.
* Enforce concentration limits.
* Check capital/reserve impact.
* Recommend accept/refer/decline.

### API sketch

```http
POST /risk-appetite/evaluate
GET  /risk-appetite/policies
POST /risk-appetite/policies/{policy_id}/versions
POST /risk-appetite/scenarios
GET  /risk-appetite/exposure-map
```

### Decision response

```json
{
  "decision": "REFER_TO_UNDERWRITER",
  "reason_codes": [
    "ZIP_CONCENTRATION_LIMIT",
    "CAPITAL_USAGE_ABOVE_THRESHOLD"
  ],
  "capital_impact": {
    "required_capital_delta": 183.22,
    "reserve_delta": 91.11
  },
  "portfolio_impact": {
    "zip_exposure_after_bind": 0.084,
    "zip_limit": 0.075
  },
  "required_approvals": [
    "UNDERWRITER_LEVEL_2"
  ]
}
```

---

## Policy Service

### Responsibilities

* Bind quotes.
* Issue policies.
* Generate policy documents.
* Manage endorsements.
* Manage cancellations and renewals.
* Sync policy commitments to chain.

### API sketch

```http
POST /policies/bind
GET  /policies/{policy_id}
POST /policies/{policy_id}/endorsements
POST /policies/{policy_id}/cancel
POST /policies/{policy_id}/renew
POST /policies/{policy_id}/sync-chain
```

### Core tables

```sql
policy
policy_version
policy_coverage
policy_document
policy_status_history
policy_blockchain_commitment
policy_party
policy_billing_schedule
```

---

## Claims Service

### Responsibilities

* Intake FNOL.
* Verify coverage.
* Triage fraud and severity.
* Create reserves.
* Manage adjuster workflow.
* Approve/deny/pay claims.
* Commit claim events on-chain.

### API sketch

```http
POST /claims
GET  /claims/{claim_id}
POST /claims/{claim_id}/evidence
POST /claims/{claim_id}/coverage-check
POST /claims/{claim_id}/reserve
POST /claims/{claim_id}/decision
POST /claims/{claim_id}/payout
```

### Claim status model

```text
FNOL_RECEIVED
EVIDENCE_PENDING
COVERAGE_REVIEW
FRAUD_REVIEW
ADJUSTER_REVIEW
RESERVE_SET
APPROVED
DENIED
PAYMENT_PENDING
PAID
CLOSED
REOPENED
```

---

## Treasury Service

### Responsibilities

* Track premium cash.
* Calculate reserves.
* Manage float allocation.
* Enforce investment constraints.
* Generate treasury proposals.
* Route approvals.
* Record execution.
* Produce accounting exports.

### API sketch

```http
POST /treasury/premium-received
POST /treasury/reserve-calc
GET  /treasury/liquidity-ladder
POST /treasury/proposals
POST /treasury/proposals/{proposal_id}/approve
POST /treasury/proposals/{proposal_id}/execute
GET  /treasury/solvency-dashboard
```

### Core tables

```sql
premium_cashflow
reserve_snapshot
float_allocation
treasury_policy
treasury_proposal
treasury_approval
treasury_execution
asset_position
counterparty_exposure
```

---

## Blockchain Gateway

### Responsibilities

* Abstract chain RPC.
* Submit contract transactions.
* Verify receipts.
* Index chain events.
* Reconcile on-chain/off-chain state.
* Manage contract ABI versions.
* Enforce signer policy.

### API sketch

```http
POST /chain/policies/register
POST /chain/premiums/record
POST /chain/claims/record
POST /chain/reserves/attest
GET  /chain/transactions/{tx_hash}
GET  /chain/reconcile
```

### Design requirement

All chain writes should be asynchronous and idempotent:

```text
Request created
  -> Outbox event written
  -> Blockchain worker submits tx
  -> Receipt indexed
  -> Off-chain record updated
  -> Reconciliation job verifies state
```

---

# 6. Smart Contract LLD

## 6.1 Contract: PolicyRegistry

### Purpose

Register policy commitments and lifecycle state.

### Minimal interface

```solidity
interface IPolicyRegistry {
    function registerPolicy(
        bytes32 policyId,
        bytes32 policyHash,
        bytes32 productVersionHash,
        address policyholderRef,
        uint256 effectiveTimestamp,
        uint256 expirationTimestamp
    ) external;

    function updatePolicyStatus(
        bytes32 policyId,
        bytes32 status,
        bytes32 statusReasonHash
    ) external;

    function getPolicy(bytes32 policyId)
        external
        view
        returns (
            bytes32 policyHash,
            bytes32 productVersionHash,
            bytes32 status,
            uint256 effectiveTimestamp,
            uint256 expirationTimestamp
        );
}
```

### Notes

* `policyholderRef` should not directly expose the user’s real identity.
* `policyHash` is the hash of the canonical off-chain policy package.
* Status updates should only be callable by approved roles.

---

## 6.2 Contract: PremiumEscrow

### Purpose

Record premium payment commitments and escrow allocations.

```solidity
interface IPremiumEscrow {
    function recordPremium(
        bytes32 policyId,
        bytes32 paymentId,
        uint256 amount,
        address asset,
        bytes32 allocationHash
    ) external;

    function allocatePremium(
        bytes32 paymentId,
        bytes32 reserveBucketHash
    ) external;
}
```

---

## 6.3 Contract: ClaimsEscrow

### Purpose

Record claim events and authorized payouts.

```solidity
interface IClaimsEscrow {
    function registerClaim(
        bytes32 policyId,
        bytes32 claimId,
        bytes32 claimHash
    ) external;

    function approvePayout(
        bytes32 claimId,
        uint256 amount,
        address asset,
        bytes32 approvalHash
    ) external;

    function markPaid(
        bytes32 claimId,
        bytes32 paymentHash
    ) external;
}
```

---

## 6.4 Contract: ReserveAttestation

### Purpose

Publish periodic reserve and solvency attestations.

```solidity
interface IReserveAttestation {
    function attestReserveSnapshot(
        bytes32 snapshotId,
        bytes32 reserveMerkleRoot,
        uint256 timestamp,
        bytes32 methodologyHash
    ) external;
}
```

---

## 6.5 Contract: GovernanceMultisig

### Purpose

Control high-impact parameters.

Governance should control:

* Contract upgrades.
* Treasury policy changes.
* Oracle registry updates.
* Emergency pauses.
* Signer rotation.
* Product activation.
* Reinsurance counterparty approval.
* Claim payout thresholds.

---

# 7. Data Model Draft

## 7.1 Core relational entities

```text
Party
Customer
Producer
Lead
Consent
Product
ProductVersion
Coverage
RatePlan
Quote
QuoteVersion
RiskAssessment
Policy
PolicyVersion
Claim
ClaimEvidence
ClaimDecision
Payment
ReserveSnapshot
TreasuryProposal
TreasuryExecution
BlockchainTransaction
AuditEvent
ModelVersion
AIInteraction
ComplianceReview
```

---

## 7.2 Neo4j graph model

Neo4j should be useful for relationship-heavy risk, fraud, exposure, customer, and operational intelligence.

### Node labels

```text
:Customer
:Household
:Business
:Policy
:Quote
:Claim
:Vehicle
:Property
:Location
:Producer
:Agent
:Underwriter
:RiskFactor
:Coverage
:Payment
:Wallet
:Device
:Document
:Conversation
:Model
:Jurisdiction
:Product
:Reinsurer
:Counterparty
```

### Relationship types

```text
(:Customer)-[:OWNS_POLICY]->(:Policy)
(:Policy)-[:HAS_COVERAGE]->(:Coverage)
(:Policy)-[:INSURES]->(:Property)
(:Claim)-[:FILED_UNDER]->(:Policy)
(:Claim)-[:HAS_EVIDENCE]->(:Document)
(:Customer)-[:USES_WALLET]->(:Wallet)
(:Quote)-[:EVALUATED_BY]->(:Model)
(:Policy)-[:LOCATED_IN]->(:Jurisdiction)
(:RiskFactor)-[:AFFECTS]->(:Quote)
(:Producer)-[:SOLD]->(:Policy)
(:Policy)-[:CEDED_TO]->(:Reinsurer)
(:Payment)-[:ALLOCATED_TO]->(:ReserveSnapshot)
```

---

## 7.3 Event schemas

All meaningful changes should emit immutable domain events.

Example events:

```text
LeadCreated
ConsentCaptured
QuoteRequested
RiskAssessmentCompleted
QuoteGenerated
QuoteAccepted
PolicyBound
PolicyIssued
PremiumReceived
PolicyCommittedOnChain
ClaimSubmitted
ClaimReserveSet
ClaimApproved
ClaimPaid
ReserveSnapshotCreated
ReserveSnapshotAttestedOnChain
TreasuryProposalCreated
TreasuryProposalApproved
TreasuryExecutionCompleted
AIInteractionLogged
HumanReviewRequired
ComplianceExceptionRaised
```

Example event envelope:

```json
{
  "event_id": "evt_01HX...",
  "event_type": "QuoteGenerated",
  "aggregate_type": "Quote",
  "aggregate_id": "quote_123",
  "occurred_at": "2026-05-26T14:00:00Z",
  "actor": {
    "actor_type": "AI_AGENT",
    "actor_id": "agent_quote_v1"
  },
  "correlation_id": "corr_abc",
  "causation_id": "evt_prev",
  "payload": {},
  "schema_version": "1.0.0"
}
```

---

# 8. AI Agent Design

## 8.1 Agent roles

```text
SalesIntakeAgent
UnderwritingAssistantAgent
RiskAppetiteAgent
PolicyServiceAgent
ClaimsIntakeAgent
ClaimsTriageAgent
ComplianceReviewAgent
TreasuryAnalystAgent
CustomerRetentionAgent
ExecutiveOpsAgent
```

## 8.2 Agent orchestration pattern

Use a central orchestrator with strict tool permissions:

```text
User message
  -> Intent classification
  -> Policy/product retrieval
  -> Tool authorization check
  -> Tool execution
  -> Compliance guardrail
  -> Human review if needed
  -> Final response
  -> Audit log
```

## 8.3 Tool permissions

| Agent                      | Allowed tools                  | Restricted tools                      |
| -------------------------- | ------------------------------ | ------------------------------------- |
| SalesIntakeAgent           | CRM, quote draft, product info | Bind, decline, treasury               |
| UnderwritingAssistantAgent | Risk scoring, data enrichment  | Final adverse decision without review |
| RiskAppetiteAgent          | Portfolio analysis             | Product filing changes                |
| ClaimsIntakeAgent          | FNOL, evidence upload          | Claim payout                          |
| TreasuryAnalystAgent       | Proposals, reserve views       | Direct execution above thresholds     |
| ComplianceReviewAgent      | Audit review, disclosure check | Contract upgrade                      |
| ExecutiveOpsAgent          | Dashboards, approvals          | Raw model edits without governance    |

---

# 9. Compliance and Governance

## 9.1 AI governance artifacts

The repo should include a documented AI Systems Program because NAIC’s model bulletin focuses on insurer governance, risk management, internal controls, and oversight for AI systems used across the insurance lifecycle. ([NAIC][3])

Create these files:

```text
docs/05_ai_governance.md
governance/model_inventory.yml
governance/approved_prompts/
governance/model_eval_reports/
governance/adverse_action_reason_codes.yml
governance/human_review_thresholds.yml
```

## 9.2 Required governance controls

* Model inventory.
* Data inventory.
* Prompt registry.
* Tool registry.
* Human approval thresholds.
* Bias/fairness test suite.
* Explainability reports.
* Consumer-impact review.
* Versioned model deployment.
* Rollback process.
* Complaint review workflow.
* Audit export.

---

# 10. Security Model

## 10.1 Access control

Use RBAC plus ABAC.

### Roles

```text
CUSTOMER
PROSPECT
LICENSED_AGENT
PRODUCER
UNDERWRITER_L1
UNDERWRITER_L2
CLAIMS_ADJUSTER
CLAIMS_MANAGER
TREASURY_ANALYST
TREASURY_APPROVER
COMPLIANCE_OFFICER
ACTUARY
AUDITOR
ADMIN
SMART_CONTRACT_SIGNER
```

### Attributes

```text
jurisdiction
product_line
authority_limit
license_status
department
case_assignment
approval_threshold
chain_signing_role
```

## 10.2 Security requirements

* Encrypt PII at rest.
* Encrypt documents.
* Field-level access controls.
* Full audit log.
* Immutable event log.
* Signed decision records.
* Secrets managed outside code.
* Zero direct production DB access for agents.
* Contract admin via multisig.
* Emergency pause.
* Contract upgrade timelock.
* Automated key rotation.
* Least privilege service accounts.

---

# 11. Execution Plan

## Phase 0 — Repo bootstrap and architecture

### Deliverables

```text
README.md
docs/01_hld.md
docs/02_lld.md
docs/03_execution_plan.md
docs/04_regulatory_guardrails.md
docs/14_open_questions.md
docker-compose.yml
```

### Acceptance criteria

* Local dev environment boots.
* Docs define product scope.
* Event schema package exists.
* Initial service boundaries are defined.
* Smart contract skeletons compile.

---

## Phase 1 — Product, quote, and risk MVP

### Build

* Product config schema.
* Rating DSL.
* Quote service.
* Risk appetite service.
* Underwriter referral workflow.
* Quote audit logs.
* Sample product.

### MVP assumption

Start with a simple product such as:

```text
parametric travel delay insurance
renters insurance
personal cyber protection
small device protection
```

Avoid starting with complex auto/home/commercial unless the first goal is architecture only.

### Acceptance criteria

* User can request quote.
* Quote engine calculates premium.
* Risk appetite engine returns accept/refer/decline.
* Quote is reproducible from snapshot.
* Human override is audited.

---

## Phase 2 — AI agent and CRM

### Build

* AI intake agent.
* CRM lead/customer model.
* Conversation memory.
* Product knowledge retrieval.
* Quote explanation.
* Handoff to human.
* Consent capture.
* Communication preferences.

### Acceptance criteria

* AI agent collects complete quote intake.
* Agent can explain quote but not fabricate coverage.
* Agent creates CRM records.
* Agent routes edge cases to human review.
* All conversations are auditable.

---

## Phase 3 — Policy admin and blockchain commitments

### Build

* Policy bind flow.
* Policy document generation.
* Policy registry smart contract.
* Blockchain gateway.
* On-chain policy hash registration.
* Reconciliation jobs.

### Acceptance criteria

* Accepted quote can bind into policy.
* Policy document hash is committed on-chain.
* Policy state changes are mirrored.
* Chain/off-chain reconciliation report exists.

---

## Phase 4 — Premium, billing, and escrow

### Build

* Billing schedule.
* Payment intake.
* Premium allocation.
* Premium escrow contract.
* Earned/unearned premium tracking.
* Payment reconciliation.

### Acceptance criteria

* Premium payment is recorded.
* Allocation is calculated.
* Chain commitment is created.
* Billing status reconciles.

---

## Phase 5 — Claims MVP

### Build

* FNOL intake.
* Evidence upload.
* Coverage check.
* Reserve estimate.
* Claim decision workflow.
* Claims escrow contract.
* Payout approval flow.

### Acceptance criteria

* Customer can file claim.
* Coverage check references policy version.
* Claim reserve is logged.
* Claim decision is auditable.
* Approved payout creates on-chain event.

---

## Phase 6 — Float and treasury system

### Build

* Reserve engine.
* Liquidity ladder.
* Treasury policy engine.
* Asset position tracking.
* Investment proposal workflow.
* Approval workflow.
* Reserve attestation contract.

### Acceptance criteria

* Premium float is allocated by rule.
* Reserve snapshots are generated.
* Treasury proposals are blocked if policy limits fail.
* High-value execution requires approval.
* Reserve snapshot hash is committed on-chain.

---

## Phase 7 — Reinsurance and portfolio risk

### Build

* Treaty model.
* Ceded premium/loss tracking.
* Reinsurer counterparty registry.
* Exposure aggregation.
* Catastrophe/concentration dashboards.
* Risk appetite feedback loop.

### Acceptance criteria

* Risk appetite sees reinsurance capacity.
* Ceded exposure is tracked.
* Counterparty limits are enforced.
* Portfolio aggregation dashboard exists.

---

## Phase 8 — Governance, regulatory, and reporting layer

### Build

* AI governance reports.
* Product filing metadata.
* Audit exports.
* Complaint workflow.
* Model inventory.
* ORSA-style risk report.
* Statutory accounting export stubs.

### Acceptance criteria

* Every AI decision has trace metadata.
* Every quote references product/rate/form version.
* Every policy state transition has audit history.
* Compliance officer can export review package.

---

# 12. Testing Strategy

## Unit tests

* Rating factors.
* Eligibility rules.
* Risk appetite rules.
* Reserve calculations.
* Smart contract access control.
* Event schema validation.
* Agent guardrails.

## Integration tests

* Quote to bind.
* Bind to chain commitment.
* Premium to reserve allocation.
* Claim to payout.
* Treasury proposal to approval.
* AI agent to quote service.

## Property-based tests

* Premium cannot be negative.
* Policy cannot bind without accepted quote.
* Claim cannot pay above approved amount.
* Treasury cannot exceed policy limits.
* Contract state cannot skip required statuses.

## Security tests

* PII never emitted to chain.
* Unauthorized agent cannot bind.
* Unauthorized treasury user cannot execute.
* Smart contract signer role cannot be bypassed.
* Prompt injection cannot override tool permissions.

## Model tests

* Quote explanation accuracy.
* Coverage hallucination tests.
* Adverse decision explanation tests.
* Bias/fairness evaluation.
* Regression testing across model versions.

---

# 13. Initial Roadmap Issues for GitHub

Create these as first repo issues:

```text
#1 Bootstrap repo structure and documentation skeleton
#2 Define canonical event envelope and event schemas
#3 Implement product configuration schema
#4 Implement deterministic rating DSL MVP
#5 Implement quote-service MVP
#6 Implement risk-appetite-service MVP
#7 Implement AI agent orchestrator skeleton
#8 Implement CRM lead/customer model
#9 Implement policy-service bind flow
#10 Implement PolicyRegistry smart contract
#11 Implement blockchain-gateway outbox worker
#12 Implement audit event service
#13 Implement claims FNOL MVP
#14 Implement premium allocation model
#15 Implement reserve snapshot model
#16 Implement treasury policy constraints
#17 Implement compliance guardrail service
#18 Implement model inventory and AI governance docs
#19 Implement local Docker Compose stack
#20 Implement e2e quote-to-policy test
```

---

# 14. Design Decision Questions for You

## Company and product scope

1. What is the first insurance product line: renters, travel, cyber, device protection, auto, home, commercial, parametric weather, something else?
2. Is this a real regulated carrier, MGA, captive, reinsurer-like structure, or proof-of-concept protocol?
3. What states or jurisdictions should the system assume first?
4. Should the first product be admitted, surplus lines, captive, or parametric/contractual protection?
5. Should the platform support only direct-to-consumer or also brokers/producers?

## Blockchain strategy

6. Public chain, permissioned EVM, appchain, or hybrid?
7. Should customers use wallets directly, or should wallet abstraction hide the chain?
8. Should policies be represented as NFTs, soulbound tokens, registry records, or non-transferable attestations?
9. Should premium payments support fiat only, stablecoins, or both?
10. Should claim payouts support fiat only, stablecoins, or both?
11. What chain should we target first for testnet/mainnet?
12. Do you want on-chain governance, traditional corporate governance, or hybrid multisig plus board approval?

## AI agent authority

13. Can the AI agent only quote, or can it also bind within strict rules?
14. Should the AI agent be allowed to decline risks, or only refer/soft-decline with human review?
15. What actions always require licensed human approval?
16. Should the AI agent interact with customers by web chat only, or also email/SMS/voice?
17. Should agent conversations be stored forever, retained for a fixed period, or purged by policy?

## Underwriting and pricing

18. Should rating be deterministic rules first, ML first, or hybrid?
19. What third-party data sources should be allowed?
20. What risk factors are explicitly prohibited?
21. Should underwriting be instant-bind, referral-heavy, or conservative at launch?
22. How should manual overrides work?
23. Do we need adverse action notices or quote-decline explanations in MVP?

## Risk appetite

24. What is the company’s initial maximum policy limit?
25. What is the maximum exposure per customer?
26. What is the maximum exposure per geography?
27. What is the target loss ratio?
28. What concentration risks matter most?
29. How aggressive should growth be versus solvency protection?
30. Should reinsurance be assumed from day one?

## Float and treasury

31. Should float management be simulated only at first?
32. What assets are allowed for float?
33. Are crypto/stablecoin assets allowed at all?
34. What minimum cash/liquidity percentage should be enforced?
35. What approval thresholds should apply to treasury actions?
36. Should the platform integrate with a real custodian or use mock treasury accounts first?
37. Should investment yield be included in quote/pricing assumptions?

## Claims

38. Should claims be AI-assisted only or partially automated?
39. What claim types can be automatically paid?
40. What evidence types are required?
41. What fraud checks are needed?
42. What payout thresholds require human review?
43. Should claims settlement be fiat, stablecoin, or customer choice?

## Data and architecture

44. Do you want this as a monorepo?
45. Should the first implementation be Python-heavy, TypeScript-heavy, or split?
46. Should Neo4j be part of MVP from day one?
47. Should Kafka/Redpanda be included immediately, or should we start with Postgres outbox?
48. Should the local dev stack use Docker Compose?
49. Should we build cloud-agnostic infrastructure or target AWS/GCP/Azure?

## Compliance

50. Who are the intended users: consumers, licensed agents, internal staff, regulators, auditors?
51. Should every material decision be exportable into a regulator/auditor packet?
52. Should the product/rate/form approval workflow be simulated or real from day one?
53. Should the AI governance framework be built before AI can affect quote decisions?
54. What level of explainability is required for launch?

---

# 15. Recommended First Implementation Path

The strongest implementation path is:

```text
1. Start with product config, rating DSL, quote engine, and risk appetite engine.
2. Add AI agent only as an orchestrator around deterministic tools.
3. Add policy bind flow.
4. Add blockchain policy commitment.
5. Add premium allocation and reserve snapshots.
6. Add claims.
7. Add float/treasury governance.
8. Add reinsurance and advanced portfolio optimization.
```

The key is to avoid building a flashy autonomous agent before the regulated core exists. The first working system should prove:

```text
customer intake
  -> quote
  -> risk appetite decision
  -> policy bind
  -> on-chain commitment
  -> premium allocation
  -> audit trail
```

Once that works, the AI agent becomes powerful because it has safe tools, explicit authority boundaries, deterministic rating logic, and auditable workflows.

[1]: https://content.naic.org/insurance-topics/own-risk-and-solvency-assessment?utm_source=chatgpt.com "Insurance Topics | Own Risk and Solvency Assessment"
[2]: https://content.naic.org/insurance-topics/risk-based-capital?utm_source=chatgpt.com "Insurance Topics | Risk-Based Capital"
[3]: https://content.naic.org/sites/default/files/cmte-h-big-data-artificial-intelligence-wg-ai-model-bulletin.pdf.pdf?utm_source=chatgpt.com "Use of Artificial Intelligence Systems by Insurers"
[4]: https://content.naic.org/industry?utm_source=chatgpt.com "Industry"
[5]: https://content.naic.org/committees/e/statutory-accounting-principles-wg?utm_source=chatgpt.com "Statutory Accounting Principles (E) Working Group"
[6]: https://content.naic.org/insurance-topics/artificial-intelligence?utm_source=chatgpt.com "Insurance Topics | Artificial Intelligence"
