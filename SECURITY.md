# Security Model

## Security Objectives

The system must protect customer data, regulated insurance decisions, treasury assets, smart contract authority, and audit integrity.

## Current Status

This repository is a prototype. The current security controls are a P0 scaffold and are not sufficient for production insurance operations.

## Core Rules

1. No sensitive customer data on-chain.
2. No unaudited AI tool execution.
3. No direct production database access by AI agents.
4. No treasury execution without policy checks and approvals.
5. No smart contract admin actions without multisig or equivalent approval.
6. No policy binding without quote, risk appetite, payment, and authority checks.
7. No claim payout without coverage verification and approval thresholds.

## Development Authentication Contract

The shared `packages/security` package now supports a development bearer-token format so services can enforce deny-by-default role checks while the production identity provider is still pending.

Supported development tokens:

- `Bearer dev:<actor_id>:<ROLE>`
- `Bearer dev:<actor_id>:<ROLE>,<ROLE>`
- `Bearer system:<actor_id>`

This is intentionally a local development contract only. It must be replaced before production use.

## Required Production Authentication Work

Before any production use, replace the development token parser with:

- JWT signature verification.
- Issuer and audience validation.
- Key rotation and JWKS support.
- Tenant and customer ownership checks.
- Centralized authorization policy logging.
- Service-to-service authentication.
- Secrets manager integration.
- Rate limiting and request-size limits.
- PII redaction in logs and traces.
- Audit event persistence.

## Identity and Access

Use RBAC plus ABAC.

### Roles

```text
CUSTOMER
PROSPECT
LICENSED_AGENT
PRODUCER
AGENT
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
SYSTEM
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
customer_owner_id
tenant_id
```

## Endpoint Policy Baseline

- Health endpoints remain unauthenticated.
- Quote creation requires customer, agent, underwriter, admin, or system context.
- Quote recalculation requires agent, underwriter, admin, or system context.
- Quote read and explain endpoints require customer, agent, underwriter, admin, or system context.
- Risk assessment requires agent, underwriter, admin, or system context.
- Runtime risk policy mutation must remain disabled by default and will be replaced by a versioned approval workflow.

## Data Protection

- Encrypt PII at rest.
- Encrypt policy documents and claim evidence.
- Use field-level access controls for sensitive records.
- Store document hashes for verification.
- Use object storage retention policies.
- Maintain access logs for regulated records.
- Separate customer identity from on-chain identifiers.
- Redact PII in application logs.

## AI Agent Security

AI agents must operate through permissioned tools only.

Agents must not:

- Execute raw SQL against production systems.
- Modify rating factors directly.
- Bind policies without authority.
- Approve adverse decisions without review thresholds.
- Execute treasury actions.
- Approve high-value claims.
- Override compliance blocks.
- Push on-chain transactions directly.

Every AI tool call must log actor, tool, input hash, output hash, timestamp, approval state, and correlation ID.

## Non-Production Guards

Until product filing, approval, payment, bind, claims, and compliance workflows exist:

- Do not bind real policies.
- Do not collect real premiums.
- Do not issue real policy documents.
- Do not deny claims.
- Do not store real customer PII.
- Do not deploy contracts to a public chain.
