# Execution Plan

## Goal

Move from architecture into an implementation-ready monorepo without creating unsafe shortcuts around AI authority, regulated decisioning, treasury execution, or blockchain privacy.

## Milestone 1: Repo Bootstrap

Tasks:

- Create top-level docs.
- Create HLD and LLD.
- Create governance templates.
- Define first implementation issues.
- Decide first product, jurisdiction, chain target, and service stack.

Exit criteria:

- Documentation is sufficient for a Codex implementation pass.
- Open questions are captured.
- The first MVP boundary is agreed.

## Milestone 2: Shared Schemas and Local Dev

Tasks:

- Add `packages/shared-types`.
- Add `packages/event-schemas`.
- Add `packages/product-config`.
- Add `packages/rating-dsl`.
- Add Docker Compose with PostgreSQL, Redis, Neo4j, MinIO, and local EVM chain.

Exit criteria:

- Local stack boots.
- Shared event envelope validates.
- Sample product config validates.

## Milestone 3: Quote and Risk Core

Tasks:

- Implement quote-service skeleton.
- Implement deterministic rating path.
- Implement risk-appetite-service skeleton.
- Add risk appetite policy loader.
- Add quote-to-risk integration tests.

Exit criteria:

- Sample quote can be generated.
- Risk appetite result is returned.
- Quote snapshot is replayable.

## Milestone 4: Policy Bind and Audit

Tasks:

- Implement policy-service skeleton.
- Add policy lifecycle state machine.
- Add document hash support.
- Add audit event persistence.

Exit criteria:

- Accepted quote can bind.
- Policy version is created.
- Audit packet is generated.

## Milestone 5: Blockchain Commitments

Tasks:

- Add contract workspace.
- Implement PolicyRegistry contract.
- Add blockchain-gateway skeleton.
- Add outbox worker.
- Add reconciliation job.

Exit criteria:

- Policy hash is committed to local chain.
- Chain receipt is indexed.
- Reconciliation report passes.

## Milestone 6: AI Agent Orchestration

Tasks:

- Implement agent session model.
- Add product/rate/form retrieval stubs.
- Add tool permission matrix.
- Connect agent to quote and risk services.
- Add human handoff workflow.

Exit criteria:

- Agent can collect intake and generate a draft quote.
- Agent cannot bind, decline, pay, or execute treasury actions unless explicitly enabled.
- Agent audit log captures tool calls and context.

## Milestone 7: Premium, Reserves, and Treasury Simulation

Tasks:

- Add premium cashflow model.
- Add reserve snapshot model.
- Add treasury policy evaluator.
- Add liquidity ladder.
- Add ReserveAttestation contract skeleton.

Exit criteria:

- Premium allocation can be simulated.
- Reserve snapshot is generated and hashed.
- Treasury proposal is evaluated against policy.

## Milestone 8: Claims MVP

Tasks:

- Implement claims-service skeleton.
- Add FNOL intake.
- Add coverage verification.
- Add evidence metadata and hashing.
- Add reserve and claim decision workflows.

Exit criteria:

- Claim can be created against active policy.
- Coverage check references policy version.
- Claim decision audit packet exists.

## Milestone 9: Compliance Export and Hardening

Tasks:

- Add audit packet export.
- Add model inventory checks.
- Add adverse action reason code registry.
- Add security tests.
- Add compliance tests.

Exit criteria:

- Quote, policy, claim, and treasury audit packets export.
- AI and human decision paths are traceable.
- Security and compliance test suite passes.
