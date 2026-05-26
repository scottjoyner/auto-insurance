# AI Agent Architecture

## Purpose

The AI agent is an orchestrator and assistant. It helps customers, agents, underwriters, claims staff, treasury analysts, and compliance reviewers move through workflows. It should not operate as an unrestricted autonomous insurer.

## Agent Roles

```text
SalesIntakeAgent
UnderwritingAssistantAgent
RiskAppetiteAgent
PolicyServiceAgent
ClaimsIntakeAgent
ClaimsTriageAgent
TreasuryAnalystAgent
ComplianceReviewAgent
CustomerRetentionAgent
ExecutiveOpsAgent
```

## Authority Model

### Allowed by default

- collect customer intake
- explain products using approved knowledge
- prepare draft quote requests
- call quote tools
- call risk appetite tools
- summarize missing information
- create service cases
- route to human review
- summarize claim FNOL
- draft customer communications

### Restricted by default

- binding policies
- declining risks
- making final adverse decisions
- modifying rating logic
- approving claim payouts
- denying claims
- executing treasury actions
- changing smart contract parameters
- changing governance policy files

## Tool Flow

```text
message received
  -> session loaded
  -> intent classified
  -> applicable product/jurisdiction context retrieved
  -> tool permissions checked
  -> tool executed
  -> compliance guardrail applied
  -> human review triggered if required
  -> response generated
  -> audit log persisted
```

## Required Logs

Every AI interaction should log:

- session ID
- actor ID
- customer or case reference
- model ID
- model version
- prompt/template version
- retrieved documents
- tool calls
- tool inputs
- tool outputs
- final response
- human review flags
- reason codes

## Prompt Injection Controls

The agent must not accept user instructions that override:

- tool permissions
- product rules
- rating logic
- risk appetite rules
- human review thresholds
- treasury policy
- claim approval thresholds
- smart contract signer controls

## Human Handoff

Human handoff is required when:

- quote decline is possible
- customer disputes rating or eligibility
- underwriting information is inconsistent
- coverage explanation requires licensed review
- claim denial is possible
- payout exceeds threshold
- fraud indicator is present
- treasury proposal exceeds approval threshold
- compliance exception is raised

## First Implementation

The first implementation should expose a narrow agent shell:

```http
POST /agent/sessions
POST /agent/sessions/{session_id}/messages
POST /agent/sessions/{session_id}/handoff
GET /agent/sessions/{session_id}/audit
```

The only initial tools should be:

```text
create_lead
create_quote_request
generate_quote
evaluate_risk_appetite
create_human_review_case
get_product_knowledge
```
