# Documentation Index

## Purpose

This file is the canonical entry point for repository documentation. Older markdown files may describe earlier architecture assumptions and should be treated as historical unless listed below as current.

## Current operator-facing documents

- `04_phase1_completion_report.md` — completed foundation work.
- `05_production_gap_closure.md` — production gap closure status.
- `06_production_hardening_runbook.md` — deployment gates and hardening commands.
- `07_employee_operating_manual.md` — employee workflow manual.
- `08_claims_crm_operating_guide.md` — claims CRM workflow guide.
- `09_blockchain_security_review.md` — blockchain contract security review checklist.
- `10_markdown_cleanup_register.md` — stale documentation register.

## Current engineering documents

- Service READMEs under `services/*` when present.
- Package READMEs under `packages/*` when present.
- SQL migrations under `services/*/migrations`.
- Alembic baselines under `services/*/alembic`.
- CI workflows under `.github/workflows`.

## Stale documentation policy

1. A document is stale when it says a feature is missing but the implementation and tests now exist.
2. Do not delete stale docs immediately if they contain decision history.
3. Mark stale docs in `10_markdown_cleanup_register.md` with one of: current, superseded, archived, delete-candidate.
4. New work should link to this index instead of linking directly to older planning docs.
5. Customer-facing or employee-facing workflow documents must include owner, audience, and last-reviewed metadata.

## Documentation owners

- Engineering docs: platform engineering.
- Employee operating docs: operations lead.
- Claims CRM docs: claims operations lead.
- Blockchain security docs: smart-contract/security lead.
- Compliance/customer communication docs: compliance lead and counsel review.
