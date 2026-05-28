# UI Target & Current State — Customer and Admin UIs

Date: 2026-05-28

## Purpose
This document captures the current UI surface, the desired target state for customer-facing and administrative user interfaces, and a prioritized plan to reach that state. It also records AI-agent integration points for product drafting, risk analysis, and claims triage.

## Current State (snapshot)
- `packages/web-ui`: minimal Vite + React scaffold with `App.jsx` showing a demo header. No flows implemented.
- `packages/blockchain-ui`: minimal wallet-connect scaffold with placeholder for contract list.
- `packages/ops-portal`: minimal operations portal scaffold with placeholder for claims management.
- `infra/docker-compose.yml`: includes services and web UI containers for local dev.
- E2E testing scaffold present under `tests/e2e` with a basic Playwright test that verifies frontend title.

## Target State (user-facing)

1) Customer Portal (`web-ui`)
  - Quote flow: form to collect applicant, vehicle, coverage options.
  - Quote results page: show premiums, breakdown, risk drivers, recommended coverages.
  - Purchase/bind: allow customer to purchase and trigger policy issuance (calls `policy-service`).
  - Policy dashboard: list active policies, download policy documents.
  - Customer support: submit claims (creates claim resource) and view claim status.

2) Blockchain Admin (`blockchain-ui`)
  - Wallet connect for admin wallets (MetaMask etc.).
  - Contracts registry: list deployed contracts, addresses, ABIs.
  - Deployment helpers: trigger local test deployments (Hardhat) and capture addresses.
  - Signer management: view and rotate on-chain signers (integration to Vault/KMS for keys).
  - Audit UI: view blockchain events and reconcile with off-chain state.

3) Operations Portal / Claims Handler (`ops-portal`)
  - Claims queue: list claims requiring review with filters (severity, product, date).
  - Claim detail: evidence, claimant info, linked policy, action buttons (triage, escalate, approve, deny, pay).
  - Underwriting tools: view quote risk factors and historical loss data to adjust decisions.
  - Manual policy adjustments: update policy metadata, endorsements.

## AI-Agent Integration Points (future)
- Product analysis agent: on demand, analyze proposed product definitions (rating rules, limits) and produce risk summary, suggested premiums, and draft policy language. Triggered from admin UI during product creation.
- Policy drafting agent: given product template and jurisdiction rules, draft policy terms and generate machine-readable contract fragments for on-chain commitments.
- Claims triage agent: analyze new claims (attachments, reports) and recommend severity score, required evidence, and whether to auto-approve or assign to human.
- Monitoring agent: watch metrics/events and open tickets or notify teams for anomalies (fraud scoring, sharp risk changes).

## Required APIs & Data Contracts
- Quote API: POST `/quotes` -> returns quote id and pricing breakdown.
- Purchase API: POST `/policies` with quote id -> returns policy id and status.
- Claims API: POST `/claims`, GET `/claims/:id`, PATCH `/claims/:id/decision`.
- Contracts API: GET `/contracts`, POST `/contracts/deploy` (CI/ops-only), GET `/events?from=`.
- Admin Auth: OIDC or API token endpoints for session authentication.

## UI Components (high level)
- Shared: Header, Sidebar, Auth, API client wrapper, Toaster/Notifications.
- Web UI: QuoteForm, QuoteResult, PolicyList, PolicyDetail, ClaimCreate, ClaimStatus.
- Ops Portal: ClaimsList, ClaimDetail, ActionBar, CaseNotes, AuditTrail.
- Blockchain UI: ContractsList, ContractDetail, DeployWizard, SignerMgmt, EventExplorer.

## Acceptance Criteria / E2E Scenarios
1. Quote -> Purchase flow
  - User fills QuoteForm, receives QuoteResult, completes purchase, and policy appears in PolicyList.
2. Claim creation -> triage -> assignment
  - Customer submits claim; system enqueues claim; triage agent flags high-risk claims; operations user opens claim detail and executes decision.
3. Contract deploy -> service integration
  - Admin triggers local contract deploy; system captures addresses and services can call deployed contract endpoints in integration tests.

## Prioritized Implementation Roadmap (first 3 sprints)
Sprint 1 (scaffold & core flows)
- Implement QuoteForm and QuoteResult; wire to `quote-service` (or stub) and store quotes locally.
- Implement ClaimsList and ClaimDetail scaffolds; ability to fetch and display claims (stubbed).
- Implement ContractsList and SignerMgmt UI that reads contract addresses from a CI artifact or stub endpoint.

Sprint 2 (integration & auth)
- Wire real APIs (quote → purchase → policy issuance) and implement session/auth.
- Implement basic claims actions (assign, escalate, change status).
- Add local contract deploy action and integrate addresses into `infra/docker-compose.yml` for staging.

Sprint 3 (AI agent hooks & e2e)
- Add UI controls to trigger product analysis agent and display agent output.
- Implement claims triage agent integration and surface recommendations in ClaimDetail.
- Finalize e2e tests covering Quote→Purchase and Claim workflows.

## Current Gaps vs Target (summary)
- No quote form or purchase flow implemented in `web-ui` (gap).
- Claims workflows are placeholders in `ops-portal` (gap).
- Blockchain admin lacks contract listing and deploy/rotation UIs beyond wallet connect (partial gap).
- Auth is unspecified and not implemented (key gap for production readiness).

## Next concrete tasks (short-term)
1. Implement `QuoteForm` and `QuoteResult` in `packages/web-ui` (in progress).
2. Implement `ClaimsList` and `ClaimDetail` in `packages/ops-portal` (in progress).
3. Implement `ContractsList` and `SignerManagement` in `packages/blockchain-ui` (in progress).
4. Add API stubs/mock server for local development to allow full UI testing without backend readiness.
5. Add e2e Playwright flows for the core acceptance criteria.

## Open decisions
- Choose auth mechanism (OIDC vs API tokens).
- Decide on storage for signer keys (Vault/HSM) and how keys are rotated from UI actions.
- UX decisions for claims triage automation and thresholds for auto-approvals.

---
Document saved to session memory and linked to implementation tasks.
