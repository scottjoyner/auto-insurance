# Identity Provider Readiness Guide

Owner: Platform Engineering and Security  
Audience: engineering, security, operations  
Last reviewed: 2026-05-29  
Status: active P0.3 production-auth guide

## Purpose

This guide defines the production identity-provider contract for the insurance operating system. Local development can use development bearer tokens, but production deployments must use JWT/JWKS authentication with fail-closed settings validation.

## Current implementation

The shared security package supports:

- development bearer tokens for local work;
- JWT mode through `INSURANCE_AUTH_MODE=jwt`;
- HS256 validation for local/integration test deployments;
- RS256 and asymmetric JWT validation through JWKS;
- issuer and audience validation;
- role extraction into `ActorContext`;
- tenant/customer claim extraction into `ActorContext`;
- fail-closed settings validation for JWT mode.

## Local development mode

Development tokens remain available when:

```bash
INSURANCE_AUTH_MODE=dev
INSURANCE_ALLOW_DEV_TOKENS=true
```

Token examples:

```text
Bearer dev:<actor_id>:<ROLE>[,<ROLE>...]:<tenant_id>:<customer_id>
Bearer system:<actor_id>
```

Production environments must not use development tokens.

## Production JWT mode

Required baseline settings:

```bash
INSURANCE_AUTH_MODE=jwt
INSURANCE_ALLOW_DEV_TOKENS=false
INSURANCE_JWT_ISSUER=https://idp.example.com/
INSURANCE_JWT_AUDIENCE=auto-insurance-api
INSURANCE_JWT_ALGORITHM=RS256
INSURANCE_JWT_JWKS_URL=https://idp.example.com/.well-known/jwks.json
```

For HS256-only non-production integration tests:

```bash
INSURANCE_AUTH_MODE=jwt
INSURANCE_ALLOW_DEV_TOKENS=false
INSURANCE_JWT_ISSUER=https://idp.example.test/
INSURANCE_JWT_AUDIENCE=auto-insurance-api
INSURANCE_JWT_ALGORITHM=HS256
INSURANCE_JWT_HS256_SECRET=<test-secret>
```

## Required JWT claims

Minimum required claims:

```json
{
  "sub": "external-user-or-service-id",
  "roles": ["AGENT"],
  "tenant_id": "tenant-1",
  "customer_id": "customer-1",
  "iss": "https://idp.example.com/",
  "aud": "auto-insurance-api"
}
```

`tenant_id` and `customer_id` are required for customer-scoped workflows. Privileged service/admin workflows may omit `customer_id` only when the endpoint permits privileged access.

## Canonical roles

The shared role enum currently supports:

- `CUSTOMER`
- `AGENT`
- `UNDERWRITER_L1`
- `UNDERWRITER_L2`
- `CLAIMS_MANAGER`
- `TREASURY_APPROVER`
- `SMART_CONTRACT_SIGNER`
- `ADMIN`
- `SYSTEM`

External IdP groups should map into these canonical roles before tokens reach the application, or a role-claim mapping adapter should be added before production launch.

## Fail-closed behavior

When `INSURANCE_AUTH_MODE=jwt`, `validate_security_settings()` requires:

- issuer;
- audience;
- algorithm;
- HS256 secret when `INSURANCE_JWT_ALGORITHM=HS256`;
- JWKS URL for asymmetric algorithms such as `RS256`.

If settings are missing or invalid, authenticated requests fail closed.

## Test coverage

Security tests currently cover:

- missing token rejected;
- wrong role rejected;
- development token accepted in dev mode;
- dev token rejected when JWT mode disables dev tokens;
- HS256 valid token accepted;
- bad HS256 signature rejected;
- wrong issuer rejected;
- wrong audience rejected;
- missing roles rejected;
- RS256/JWKS valid token accepted;
- unknown JWKS key rejected;
- JWT settings validator failures for missing issuer, audience, secret, or JWKS URL.

## Rollout plan

### Phase 1: staging JWT validation

1. Configure staging IdP application/API audience.
2. Configure RS256 signing keys and expose JWKS.
3. Set service environment variables for JWT mode.
4. Disable dev tokens.
5. Create test users for each canonical role.
6. Validate quote, policy, claims, and customer-service endpoints with real IdP tokens.

### Phase 2: role and tenant/customer mapping

1. Map IdP groups to canonical roles.
2. Ensure `tenant_id` and `customer_id` claims are present for customer-scoped users.
3. Use customer-service identity links to resolve external subjects to internal customers where needed.
4. Add integration tests with realistic IdP token fixtures.

### Phase 3: production enforcement

1. Require `INSURANCE_AUTH_MODE=jwt` for all public services.
2. Require `INSURANCE_ALLOW_DEV_TOKENS=false`.
3. Add deployment admission checks for JWT settings.
4. Alert on authentication failures and JWKS fetch failures.
5. Rotate signing keys through the IdP and validate JWKS cache behavior.

## Remaining implementation gaps

- Service startup currently validates JWT settings in the FastAPI auth path. A deployment-level or app-startup validation hook should be added so misconfigured JWT mode fails before serving traffic.
- Role-claim mapping from external IdP group names to canonical roles is not yet implemented.
- Identity-link resolution exists in customer-service, but quote/policy/claims still use actor claims directly and do not yet resolve external `sub` to customer-service records.
- JWKS cache/refresh behavior relies on PyJWT defaults and should be reviewed for production key-rotation requirements.

## Acceptance checklist

- [ ] All public services run with `INSURANCE_AUTH_MODE=jwt` in staging.
- [ ] `INSURANCE_ALLOW_DEV_TOKENS=false` in staging and production.
- [ ] RS256 tokens validate against JWKS.
- [ ] wrong issuer and audience fail.
- [ ] unknown `kid` fails.
- [ ] missing role fails.
- [ ] customer-scoped endpoint rejects missing tenant/customer context.
- [ ] service logs redact tokens and do not emit PII claims.
- [ ] deployment runbook includes IdP outage and JWKS rotation procedures.
