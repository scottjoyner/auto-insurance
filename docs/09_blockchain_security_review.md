# Blockchain Contract Security Review

Owner: Smart Contract / Security Lead  
Audience: engineering, security, smart-contract signers, compliance  
Last reviewed: 2026-05-29  
Status: required pre-deployment audit checklist

## Current repository inventory

Repository search did not surface committed Solidity or Hardhat contract source files at the time this document was written. Earlier planning references mentioned `PolicyRegistry` and `AuditEventRegistry`, but those contracts must be treated as unverified until source code is committed, tested, and audited.

No public-chain deployment is approved from this repository until the checklist below is completed.

## Approved blockchain scope

Allowed MVP scope:

- local development chain only
- audit event commitment
- policy commitment hash registry
- no customer wallet exposure
- no tokenized policy ownership
- no premium custody
- no claim payout custody
- no treasury custody

Prohibited until later review:

- public-chain deployment
- upgradeable proxy deployment
- custody of funds
- automatic claims payouts
- customer self-custody requirements
- policy NFTs
- oracle-controlled bind/claim execution

## Threat model

### Assets

- policy commitment hashes
- audit event hashes
- signer keys
- deployment keys
- admin role keys
- bridge/oracle credentials if introduced
- off-chain policy and claim records referenced by hashes

### Threat actors

- external attackers
- malicious insiders
- compromised signer
- compromised deployer
- compromised CI runner
- compromised RPC endpoint
- malicious oracle or indexer
- accidental admin misuse

### Critical risks

- unauthorized contract admin action
- event tampering or replay
- incorrect commitment hash
- chain reorg assumptions
- signer key compromise
- unbounded role permissions
- upgradeable contract abuse
- missing pause/emergency controls
- weak access control
- deployment to wrong chain
- leaking PII on-chain

## Contract design requirements

Contracts must:

1. Store only hashes or opaque IDs, never PII.
2. Enforce role-based access control.
3. Emit events for every state-changing action.
4. Support deterministic off-chain replay from event logs.
5. Prevent duplicate commitment IDs unless explicitly versioned.
6. Include chain ID and contract address in off-chain signed payload domain separation.
7. Use reviewed OpenZeppelin primitives where applicable.
8. Avoid custom cryptography.
9. Avoid arbitrary external calls.
10. Avoid fund custody unless separately reviewed.

## Required tests before audit

- unit tests for every public/external function
- unauthorized caller tests
- duplicate/replay tests
- event emission tests
- invalid input tests
- boundary tests
- chain ID/domain separation tests
- deployment script tests
- gas snapshot for common paths
- fork/local-chain smoke test

## Static analysis checklist

Run and archive output for:

```bash
slither .
solhint 'contracts/**/*.sol'
npm audit
npm test
npx hardhat test
npx hardhat coverage
```

If Foundry is used:

```bash
forge test
forge coverage
forge snapshot
```

## Manual audit checklist

### Access control

- Every state-changing method has explicit authorization.
- Admin roles are least privilege.
- Role grant/revoke paths are controlled.
- No public initializer remains callable after deployment.
- Ownership cannot be accidentally renounced unless intentional and documented.

### Data exposure

- No names, addresses, VINs, phone numbers, emails, policy details, claim descriptions, or payment details are stored on-chain.
- Hash inputs are canonicalized and documented.
- Hash preimage data is stored off-chain in auditable systems.

### Replay and uniqueness

- Commitment IDs are unique.
- Event IDs are unique.
- Replays either fail or create explicit new versions.
- Off-chain signatures include nonce, chain ID, contract address, and expiry.

### Upgradeability

If upgradeability is used:

- proxy admin is multisig-controlled
- implementation initialization is locked
- storage layout is tested
- upgrade process requires change approval
- rollback process is documented

If upgradeability is not used:

- migration process is documented
- contract versioning is explicit

### Operational safety

- Deployment scripts verify chain ID.
- Deployment scripts verify expected deployer.
- Admin actions require multisig or equivalent approval.
- Emergency pause path exists if contract has operational risk.
- Signer key rotation procedure exists.

## Deployment gate

No deployment beyond local Anvil is permitted until:

- source code is committed
- tests pass
- static analysis passes or findings are triaged
- manual audit checklist is completed
- deployment runbook is completed
- signer key management is documented
- compliance confirms no PII goes on-chain
- smart-contract signer approves deployment

## Required audit artifact format

Each contract audit must produce:

- contract name and commit SHA
- compiler version
- dependency versions
- deployment network target
- test command output summary
- static analysis output summary
- findings by severity: critical, high, medium, low, informational
- remediation commit references
- final approval decision

## Finding severity definitions

Critical: loss of funds, unauthorized admin, permanent corruption, public PII exposure.  
High: privilege escalation, replay vulnerability, broken access control.  
Medium: incorrect event commitment, operational bypass, missing important validation.  
Low: documentation mismatch, weak error messages, non-critical gas issue.  
Informational: style, maintainability, developer experience.

## Open action items

1. Commit actual contract source files or remove blockchain scope from MVP docs.
2. Add contract-specific tests.
3. Add static analysis workflow.
4. Add deployment script guardrails.
5. Add signer key management runbook.
6. Complete first contract audit artifact.
