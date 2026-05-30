# Production UI Design Specification

Owner: Product Design and Platform Engineering  
Audience: product, design, frontend engineering, backend engineering, compliance, operations  
Last reviewed: 2026-05-29  
Status: active design target

## Purpose

This document defines the production UI vision for the insurance operating system. The current repository is backend-heavy and does not yet have a complete frontend implementation. This specification turns the product vision into concrete user surfaces, navigation, screens, workflows, state requirements, and API integration targets.

## Design principles

1. **Human approval first**: any material insurance decision must clearly show who approved it and why.
2. **Audit visible by default**: every quote, risk decision, bind request, policy, claim, reserve, and notice needs a timeline.
3. **No hidden AI authority**: AI suggestions must be visually labeled as suggestions and must never appear as final approvals.
4. **Explainability is a product surface**: rating factors, risk appetite triggers, referral reasons, reserve recommendations, and claim routing must be understandable.
5. **PII minimization**: only show sensitive data when needed for role-authorized workflows.
6. **Queue-driven operations**: staff should work from queues, not raw database lists.
7. **Exception-first dashboards**: surface blocked binds, referrals, missing evidence, expired quotes, reserve approvals, denied-review drafts, and compliance deadlines.

## Applications

### 1. Customer Portal

Purpose: customer-facing self-service.

Primary navigation:

- Home
- Get a quote
- My quotes
- Policies
- Claims
- Documents
- Messages
- Profile

Core screens:

#### Customer home

Cards:

- active policies
- open claims
- pending quote actions
- unread messages
- required documents

#### Quote intake

Steps:

1. Applicant information
2. Vehicle/property information
3. Coverage choices
4. Review inputs
5. Quote result
6. Next action: save, ask questions, contact agent, or request bind

Required UI states:

- draft
- validating
- quoted
- referral required
- quote expired
- bind not eligible

#### Quote result

Must show:

- total premium
- coverage breakdown
- deductibles
- reason codes
- discounts/surcharges
- expiration date
- explainability panel
- customer-friendly caveat: quote is not bound until approved

#### Policy view

Must show:

- policy ID
- term dates
- coverages
- documents
- billing/payment placeholder
- claim creation entry point
- event/audit timeline simplified for customer

#### Claim FNOL

Steps:

1. Select policy
2. Loss date/time/location
3. Loss type
4. What happened
5. Injuries/police report indicators
6. Upload evidence metadata/files
7. Review and submit

#### Claim detail

Must show:

- claim status
- claim queue/customer-facing stage
- assigned team/next step
- evidence checklist
- messages
- timeline

### 2. Agent Desktop

Purpose: agent-assisted quote, customer, and bind preparation.

Primary navigation:

- Search
- Customers
- Quotes
- Referrals
- Bind requests
- Documents
- Messages

Core screens:

#### Customer 360

Tabs:

- overview
- quotes
- policies
- claims
- documents
- messages
- audit timeline

#### Agent quote workspace

Panels:

- intake form
- quote result
- explainability
- underwriting referral reasons
- missing information
- customer communication draft

#### Bind preparation

Must show:

- quote snapshot
- risk assessment snapshot
- bind eligibility
- compliance guard result
- required documents
- idempotency/request key
- submit-to-underwriter button

### 3. Underwriter Console

Purpose: risk appetite, referrals, bind approvals, and decline review.

Primary navigation:

- Work queue
- Risk appetite
- Quote referrals
- Bind approvals
- Decline review
- Policy activity
- Audit exports

Core screens:

#### Underwriting queue

Columns:

- age/time in queue
- customer/agent
- quote ID
- product/jurisdiction
- premium
- risk score
- referral reason
- status
- assigned underwriter

Filters:

- jurisdiction
- product
- risk level
- referral reason
- age/SLA
- assigned to me

#### Risk assessment detail

Must show:

- quote snapshot
- risk score
- risk level
- triggered rules
- capital impact
- reinsurance impact
- reason codes
- risk policy version
- decision history

#### Bind approval detail

Required sections:

- quote summary
- risk summary
- compliance guard result
- customer/account ownership
- documents
- premium/coverage summary
- audit timeline
- approve/reject controls

Hard rules:

- approve button disabled if compliance guard fails
- reject requires reason
- any policy issuance must display actor, timestamp, and request key

### 4. Claims Workspace

Purpose: claims operations and manager approvals.

Primary navigation:

- FNOL queue
- My claims
- Missing information
- Coverage review
- Manager approval
- Denial review
- Payments/reserves
- Closed claims

Core screens:

#### Claims queue

Columns:

- claim ID
- policy ID
- customer
- severity
- queue
- loss type
- loss date
- status
- SLA age
- assigned adjuster

#### Claim detail

Tabs:

- overview
- coverage
- evidence
- notes
- reserves
- communications
- timeline
- audit

#### Evidence tab

Must show:

- type
- source
- URI/file reference
- checksum
- visibility
- uploaded by
- uploaded at
- immutable metadata indicator

#### Reserve tab

Must show:

- recommended reserves
- approved reserves
- approver
- reason
- event history
- approval controls for Claims Manager only

#### Denial review

Must show:

