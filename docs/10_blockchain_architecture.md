# Blockchain Architecture

## Purpose

The blockchain layer provides cryptographic commitments, settlement attestations, governance records, and tamper-evident audit anchors. It should not store sensitive insurance data directly.

## Design Rule

Blockchain-first does not mean putting all insurance data on-chain. The chain should store hashes, commitments, attestations, approvals, and minimal metadata. Operational systems remain the system of record for regulated workflows and sensitive data.

## On-Chain Objects

| Object | Representation |
| --- | --- |
| Policy | Policy commitment hash, product version hash, lifecycle status |
| Premium | Payment commitment, allocation hash, asset reference |
| Claim | Claim commitment hash, decision commitment, payout authorization |
| Reserve | Reserve snapshot Merkle root, methodology hash, timestamp |
| Treasury | Policy compliance proof, movement attestation, approval reference |
| Governance | Parameter updates, signer changes, emergency pauses, contract upgrades |

## Off-Chain Objects

Do not store these on-chain:

- customer names
- addresses
- phone numbers
- emails
- SSNs
- driver's license numbers
- policy PDFs
- claim photos or evidence
- underwriting documents
- medical information
- full AI conversations
- payment account details

## Initial Contracts

```text
PolicyRegistry
PremiumEscrow
ClaimsEscrow
ReserveAttestation
TreasuryPolicy
GovernanceMultisig
OracleRegistry
AuditEventRegistry
```

## PolicyRegistry Responsibilities

- Register policy commitment.
- Store product/rate/form version hash.
- Store effective and expiration timestamps.
- Update policy status.
- Emit lifecycle events.

## PremiumEscrow Responsibilities

- Record premium receipt commitment.
- Record allocation hash.
- Support reconciliation with payment processor or stablecoin transfer.

## ClaimsEscrow Responsibilities

- Register claim commitment.
- Record claim decision commitment.
- Record payout approval commitment.
- Record paid status.

## ReserveAttestation Responsibilities

- Publish reserve snapshot Merkle roots.
- Reference methodology hash.
- Identify authorized attestor.
- Support audit reconciliation.

## Blockchain Gateway

All chain writes should flow through `services/blockchain-gateway`.

The gateway must:

- validate payloads
- enforce signer policy
- write outbox rows
- submit transactions
- index receipts
- support retries
- reconcile on-chain state
- expose transaction status

## Idempotent Chain Write Flow

```text
off-chain workflow event
  -> canonical hash generated
  -> outbox event written
  -> blockchain worker submits transaction
  -> transaction receipt indexed
  -> source record updated
  -> reconciliation job verifies contract state
```

## Development Target

Initial development should use a local EVM chain:

- Anvil or Hardhat node.
- Foundry or Hardhat tests.
- Local test accounts only.
- No production network until governance and security reviews are complete.

## Testing Requirements

- Contract access control tests.
- PII exclusion tests.
- Idempotent retry tests.
- Reconciliation tests.
- Emergency pause tests.
- Signer rotation tests.
