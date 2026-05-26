# Architecture Overview

## System Intent

Auto Insurance is a blockchain-first, AI-assisted insurance operating system. The architecture separates regulated operational decisioning from cryptographic audit, settlement, and commitment infrastructure.

## Architectural Principles

1. Deterministic insurance decisions before autonomous AI decisions.
2. Blockchain commitments for auditability, not public exposure of sensitive data.
3. Every quote, bind, claim, reserve, and treasury movement must be reproducible.
4. Human review gates must exist for regulated, adverse, high-risk, and high-value actions.
5. All AI actions must be tool-scoped, permissioned, and logged.
6. Product, rate, form, and jurisdiction metadata must be versioned.
7. Float management must obey a treasury policy, liquidity ladder, and approval workflow.

## Logical Architecture

```text
[Web App / Agent Portal / Admin Console]
              |
              v
[AI Agent Orchestrator]
              |
              +--> [CRM Service]
              +--> [Quote Service]
              +--> [Risk Appetite Service]
              +--> [Policy Service]
              +--> [Claims Service]
              +--> [Treasury Service]
              +--> [Compliance Service]
              +--> [Document Service]
              |
              v
[Event Bus / Workflow Engine / Audit Log]
              |
              +--> [PostgreSQL Operational Store]
              +--> [Neo4j Risk and Relationship Graph]
              +--> [Object Storage]
              +--> [Vector Store]
              +--> [Analytics Warehouse]
              |
              v
[Blockchain Gateway]
              |
              +--> [PolicyRegistry]
              +--> [PremiumEscrow]
              +--> [ClaimsEscrow]
              +--> [ReserveAttestation]
              +--> [TreasuryPolicy]
              +--> [GovernanceMultisig]
```

## Core Services

| Service | Purpose |
| --- | --- |
| ai-agent-orchestrator | Conversational intake, tool orchestration, quote explanation, human handoff |
| quote-service | Product eligibility, deterministic rating, quote snapshots, explainability |
| risk-appetite-service | Portfolio, capital, reserve, geography, and reinsurance gating |
| policy-service | Bind, issue, endorse, renew, cancel, reinstate, verify coverage |
| claims-service | FNOL, evidence, coverage checks, reserves, decisions, payouts |
| crm-service | Leads, customers, touchpoints, campaigns, retention, service cases |
| treasury-service | Premium allocation, reserve snapshots, liquidity ladder, float policy |
| blockchain-gateway | Idempotent chain writes, receipt indexing, reconciliation |
| compliance-service | Review gates, adverse action reasons, audit packets, model governance |
| document-service | Policy documents, claim evidence, retention, hash generation |

## On-Chain vs Off-Chain Split

### On-chain

- Policy hash commitments.
- Premium payment commitments.
- Claim event commitments.
- Payout approval commitments.
- Reserve attestation hashes.
- Treasury governance approvals.
- Oracle attestations.
- Emergency pause and upgrade events.

### Off-chain

- Customer PII.
- Full policy documents.
- Underwriting evidence.
- Claim evidence.
- Payment account data.
- AI conversation logs.
- Rating model details.
- Actuarial assumptions.
- Internal treasury books.

## First End-to-End Milestone

```text
Lead created
  -> AI intake starts
  -> quote request created
  -> quote generated
  -> risk appetite evaluated
  -> quote accepted
  -> policy bound
  -> policy document hash generated
  -> policy commitment recorded on-chain
  -> premium allocation recorded
  -> audit packet generated
```

## Non-Goals for Initial MVP

- Real-money treasury execution.
- Unrestricted AI policy binding.
- Fully automated claim payout without thresholds.
- Multi-state production filing support.
- Public exposure of customer policy data on-chain.
- Complex DeFi float strategies.
