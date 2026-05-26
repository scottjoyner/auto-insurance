# Float and Treasury Management

## Purpose

The float and treasury system controls premium allocation, reserves, liquidity, investable surplus, and treasury proposals. It must prioritize solvency, liquidity, and governance before yield.

## Core Principle

Float is not free capital. Premiums must be segmented into earned premium, unearned premium reserve, loss reserve, loss adjustment expense reserve, operating capital, restricted capital, and investable surplus according to approved policy.

## Premium Allocation

```text
Premium received
  -> payment reconciled
  -> earned/unearned split calculated
  -> reserve buckets updated
  -> liquidity ladder updated
  -> investable surplus calculated
  -> treasury policy evaluated
  -> audit event emitted
```

## Reserve Buckets

```text
unearned_premium_reserve
loss_reserve
loss_adjustment_expense_reserve
reinsurance_payable
operating_capital
restricted_capital
investable_surplus
```

## Treasury Policy

Treasury policy should be loaded from:

```text
governance/treasury_policy.yml
```

The policy should define:

- allowed assets
- prohibited assets
- minimum liquidity
- max duration
- max counterparty exposure
- max stablecoin exposure
- approval thresholds
- emergency freeze conditions
- mark-to-market frequency
- reserve segregation rules

## Treasury Proposal Flow

```text
proposal created
  -> policy validation
  -> liquidity impact analysis
  -> reserve impact analysis
  -> counterparty exposure check
  -> approval routing
  -> execution authorization
  -> execution record
  -> reserve/treasury attestation
```

## Required Controls

- No treasury execution without policy validation.
- No policy exception without approval.
- No high-value action without human review.
- No disallowed asset or counterparty.
- No movement that violates liquidity or reserve limits.
- No direct AI execution of treasury transactions.

## Service Responsibilities

`treasury-service` should provide:

```http
POST /treasury/premium-received
POST /treasury/reserve-snapshots
GET /treasury/liquidity-ladder
POST /treasury/proposals
POST /treasury/proposals/{proposal_id}/approve
POST /treasury/proposals/{proposal_id}/execute
GET /treasury/solvency-dashboard
```

## Reserve Attestation

Reserve snapshots should be hashed and optionally committed on-chain through `ReserveAttestation`.

A reserve snapshot should include:

- snapshot ID
- timestamp
- methodology version
- reserve buckets
- asset position summary
- liabilities summary
- liquidity ladder
- policy compliance result
- approving actor

## MVP Boundary

Initial implementation should simulate treasury only.

MVP should not execute real trades, DeFi transactions, custodian transfers, or production stablecoin movements. It should create proposals, evaluate them against policy, require approvals, and record simulated execution.
