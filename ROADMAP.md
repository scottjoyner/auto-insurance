# Roadmap

## Phase 0: Architecture Bootstrap

Deliverables:

- README landing page.
- Architecture overview.
- High-level design.
- Low-level design.
- Execution plan.
- Compliance, security, and governance documents.
- Initial policy YAML templates.

Acceptance criteria:

- Repo communicates scope and boundaries.
- Build sequence is obvious.
- Open questions are documented.
- Initial Codex implementation prompts can target specific files.

## Phase 1: Product Config and Rating DSL

Deliverables:

- Product configuration schema.
- Sample product config.
- Rating DSL design.
- Quote input/output schemas.
- Deterministic premium calculation tests.

Acceptance criteria:

- A sample product can be rated reproducibly.
- Every quote references product, rate, form, and jurisdiction versions.
- Rating snapshots can be replayed.

## Phase 2: Quote Service

Deliverables:

- quote-service skeleton.
- Quote creation endpoint.
- Quote recalculation endpoint.
- Quote expiration handling.
- Quote explainability package.
- Referral flag output.

Acceptance criteria:

- A quote can be generated from sample applicant data.
- Quote output contains premium, factors, reason codes, and bind eligibility.
- Quote result is deterministic for identical input snapshots.

## Phase 3: Risk Appetite Service

Deliverables:

- risk-appetite-service skeleton.
- Risk appetite policy config.
- Exposure concentration checks.
- Capital and reserve impact stubs.
- Reinsurance capacity stubs.

Acceptance criteria:

- Service returns ACCEPT, REFER, DECLINE, REQUEST_MORE_INFO, or ACCEPT_WITH_LIMITS.
- Decision output includes reason codes and audit metadata.
- Risk appetite policy can be changed without code edits.

## Phase 4: AI Agent Orchestrator

Deliverables:

- Tool-scoped AI agent shell.
- Agent session model.
- Retrieval hooks for product and policy knowledge.
- Tool permission matrix.
- Human handoff workflow.

Acceptance criteria:

- Agent can collect intake and call quote tools.
- Agent cannot bind, decline, pay claims, or execute treasury actions unless explicitly permitted.
- All tool calls and retrieved context are logged.

## Phase 5: Policy Admin and Bind Flow

Deliverables:

- policy-service skeleton.
- Quote acceptance flow.
- Bind request flow.
- Policy lifecycle state machine.
- Policy document hash generation.

Acceptance criteria:

- Accepted quote can produce a bound policy.
- Policy state transitions are auditable.
- Policy documents are versioned and hashable.

## Phase 6: Blockchain Commitments

Deliverables:

- Foundry or Hardhat contract workspace.
- PolicyRegistry contract.
- blockchain-gateway service skeleton.
- Outbox pattern for chain writes.
- Receipt indexing and reconciliation job.

Acceptance criteria:

- Policy commitment can be recorded on a local chain.
- Chain write is idempotent.
- Off-chain and on-chain policy commitment states can be reconciled.

## Phase 7: Premium Allocation and Reserve Snapshots

Deliverables:

- premium cashflow model.
- earned/unearned premium allocation model.
- reserve snapshot schema.
- ReserveAttestation contract skeleton.

Acceptance criteria:

- Premium can be allocated across reserve buckets.
- Reserve snapshot can be created and hashed.
- Reserve hash can be committed on-chain.

## Phase 8: Claims MVP

Deliverables:

- claims-service skeleton.
- FNOL intake.
- Coverage verification.
- Evidence metadata model.
- Reserve setting workflow.
- Claim decision workflow.

Acceptance criteria:

- Claim can be created against a policy.
- Coverage check references the policy version.
- Claim decision is auditable.

## Phase 9: Treasury Governance

Deliverables:

- treasury-service skeleton.
- Treasury policy engine.
- Liquidity ladder model.
- Proposal/approval workflow.
- TreasuryPolicy contract skeleton.

Acceptance criteria:

- Treasury proposal is evaluated against policy.
- High-value actions require approval.
- Disallowed assets, protocols, or counterparties are blocked.

## Phase 10: Compliance and Audit Packets

Deliverables:

- Compliance control matrix.
- AI model inventory.
- Adverse action reason code registry.
- Regulatory/auditor export packet design.

Acceptance criteria:

- Each material decision has an audit trail.
- Each AI action has model/tool/context traceability.
- Compliance can export a quote/policy/claim review packet.
