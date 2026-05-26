# Data Model

## Purpose

This document defines the initial canonical entities for the insurance operating system. The system should separate operational records, graph relationships, documents, vector memory, analytics, and blockchain commitments.

## Storage Layers

| Store | Purpose |
| --- | --- |
| PostgreSQL | Operational truth for quotes, policies, claims, payments, approvals, audit records |
| Neo4j | Relationship graph for risk, fraud, exposure, customers, policies, claims, counterparties |
| Object storage | Policy PDFs, claim evidence, underwriting documents, generated reports |
| Vector store | Product knowledge, customer support retrieval, underwriting guidance, internal docs |
| Event log | Immutable domain events and workflow state transitions |
| Blockchain | Hash commitments, attestations, approvals, and settlement references |
| Warehouse | Analytics, actuarial reporting, portfolio risk, financial reporting |

## Core Relational Entities

```text
Party
Customer
Lead
Producer
Agent
Consent
CommunicationPreference
Product
ProductVersion
Coverage
RatePlan
Quote
QuoteVersion
QuoteInputSnapshot
RiskAssessment
Policy
PolicyVersion
PolicyCoverage
PolicyDocument
Claim
ClaimEvidence
ClaimReserve
ClaimDecision
Payment
PremiumAllocation
ReserveSnapshot
TreasuryProposal
TreasuryApproval
TreasuryExecution
BlockchainTransaction
AuditEvent
AIInteraction
ModelVersion
ComplianceReview
```

## Suggested Entity Ownership

| Entity | Owning Service |
| --- | --- |
| Lead | crm-service |
| Customer | crm-service |
| Consent | crm-service |
| ProductVersion | quote-service / product-config package |
| Quote | quote-service |
| RiskAssessment | risk-appetite-service |
| Policy | policy-service |
| Claim | claims-service |
| Payment | treasury-service or billing module |
| ReserveSnapshot | treasury-service |
| BlockchainTransaction | blockchain-gateway |
| AIInteraction | ai-agent-orchestrator |
| ComplianceReview | compliance-service |
| AuditEvent | shared audit/event layer |

## Neo4j Graph Model

### Node Labels

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

### Relationship Types

```text
(:Customer)-[:OWNS_POLICY]->(:Policy)
(:Policy)-[:HAS_COVERAGE]->(:Coverage)
(:Policy)-[:INSURES]->(:Property)
(:Policy)-[:INSURES]->(:Vehicle)
(:Claim)-[:FILED_UNDER]->(:Policy)
(:Claim)-[:HAS_EVIDENCE]->(:Document)
(:Customer)-[:USES_WALLET]->(:Wallet)
(:Quote)-[:EVALUATED_BY]->(:Model)
(:Policy)-[:LOCATED_IN]->(:Jurisdiction)
(:RiskFactor)-[:AFFECTS]->(:Quote)
(:Producer)-[:SOLD]->(:Policy)
(:Policy)-[:CEDED_TO]->(:Reinsurer)
(:Payment)-[:ALLOCATED_TO]->(:ReserveSnapshot)
(:Counterparty)-[:HOLDS_ASSET]->(:TreasuryExecution)
```

## Identifier Strategy

Use stable opaque IDs:

```text
lead_*
customer_*
quote_*
risk_*
policy_*
claim_*
payment_*
reserve_*
treasury_*
chain_tx_*
audit_*
```

Do not use PII-derived identifiers.

## Hashing Strategy

Canonical records that are committed on-chain should be serialized deterministically and hashed.

Hash candidates:

- policy document package
- quote input snapshot
- claim evidence manifest
- reserve snapshot
- treasury proposal
- governance approval

## Data Privacy Rules

- Do not store PII on-chain.
- Do not store raw secrets in databases.
- Encrypt sensitive fields at rest.
- Use object storage encryption for documents and evidence.
- Maintain retention policies by entity type.
- Log every access to sensitive documents.
