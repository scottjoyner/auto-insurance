# High-Level Design

## Overview

The platform is a blockchain-first, AI-assisted insurance operating system. It supports the full lifecycle from customer acquisition through quote, risk appetite evaluation, policy creation, claims, float management, and audit reporting.

## System Domains

| Domain | Purpose |
| --- | --- |
| Identity and Access | Customers, agents, underwriters, claims, treasury, compliance, auditors, smart contract signers |
| Customer Acquisition | Leads, campaigns, referrals, quote abandonment recovery, lifecycle messaging |
| AI Insurance Agent | Intake, explanation, document collection, routing, support, claim FNOL |
| Quote Engine | Eligibility, rating, quote snapshots, explainability, referral flags |
| Risk Appetite Engine | Accept/refer/decline decisions based on portfolio, capital, and policy constraints |
| Policy Admin | Bind, issue, endorse, renew, cancel, reinstate, document generation |
| Claims | FNOL, evidence, coverage check, reserve, decision, payout |
| Blockchain Core | Policy, premium, claim, reserve, treasury, and governance commitments |
| Float and Treasury | Premium allocation, reserve snapshots, liquidity ladder, investment policy controls |
| Compliance | Human review, adverse action reason codes, AI governance, audit packets |
| Analytics | Loss ratios, quote conversion, portfolio exposure, treasury performance |

## Core Workflows

### Quote to Bind

```text
Lead created
  -> AI agent collects intake
  -> quote service validates product eligibility
  -> quote service calculates premium
  -> risk appetite service evaluates acceptance
  -> customer accepts quote
  -> payment and bind checks run
  -> policy service binds policy
  -> document service generates policy package
  -> blockchain gateway commits policy hash
  -> audit packet is generated
```

### Claims

```text
Claim submitted
  -> AI agent collects FNOL
  -> claims service verifies policy and coverage
  -> evidence is uploaded and hashed
  -> fraud/severity triage runs
  -> reserve is set
  -> adjuster or automated rules decide path
  -> payout approval workflow runs
  -> blockchain gateway commits claim event
  -> claim is closed or reopened
```

### Float and Treasury

```text
Premium received
  -> premium is allocated into accounting buckets
  -> reserves are calculated
  -> liquidity ladder is updated
  -> treasury proposal is created
  -> policy checks run
  -> approval workflow executes
  -> execution is recorded
  -> reserve or treasury attestation is committed on-chain
```

## Deployment Model

Initial deployment should use local infrastructure:

- Docker Compose.
- PostgreSQL.
- Redis.
- Neo4j.
- MinIO.
- Local EVM chain using Anvil or Hardhat.
- FastAPI or TypeScript service skeletons.

Production deployment should later support Kubernetes, managed databases, KMS, secrets management, and observability.

## MVP Boundary

The MVP should include:

- sample product
- quote service
- risk appetite service
- policy bind service
- blockchain policy commitment
- audit event model
- governance YAML files

The MVP should not include:

- unrestricted AI binding authority
- real-money treasury execution
- production multi-state filing support
- public customer data on-chain
- automated high-value claim payments