- denial reason
- reason codes
- draft notice
- legal/compliance review status
- manager approval requirement
- delivery disabled until template approval

### 5. Policy Administration Console

Purpose: lifecycle beyond initial bind.

Primary navigation:

- Policies
- Endorsements
- Cancellations
- Reinstatements
- Renewals
- Forms/templates
- Audit

Required future screens:

- endorsement workflow
- cancellation workflow
- renewal generation
- policy document packet
- template version manager
- policy lifecycle timeline

### 6. Treasury / Float Console

Purpose: premium allocation, liquidity, reserves, and governance.

Primary navigation:

- Overview
- Premium inflows
- Reserve snapshots
- Liquidity ladder
- Counterparties
- Investment policy statement
- Approvals
- Audit

Hard rules:

- no AI-only treasury action
- all allocations require policy/governance checks
- counterparty limits visible on every proposed action
- liquidity/reserve thresholds shown before approval

### 7. Compliance Console

Purpose: filings, notices, customer communications, and audit exports.

Primary navigation:

- Notice drafts
- Adverse action
- Claim denial drafts
- Template versions
- Filing register
- Complaints
- Audit exports

Core requirements:

- show template version
- show jurisdiction
- show approval status
- show delivery status
- show actor/timestamp for every action

### 8. Security/Admin Console

Purpose: tenant, user, role, IdP, and system operations.

Primary navigation:

- Tenants
- Users
- Roles
- Identity provider
- Secrets status
- Services
- Event outbox
- Audit log

Required controls:

- role assignment audit
- tenant isolation tests/status
- JWT/JWKS config display without secrets
- dev-token disabled indicator for production
- service health and migration status

### 9. Blockchain / Audit Console

Purpose: cryptographic proof and audit event review.

Primary navigation:

- Commitments
- Registry state
- Signer approvals
- Chain health
- Event hashes
- Reconciliation

Hard rules:

- never display or commit PII to-chain
- show off-chain source record reference
- show hash, signer, chain, block/tx if applicable
- support reconciliation report between DB events and chain commitments

## Global navigation model

Recommended app shell:

- left sidebar for role-based nav
- top bar with tenant, user, role, environment, request ID
- global search for customer, quote, policy, claim
- notification center for approvals/SLA breaches
- environment banner for local/staging/production

## Shared UI components

Required components:

- `AuditTimeline`
- `StatusBadge`
- `RiskScoreCard`
- `ReasonCodeList`
- `ApprovalPanel`
- `DocumentDraftViewer`
- `EventOutboxStatus`
- `OwnershipBanner`
- `PIIRevealControl`
- `QuotePremiumBreakdown`
- `CoverageSummaryTable`
- `ClaimEvidenceTable`
- `ReserveApprovalPanel`
- `ComplianceGuardPanel`
- `BlockchainCommitmentBadge`

## Design system requirements

- Accessible keyboard navigation.
- WCAG AA color contrast.
- Strong status color semantics but never color-only status communication.
- All destructive or regulated actions require explicit confirmation.
- Role-disabled actions must explain required role.
- PII fields should be masked by default and require reveal action.
- Every page should have request ID available for support/debugging.

## API integration map

| UI area | Backend target |
|---|---|
| Quote intake/result | quote-service |
| Quote explainability | quote-service `/quotes/{id}/explain` |
| Risk review | risk-appetite-service `/assess`, policy version endpoints |
| Bind approval | policy-service bind endpoints |
| Policy view | policy-service policy endpoints |
| Claim FNOL/detail | claims-service claim endpoints |
| Evidence metadata | claims-service evidence endpoint |
| Reserve approval | claims-service reserve endpoints |
| Denial review | claims-service denial-review endpoint |
| Documents | packages/documents initially, future document-service |
| Event outbox | events package + future event service |
| Auth/session | shared security + external IdP |
| Blockchain audit | future blockchain-gateway |
| Treasury | future treasury-service |

## Frontend implementation plan

### P0 UI foundation

1. Create `apps/web` React/Next.js app or Vite React app.
2. Add app shell, route guards, role-aware navigation.
3. Add auth token provider abstraction.
4. Add API client package.
5. Add design-system components.
6. Add customer/agent/underwriter/claims role fixtures.
7. Add Storybook or component test harness.

### P1 operational workflows

1. Customer quote intake/result.
2. Agent quote workspace.
3. Underwriter bind approval queue.
4. Claims FNOL and claim detail.
5. Evidence table and reserve approval panel.
6. Compliance notice draft viewer.

### P2 production controls

1. Security/admin console.
2. Compliance console.
3. Treasury console.
4. Blockchain/audit console.
5. Full audit timeline integration.
6. OpenTelemetry trace/request correlation in UI.

## Acceptance criteria for first UI PR

- App shell renders role-aware navigation.
- Routes exist for customer portal, agent desktop, underwriter console, and claims workspace.
- API client has typed methods for quote, risk, policy, and claims endpoints.
- Mock data fixtures cover quote, bind, claim, reserve, and denial-review flows.
- UI shows request/environment banner.
- Regulated actions are disabled unless actor role allows them.
- PII masking component exists and is tested.
