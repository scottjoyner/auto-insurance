# Decision Records

This file indexes major architectural and governance decisions. Detailed ADRs should be added under `docs/decisions/` as implementation begins.

## Initial Decisions

### ADR-0001: Blockchain-first, not blockchain-only

The platform uses blockchain for commitments, attestations, settlement references, governance records, and audit anchors. Regulated workflows and sensitive records remain off-chain.

### ADR-0002: No sensitive insurance data on-chain

Customer PII, policy documents, claim evidence, underwriting evidence, medical data, payment details, and AI conversation logs must remain off-chain. On-chain records should use hashes, commitments, and minimal metadata.

### ADR-0003: Deterministic rating before autonomous AI authority

Quote generation and rating must be deterministic, reproducible, versioned, and testable before AI agents receive higher authority.

### ADR-0004: Human review for restricted decisions

Human review is required for adverse decisions, high-value actions, manual overrides, treasury execution, smart contract administration, claim denials, and other restricted workflows defined in governance policy.

### ADR-0005: Treasury simulation before real execution

The MVP must simulate float and treasury execution. Real-money custody, trading, DeFi, stablecoin, or treasury movement integrations require later governance, legal, accounting, security, and board review.

### ADR-0006: Local EVM before production chain selection

The MVP should use a local EVM chain for smart contract testing and architecture validation before selecting any production network.

## ADR Template

```text
# ADR-NNNN: Title

## Status

Proposed | Accepted | Superseded | Deprecated

## Context

What problem or decision does this address?

## Decision

What did we decide?

## Consequences

What are the tradeoffs, risks, and follow-up actions?
```
