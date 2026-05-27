# Open Design Questions — Resolved

This file tracks answers to the open design questions. Original questions are numbered; resolutions are appended below.

## Product and Company Scope

### Q1: What is the first insurance product line?
**A: Personal auto insurance (sample product only).**
- Chosen because: universal need, well-understood rating factors, clear regulatory framework to model, large addressable market for validation.
- The sample product will model a standard personal auto policy with liability, collision, and comprehensive coverage options.
- Not a real filed product. All values are architecture test data.

### Q2: Is the target structure a carrier, MGA, captive, protocol, or architecture prototype?
**A: Architecture prototype / MGA-style operating layer.**
- The system is designed as an MGA-style operating layer that could sit under a real carrier or captive.
- MVP targets the MGA use case: AI-assisted intake, deterministic rating, policy binding, and claims intake.
- Blockchain layer provides audit/commitment infrastructure that could be deployed under a real carrier license later.
- Explicitly NOT a standalone carrier in MVP. No real underwriting authority, no regulatory filings.

### Q3: What jurisdiction should the MVP model first?
**A: North Carolina (NC) — SAMPLE jurisdiction code.**
- NC has clear, well-documented auto insurance regulations.
- Moderate regulatory complexity (not as simple as WY, not as complex as CA).
- The sample product will use `SAMPLE` as the jurisdiction code throughout all docs and configs.
- All regulatory references will be NC-specific in architecture notes.

### Q4: Should the first product be admitted, surplus lines, parametric, captive, or a non-production sample product?
**A: Non-production sample product (status: `architecture_sample_only`).**
- This is an architecture prototype, not a regulatory product.
- The sample product will be modeled on NC personal auto with realistic but fictional rating data.
- Status transitions: `draft` -> `architecture_sample_only` -> `internal_review` -> `approved_for_testing` -> `approved_for_production` (future).

### Q5: Should the system support direct-to-consumer only, or brokers and producers too?
**A: Direct-to-consumer only for MVP.**
- MVP targets: customer (prospect) -> AI intake -> quote -> bind.
- Broker/producer channel is Phase 2+ scope.
- CRM service will track leads and campaigns but not broker relationships in MVP.

## Blockchain Strategy

### Q6: Should the MVP use public chain, permissioned EVM, appchain, or local-only EVM?
**A: Local-only EVM (Anvil) for MVP. No public chain deployment.**
- MVP blockchain scope: policy commitment hash + audit event log on local chain.
- PolicyRegistry and AuditEventRegistry contracts only for MVP.
- Other contracts (PremiumEscrow, ClaimsEscrow, ReserveAttestation, TreasuryPolicy, GovernanceMultisig, OracleRegistry) are Phase 4+ scope.
- Production chain selection requires: security review, governance approval, legal review, compliance sign-off.

### Q7: Should customers use wallets directly or should wallet abstraction hide blockchain details?
**A: Wallet abstraction for MVP.**
- Customers do NOT interact with wallets directly.
- Blockchain operations are handled by the blockchain-gateway service.
- Policy commitments are written by the policy-service via the gateway.
- Wallet abstraction layer handles: key management, transaction signing, receipt indexing.
- Customer-facing: policy number, coverage details, claim status. No blockchain terminology.

### Q8: Should policies be registry records, NFTs, soulbound attestations, or another structure?
**A: Registry records (not NFTs) for MVP.**
- Policies are hash commitments stored in PolicyRegistry, not NFTs.
- Rationale: insurance policies are not transferable like NFTs. They have endorsements, cancellations, and regulatory constraints.
- Registry record structure: `{policy_id, hash, product_version, status, committed_at, committed_by}`.
- Status transitions are tracked via events, not token transfers.

### Q9: Should premiums support fiat only, stablecoin only, or both?
**A: Fiat only for MVP. Stablecoin support is Phase 5+ scope.**
- MVP premium flow: payment confirmation (stubbed) -> premium allocation -> audit event.
- No real payment processing in MVP. Payment integration is a stub.
- Stablecoin support requires: legal review, treasury policy update, smart contract changes, compliance sign-off.

### Q10: Should claim payouts support fiat only, stablecoin only, or both?
**A: Fiat only for MVP. No real payouts in MVP.**
- MVP claims: FNOL intake, coverage check stub, reserve calculation stub, decision workflow stub.
- No payout execution in MVP. Payout is a stub that emits an audit event.
- Real payout integration requires: claims authority review, treasury policy update, payment processor integration.

### Q11: What testnet or local chain should be targeted first?
**A: Local Anvil chain (hardhat/node). No testnet deployment for MVP.**
- `infra/docker-compose.yml` will include an Anvil service on port 8545.
- Contract deployment scripts target `http://localhost:8545`.
- Testnet deployment is Phase 4+ scope.

### Q12: Should governance be traditional, on-chain, or hybrid?
**A: Traditional governance for MVP. On-chain governance is Phase 4+ scope.**
- MVP governance: YAML policy files, audit packets, human review workflows.
- GovernanceMultisig and TreasuryPolicy contracts are Phase 4+ scope.
- Hybrid governance (traditional + on-chain verification) is the long-term target.

