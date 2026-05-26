# Vision

## North Star

Build a blockchain-first insurance operating system where AI agents can safely orchestrate customer acquisition, quoting, underwriting support, policy administration, claims intake, customer service, and treasury analysis under strict governance, audit, and human authority boundaries.

## What This System Is

This system is intended to become a full operating layer for an insurance organization. It combines:

- deterministic rating and quote generation
- portfolio-aware risk appetite evaluation
- AI-assisted customer and internal workflows
- policy lifecycle administration
- claims lifecycle administration
- premium allocation and reserve management
- float and treasury governance
- blockchain-based commitments and attestations
- compliance and audit export tooling

## What This System Is Not

The system is not:

- an unregulated autonomous insurer
- a chatbot-only quote flow
- a public blockchain dump of insurance data
- a DeFi yield system pretending to be insurance treasury
- a production carrier without legal, actuarial, accounting, treasury, and regulatory review

## Design Philosophy

The platform should use AI and blockchain where they are strongest:

- AI for intake, orchestration, retrieval, explanation, triage, summaries, and workflow support.
- Blockchain for commitments, attestations, settlement references, governance records, and audit anchors.
- Deterministic services for rating, risk appetite, policy state, claims state, and treasury policy enforcement.
- Humans for regulated authority, exceptions, high-risk decisions, and governance approvals.

## First Product Goal

The first implementation should use a sample product or limited MVP product so the platform can prove the operating model before adding production regulatory complexity.

## First Technical Goal

Build the quote-to-policy loop:

```text
lead
  -> intake
  -> quote
  -> risk appetite
  -> accept
  -> bind
  -> policy document hash
  -> blockchain commitment
  -> premium allocation
  -> audit packet
```

## Long-Term Goal

The long-term architecture should support multiple product lines, multiple jurisdictions, producer channels, customer self-service, claims operations, reinsurance, float management, actuarial analytics, and regulator/auditor transparency.