# Markdown Cleanup Register

Owner: Platform Engineering  
Audience: engineering, operations, compliance  
Last reviewed: 2026-05-29  
Status: active cleanup register

## Purpose

This register tracks markdown files that may contain outdated implementation status, superseded plans, or historical architecture assumptions. It prevents old planning text from being mistaken for the current operating model.

## Status labels

- `current` — safe to use as current guidance.
- `superseded` — replaced by newer documentation; keep for history only.
- `archived` — historical decision record; not operational guidance.
- `delete-candidate` — safe to remove after review.
- `needs-review` — content may be stale and needs owner review.

## Canonical current docs

| File | Status | Notes |
|---|---|---|
| `docs/00_documentation_index.md` | current | Canonical documentation entry point. |
| `docs/04_phase1_completion_report.md` | current | Completed Phase 1 foundation report. |
| `docs/05_production_gap_closure.md` | current | Production gap closure status. |
| `docs/06_production_hardening_runbook.md` | current | Deployment gates and hardening commands. |
| `docs/07_employee_operating_manual.md` | current | Internal employee operating guide. |
| `docs/08_claims_crm_operating_guide.md` | current | Claims CRM target workflow and acceptance criteria. |
| `docs/09_blockchain_security_review.md` | current | Blockchain security review and audit checklist. |
| `docs/10_markdown_cleanup_register.md` | current | This cleanup register. |

## Known stale or likely stale docs

| File | Status | Replacement / action |
|---|---|---|
| `README.md` | needs-review | Contains older P0/P1 status language. Replace with short current overview and link to `docs/00_documentation_index.md`. |
| `docs/00_current_state_assessment.md` | needs-review | May describe earlier gaps that have since been implemented. Review against current services and CI. |
| `docs/03_execution_plan.md` | needs-review | May contain old P0/P1/P2 sequencing. Supersede implemented portions with current completion reports. |
| Older architecture docs under `docs/` | needs-review | Keep as design history if accurate; mark superseded when contradicted by current implementation. |
| Any blockchain MVP planning text | needs-review | Must reference `docs/09_blockchain_security_review.md` and cannot imply deployment approval. |
| Any claims MVP planning text | needs-review | Must reference `docs/08_claims_crm_operating_guide.md` and cannot imply claims CRM is complete. |

## Cleanup process

1. Review each markdown file.
2. Add one of the status labels above at the top of the file.
3. If superseded, add a `Superseded by:` pointer.
4. If historical, add `Historical note:` explaining why it remains.
5. If delete-candidate, confirm no current docs link to it.
6. Prefer updating links to `docs/00_documentation_index.md` rather than older phase plans.

## Required header for current operational docs

Each current operational doc should include:

```text
Owner: <role/team>
Audience: <users>
Last reviewed: YYYY-MM-DD
Status: current|draft|historical|superseded
```

## Open cleanup tasks

- [ ] Replace root README with current overview.
- [ ] Review `docs/00_current_state_assessment.md`.
- [ ] Review `docs/03_execution_plan.md`.
- [ ] Search all markdown for `not complete`, `partial`, `P0`, `P1`, `TODO`, and `MVP` and update stale statements.
- [ ] Add markdown/docs status validation script.
- [ ] Add docs owner review as a PR checklist item.