## AI Agent Authority

### Q13: Can the AI agent bind policies within strict rules, or only prepare bind requests?
**A: AI agent prepares bind requests only. Human approval required for bind.**
- AI authority: collect intake, generate quote, evaluate risk appetite, explain results, prepare bind request.
- AI restriction: cannot execute bind. Bind requires human approval for all MVP policies.
- Human review threshold: all binds require UNDERWRITER_L1 approval in MVP.
- Future scope: AI bind authority with strict rules (low-risk products, verified applicants, automated risk appetite ACCEPT).

### Q14: Can the AI agent decline risks, or only refer them for human review?
**A: AI agent can only REFER risks. Human decides decline.**
- AI output for adverse decisions: `REFER_TO_UNDERWRITER` with reason codes.
- Underwriter reviews the referral and decides: ACCEPT, ACCEPT_WITH_LIMITS, or DECLINE.
- Rationale: adverse action decisions require licensed human review in all jurisdictions.
- AI can recommend decline with reason codes, but the final decision is human.

### Q15: Which actions always require licensed human approval?
**A: All bind decisions, all adverse decisions, all claim denials, all rating overrides.**
- Policy bind: UNDERWRITER_L1 (all cases in MVP).
- Risk decline: UNDERWRITER_L2 (all cases in MVP).
- Claim denial: CLAIMS_MANAGER (all cases in MVP).
- Rating override: UNDERWRITER_L1 with documented reason.
- Treasury action: TREASURY_APPROVER (all cases).
- Smart contract admin: SMART_CONTRACT_SIGNER (multisig).

### Q16: Should customer communication include web chat, email, SMS, and voice?
**A: Web chat (HTTP API) only for MVP.**
- MVP communication channel: HTTP API endpoint for web chat.
- Email, SMS, and voice are Phase 3+ scope.
- Communication preferences are tracked in the CRM service (entity: `CommunicationPreference`).
- Consent management is tracked (entity: `Consent`).

### Q17: What is the retention policy for AI conversation logs?
**A: 7 years for MVP. Configurable via governance policy.**
- AI conversation logs are retained for 7 years (matches standard insurance record retention).
- Logs are stored in object storage with metadata in PostgreSQL.
- Logs include: session ID, actor ID, model version, prompt version, retrieved context, tool calls, response, audit metadata.
- Logs are NOT stored on-chain. Only hash commitments are stored.
- Retention policy is configurable via `governance/ai_model_inventory.yml`.

## Underwriting and Pricing

### Q18: Should rating be deterministic rule-based, ML-based, or hybrid?
**A: Deterministic rule-based for MVP. ML-based is Phase 4+ scope.**
- MVP rating: YAML-based rating DSL with factor tables, eligibility rules, and premium calculation.
- Rating DSL supports: categorical variables, numeric variables, interaction terms, discounts, surcharges.
- ML-based rating requires: model governance approval, regulatory filing, validation testing.
- AI agent can explain deterministic rating but cannot modify rating logic.

### Q19: Should third-party data (credit, MVR, telematics) be integrated in MVP?
**A: No third-party data in MVP. All inputs are self-reported.**
- MVP applicant inputs: age, ZIP code, vehicle age, driving history (self-reported).
- Third-party data integration is Phase 3+ scope.
- Integration targets: MVR (motor vehicle record), credit-based insurance score, telematics.
- Each integration requires: vendor contract, privacy review, compliance sign-off.

### Q20: What is the MVP premium range for the sample product?
**A: $500-$2,500/year for sample personal auto.**
- Base rate: $500/year (architecture test value).
- Rating variables: vehicle age band, deductible level, driver age band, ZIP code factor.
- Sample product will produce premiums in the $500-$2,500 range for test scenarios.
- All values are architecture test data, not real rates.

## Additional Decisions

### Q21: What service stack should be used?
**A: Python (FastAPI) for MVP services. TypeScript/Node.js for blockchain gateway.**
- Services: Python 3.12+, FastAPI, SQLAlchemy, Pydantic v2.
- Shared types: Python dataclasses with Pydantic validation.
- Blockchain gateway: TypeScript, ethers.js, Hardhat.
- Event processing: Python with async event handlers.
- Testing: pytest, hypothesis (property-based), pytest-asyncio.
- Docker: docker-compose for local dev, individual Dockerfiles per service.

### Q22: What is the MVP implementation sequence?
**A: Quote service -> Risk appetite service -> Policy service (bind flow) -> Blockchain gateway.**
- Milestone 1: Shared types, event schemas, product config, rating DSL, local infra.
- Milestone 2: Quote service with deterministic rating.
- Milestone 3: Risk appetite service with YAML policy loading.
- Milestone 4: Policy service with bind flow and audit events.
- Milestone 5: Blockchain gateway with PolicyRegistry on local chain.
- Milestone 6: AI agent orchestrator with tool permissions.
- Milestone 7: Claims service (MVP scope: FNOL + coverage check).
- Milestone 8: Treasury service (MVP scope: premium allocation stub).
