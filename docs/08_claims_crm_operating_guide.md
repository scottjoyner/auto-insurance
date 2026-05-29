# Claims CRM Operating Guide

Owner: Claims Operations Lead  
Audience: claims intake staff, adjusters, claims managers, support staff, engineering  
Last reviewed: 2026-05-29  
Status: draft internal operating guide

## Purpose

This guide defines the operating process for claim management CRM workflows. It covers FNOL intake, evidence collection, coverage review, claim triage, reserves, payments, denial controls, escalation, and audit expectations.

## Current implementation status

The repository currently has quote, risk, and policy foundations. Claims CRM is not yet fully implemented. This document defines the target workflow and acceptance criteria for implementation.

## Claims CRM modules

### 1. FNOL intake

First Notice of Loss captures the initial claim report.

Required fields:

- policy ID
- customer ID
- claimant name
- loss date/time
- loss location
- loss type
- description of facts
- involved parties
- vehicle/property involved
- police report indicator
- injuries indicator
- photos/documents uploaded
- preferred contact method

### 2. Coverage check

System should retrieve policy, effective/expiration dates, coverages, endorsements, exclusions, and payment/active state.

Coverage check output:

- active policy yes/no
- coverage in force on loss date yes/no
- matching coverage lines
- deductible estimate
- exclusions/referrals
- missing information

### 3. Claim triage

Claim triage assigns severity and routing.

Severity examples:

- low: minor property damage, no injuries, clear coverage
- medium: disputed facts, moderate damage, coverage questions
- high: bodily injury, litigation threat, fraud indicators, severe loss
- catastrophic: fatality, mass loss, major reserve exposure

### 4. Evidence management

CRM must track evidence items:

- photos
- videos
- police reports
- repair estimates
- medical bills
- witness statements
- correspondence
- adjuster notes
- third-party data

Evidence must have source, uploader, timestamp, hash/checksum when possible, and visibility classification.

### 5. Reserve management

Claim reserves must be human-approved. AI may recommend reserve ranges but cannot set final reserves.

Reserve fields:

- initial reserve
- current reserve
- reserve reason
- approver
- reserve history
- payment history

### 6. Claim decision

Allowed claim decision statuses:

- open
- pending information
- coverage review
- accepted
- partially accepted
- denied pending manager review
- denied approved
- closed
- reopened

AI cannot deny claims. Any denial must be reviewed by Claims Manager and compliance where required.

## Claim workflow

1. Customer or employee creates FNOL.
2. System validates policy ID and customer ownership.
3. System performs coverage check.
4. Claim is assigned severity.
5. Claim is routed to queue.
6. Adjuster requests missing evidence.
7. Adjuster reviews facts and coverage.
8. AI may summarize facts and identify missing documents.
9. Claims Manager approves reserve changes, payments, or denial decisions.
10. Customer communication is generated from approved templates.
11. Claim is closed only after all required documentation is complete.

## CRM queues

Recommended queues:

- New FNOL
- Missing Information
- Coverage Review
- Adjuster Review
- Manager Approval
- Payment Pending
- Denial Review
- Litigation/Fraud Referral
- Closed Pending Audit

## Employee permissions

| Action | Intake Staff | Adjuster | Claims Manager | AI Agent |
|---|---:|---:|---:|---:|
| Create FNOL | Yes | Yes | Yes | Assist only |
| Upload evidence | Yes | Yes | Yes | No |
| Summarize evidence | No | Yes | Yes | Yes |
| Coverage check | View | View | View | Assist only |
| Set reserve | No | Recommend | Approve | No |
| Approve payment | No | Recommend | Approve | No |
| Deny claim | No | Recommend | Approve only | No |
| Close claim | No | Yes | Yes | No |

## CRM audit fields

Every claim action must record:

- claim ID
- policy ID
- tenant ID
- customer ID
- actor ID
- actor role
- action type
- before/after values where applicable
- reason codes
- timestamp
- source system

## Required engineering acceptance criteria

A claims service is not complete until it supports:

- durable Claim table
- FNOL creation endpoint
- claim ownership enforcement
- coverage check integration with policy service
- evidence metadata table
- claim notes table
- claim status history
- reserve history
- claim event outbox
- manager approval workflow
- denial/adverse-claim communication workflow
- CRM list filters by queue, status, severity, owner, and date
- tests for customer isolation
- tests for claim denial human approval

## Prohibited behavior

The system must not:

- allow AI-only claim denial
- allow AI-only payment approval
- expose claims across customers/tenants
- delete evidence without retention workflow
- overwrite claim history
- send unapproved denial language
- ignore coverage date mismatches

## Escalation triggers

Escalate to Claims Manager if:

- injury or fatality is reported
- customer threatens litigation
- facts conflict materially
- coverage is unclear
- fraud indicators appear
- reserve exceeds authority threshold
- claim denial is being considered

## Implementation backlog

### P0 claims CRM implementation

1. Add claims-service skeleton.
2. Add Claim, ClaimEvidence, ClaimNote, ClaimStatusHistory, ClaimReserveHistory ORM models.
3. Add FNOL endpoint.
4. Add claim list/detail endpoints with ownership enforcement.
5. Add coverage check adapter to policy service.
6. Add manager approval workflow.
7. Add claim event outbox.
8. Add tests.

### P1 claims CRM implementation

1. Evidence file storage integration.
2. Customer messaging templates.
3. Adjuster assignment rules.
4. SLA timers.
5. Fraud/litigation referral workflow.
6. Dashboards and reporting.

## Claims PR checklist

- [ ] Models include tenant/customer ownership fields.
- [ ] FNOL endpoint validates policy ownership.
- [ ] Claim list endpoint scopes results to actor tenant/customer.
- [ ] Claim detail endpoint rejects cross-customer access.
- [ ] Reserve changes require Claims Manager approval.
- [ ] Denial workflow requires Claims Manager approval and compliance-ready notice draft.
- [ ] Evidence metadata is immutable after upload except classification updates.
- [ ] Event outbox captures FNOL, status change, reserve change, evidence upload, and denial approval events.
- [ ] Tests cover customer isolation, manager approval, coverage date mismatch, and missing evidence routing.
