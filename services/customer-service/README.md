# Customer Service

Owner: Platform Engineering  
Audience: engineering, operations, product  
Last reviewed: 2026-05-29  
Status: active P0.1 service scaffold

## Purpose

Customer Service is the source-of-truth service for tenants, accounts, customers, contacts, addresses, and external identity links. Quote, policy, and claims services already carry `tenant_id` and `customer_id`; this service provides the authoritative customer/account records those IDs should resolve to.

## Local run

Customer Service is available through the compose override:

```bash
docker compose -f docker-compose.yml -f docker-compose.customer.yml build customer-service
docker compose -f docker-compose.yml -f docker-compose.customer.yml up customer-service
```

Local port:

```text
8005
```

## Development auth examples

Admin token:

```text
Bearer dev:admin-1:ADMIN:tenant-1:admin
```

Agent token:

```text
Bearer dev:agent-1:AGENT:tenant-1:agent
```

Customer token:

```text
Bearer dev:customer-actor:CUSTOMER:tenant-1:<customer_id>
```

## Example workflow

Create tenant:

```bash
curl -X POST http://localhost:8005/tenants \
  -H 'Authorization: Bearer dev:admin-1:ADMIN:tenant-1:admin' \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"tenant-1","name":"Tenant One"}'
```

Create account:

```bash
curl -X POST http://localhost:8005/accounts \
  -H 'Authorization: Bearer dev:admin-1:ADMIN:tenant-1:admin' \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"tenant-1","name":"Household","account_type":"personal"}'
```

Create customer:

```bash
curl -X POST http://localhost:8005/customers \
  -H 'Authorization: Bearer dev:agent-1:AGENT:tenant-1:agent' \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"tenant-1","account_id":"<account_id>","first_name":"Jane","last_name":"Doe"}'
```

Add contact:

```bash
curl -X POST http://localhost:8005/customers/<customer_id>/contacts \
  -H 'Authorization: Bearer dev:agent-1:AGENT:tenant-1:agent' \
  -H 'Content-Type: application/json' \
  -d '{"contact_type":"reference","value":"contact-value","is_primary":true}'
```

Add address:

```bash
curl -X POST http://localhost:8005/customers/<customer_id>/addresses \
  -H 'Authorization: Bearer dev:agent-1:AGENT:tenant-1:agent' \
  -H 'Content-Type: application/json' \
  -d '{"address_type":"mailing","line1":"line one","city":"city","state":"ST","postal_code":"00000","country":"US"}'
```

Add external identity link:

```bash
curl -X POST http://localhost:8005/customers/<customer_id>/identity-links \
  -H 'Authorization: Bearer dev:admin-1:ADMIN:tenant-1:admin' \
  -H 'Content-Type: application/json' \
  -d '{"provider":"test-provider","subject":"subject-123"}'
```

Search customers:

```bash
curl 'http://localhost:8005/customers?q=Jane' \
  -H 'Authorization: Bearer dev:agent-1:AGENT:tenant-1:agent'
```

Get customer detail:

```bash
curl http://localhost:8005/customers/<customer_id> \
  -H 'Authorization: Bearer dev:customer-actor:CUSTOMER:tenant-1:<customer_id>'
```

Get customer summary:

```bash
curl http://localhost:8005/customers/<customer_id>/summary \
  -H 'Authorization: Bearer dev:agent-1:AGENT:tenant-1:agent'
```

Resolve external identity link:

```bash
curl http://localhost:8005/identity-links/test-provider/subject-123 \
  -H 'Authorization: Bearer dev:admin-1:ADMIN:tenant-1:admin'
```

## Implemented endpoints

- `POST /tenants`
- `POST /accounts`
- `POST /customers`
- `POST /customers/{customer_id}/contacts`
- `POST /customers/{customer_id}/addresses`
- `POST /customers/{customer_id}/identity-links`
- `GET /identity-links/{provider}/{subject}`
- `GET /customers/{customer_id}`
- `GET /customers`
- `GET /customers/{customer_id}/summary`
- `GET /health`

## Ownership rules

- Customer detail is denied when actor tenant/customer does not match the record.
- Customer search is tenant-scoped for non-privileged roles.
- Customer actors can only see their own customer record.
- Contact and address creation requires access to the target customer.
- External identity-link management is admin/system only.

## Events emitted

- `TenantCreated`
- `AccountCreated`
- `CustomerCreated`
- `CustomerContactCreated`
- `CustomerAddressCreated`
- `CustomerIdentityLinked`

## Current limitations

- Contact/address update/delete endpoints are not implemented yet.
- Quote/policy/claims services do not yet call this service for live ownership validation.
- Repository class was deferred because the connector blocked repeated repository-file payloads; current API uses SQLAlchemy session access directly.

## Next quick deliverables

1. Add a customer-service client helper once connector allows the package/file payload.
2. Integrate quote/policy/claims ownership validation with the helper.
3. Add contact/address update endpoints.
4. Add identity-link delete/rotation workflow.
5. Add customer-service to root compose when connector allows root YAML replacement.
