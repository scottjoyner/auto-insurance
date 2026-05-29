# Employee Operating Manual

Owner: Operations Lead  
Audience: agents, underwriters, claims staff, treasury approvers, smart-contract operators, support staff  
Last reviewed: 2026-05-29  
Status: draft internal operating guide

## Purpose

This guide explains how employees should use the insurance operating system safely. It describes who can perform each workflow, what must be reviewed by a human, and what must be escalated.

## Core rule

The system may assist employees, but it must not replace licensed, authorized human review for bind, decline, claim decision, treasury, regulatory, or smart-contract administrative actions.

## Roles

### Customer

Uses customer-facing workflows only. Customers may submit intake, view eligible quotes/policies, and upload claim information.

### Agent

May collect intake, prepare quote requests, explain quote results, and prepare bind requests. Agents may not approve declines, bind policies without required approval, deny claims, or execute treasury/blockchain actions.

### Underwriter L1

May review quote referrals, approve ordinary bind requests, request more information, and refer complex risks to Underwriter L2.

### Underwriter L2

May approve higher-risk bind requests, approve risk appetite policy changes, and handle exception referrals.

### Claims Manager

May review FNOL, coverage check results, claim evidence, reserves, and claim decision recommendations. AI can summarize claims but cannot deny claims.

### Treasury Approver

May review premium allocation, reserves, float movement, and treasury actions. AI cannot execute treasury actions.

### Smart Contract Signer

May approve contract deployments or administrative blockchain transactions only after security review and change approval.

### Admin/System

Used for service-to-service and administrative workflows. Must be tightly controlled and audited.

## Daily workflow overview

1. Review new customer intake.
2. Validate required customer and vehicle information.
3. Generate or retrieve quote.
4. Review quote explainability and reason codes.
5. Run risk appetite assessment.
6. If bind eligible, prepare bind request.
7. Human approver reviews bind request.
8. If approved, policy service issues active policy record.
9. If rejected/declined, generate adverse-action draft and route to compliance review.
10. Monitor event outbox and operational dashboards.

## Quote workflow

### Employee steps

1. Confirm customer identity and tenant/customer context.
2. Enter applicant data only from verified customer-provided or approved third-party data sources.
3. Generate quote through quote service.
4. Review premium, coverages, discounts, surcharges, reason codes, referral flag, and bind eligibility.
5. If the quote is not bind eligible, do not promise coverage.
6. If customer asks why premium changed, use quote explanation output and do not invent factors.

### Required escalation

Escalate to underwriting if:

- Referral flag is not `none`.
- Bind eligibility is false but customer wants review.
- Driver, vehicle, claims, geography, or coverage facts are disputed.
- The system returns inconsistent or missing reason codes.

## Risk appetite workflow

1. Run risk assessment against the quote snapshot.
2. Confirm active policy version used for the assessment.
3. Review decision, risk score, concentration, capital, and reinsurance impact.
4. If decision is decline/reject/deny, stop bind workflow and route to compliance review.
5. If decision is refer or accept-with-limits, route to underwriter review.

## Bind workflow

1. Confirm quote is current and not expired.
2. Confirm quote is bind eligible.
3. Confirm risk decision allows bind or requires review.
4. Create bind request with idempotency key.
5. Human approver reviews the bind packet.
6. Approver approves or rejects.
7. System creates active policy only after approval.

## Claim workflow summary

Claims work must follow `08_claims_crm_operating_guide.md`.

AI can summarize claim information and identify missing documents. AI cannot deny claims, approve payments, or determine fraud without human review.

## Blockchain workflow summary

Blockchain commitments are audit records only unless a deployment is explicitly approved. No public-chain deployment is allowed until the contract audit checklist in `09_blockchain_security_review.md` is complete.

## Customer communication rules

Employees must not send draft system-generated notices directly to customers. Draft adverse-action notices and policy packets must be reviewed by compliance/counsel-approved templates first.

## Incident escalation

Escalate immediately if any of the following occurs:

- Unauthorized customer data access.
- Incorrect policy bound.
- Quote generated with wrong jurisdiction/product.
- Event outbox fails repeatedly.
- Smart-contract key or signer key exposure.
- AI output recommends prohibited action.
- Customer communication sent with unapproved template.

## Audit expectations

Every major action must be traceable to:

- actor ID
- tenant/customer context
- quote/policy/claim ID
- timestamp
- decision and reason codes
- human approval where required

## Employee training checklist

- Understand role permissions.
- Understand AI restrictions.
- Understand quote/risk/bind sequence.
- Understand claim CRM workflow.
- Understand adverse-action escalation.
- Understand PII handling and redaction.
- Understand incident escalation path.
