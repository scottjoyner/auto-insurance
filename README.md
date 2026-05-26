# Auto Insurance

Blockchain-first insurance operating system for AI-assisted quoting, risk appetite evaluation, policy creation, claims operations, customer acquisition, client relations, and float/treasury governance.

This repository is the implementation home for a full-stack insurance company architecture. The system is designed around a regulated insurance core with AI orchestration and blockchain auditability.

## Mission

Build a modular platform that can support:

- AI-assisted insurance intake and quote generation.
- Deterministic, reproducible rating and underwriting workflows.
- Risk appetite evaluation based on portfolio, capital, liquidity, and reinsurance constraints.
- Policy binding, issuance, endorsement, renewal, cancellation, and reinstatement.
- Claims FNOL intake, evidence management, reserve setting, decisioning, and payout orchestration.
- Customer acquisition, CRM, retention, and client servicing.
- Premium allocation, reserve tracking, float management, and treasury governance.
- Blockchain commitments for policy, premium, claim, reserve, and governance events.
- Full auditability for compliance, model governance, and regulatory review.

## Core Principle

The blockchain layer is the cryptographic audit and settlement layer. The off-chain platform is the operational and regulated decisioning layer.

Sensitive insurance data, customer PII, policy documents, underwriting evidence, claim evidence, and AI conversation logs should remain off-chain. On-chain state should store commitments, hashes, attestations, approvals, and minimal non-sensitive metadata.

## Initial MVP Goal

The first milestone is an end-to-end quote-to-policy loop:

```text
customer intake
  -> quote generated
  -> risk appetite checked
  -> quote accepted
  -> policy bound
  -> policy hash committed on-chain
  -> premium allocated
  -> audit trail generated
```

## Repo Map

```text
docs/         Architecture, implementation plans, controls, and open questions.
governance/   YAML policy templates for treasury, risk appetite, AI governance, and human review.
services/     Future service implementations.
contracts/    Future smart contract implementations.
packages/     Shared schemas, types, rating DSL, authz, and observability utilities.
infra/        Local dev, Docker, Kubernetes, and Terraform infrastructure.
tests/        Unit, integration, end-to-end, security, compliance, and contract tests.
```

## Current Status

This repository is in the architecture/bootstrap phase. The first implementation should prioritize deterministic quote/risk/policy workflows before introducing high-authority AI automation or real-money treasury execution.

## Recommended Build Order

1. Product configuration schema.
2. Rating DSL.
3. Quote service.
4. Risk appetite service.
5. AI agent orchestrator with limited tool permissions.
6. Policy bind and policy admin service.
7. Blockchain policy registry.
8. Premium allocation and reserve snapshots.
9. Claims MVP.
10. Treasury governance and float management.

## Start Here

- [Architecture](ARCHITECTURE.md)
- [Roadmap](ROADMAP.md)
- [Security](SECURITY.md)
- [Compliance](COMPLIANCE.md)
- [Governance](GOVERNANCE.md)
- [Open Questions](docs/17_open_questions.md)

## Governance Warning

This repository is not legal, actuarial, accounting, tax, or regulatory advice. Any production insurance operation must involve qualified legal, compliance, actuarial, accounting, treasury, and regulatory professionals.