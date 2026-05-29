## Summary

Describe the change and why it is needed.

## Change type

- [ ] Feature
- [ ] Bug fix
- [ ] Security hardening
- [ ] Compliance / documentation
- [ ] Refactor
- [ ] Test-only

## Required checks

- [ ] Tests added or updated for changed behavior.
- [ ] Phase 1 CI passes.
- [ ] Postgres Integration CI passes when database behavior changes.
- [ ] Documentation updated when workflow, role, compliance, or deployment behavior changes.
- [ ] Required docs still include `Owner`, `Audience`, `Last reviewed`, and `Status`.

## Security checklist

- [ ] Authentication/authorization impact reviewed.
- [ ] Tenant/customer ownership impact reviewed.
- [ ] No PII is logged or emitted to events without redaction.
- [ ] Secrets are not hardcoded.
- [ ] Dev-token behavior is not enabled for production paths.

## Compliance checklist

- [ ] Human approval gates remain enforced for bind, decline, claims, treasury, and smart-contract actions.
- [ ] Adverse-action or denial workflows generate draft notices only, unless approved template delivery is explicitly implemented.
- [ ] Claims denial remains human-approved only.
- [ ] Blockchain changes do not introduce public-chain deployment or fund custody without security review.

## Operational checklist

- [ ] Event outbox behavior reviewed if new lifecycle events are added.
- [ ] Migration or schema changes include migration files.
- [ ] New service endpoints include health, ownership, and error handling behavior.
- [ ] Logs include correlation IDs and avoid sensitive data.

## Reviewer notes

List any known limitations, follow-up PRs, or areas needing special reviewer attention.
