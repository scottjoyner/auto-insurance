# Customer Service

Owner: Platform Engineering  
Audience: engineering, operations, product  
Last reviewed: 2026-05-29  
Status: active P0.1 service scaffold

## Purpose

Customer Service is the source-of-truth service for tenants, accounts, and customers. Quote, policy, and claims services already carry `tenant_id` and `customer_id`; this service provides the authoritative customer/account records those IDs should resolve to.

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
  -d '{"tenant_id":"tenant-1","name":"Jane Doe Household","account_type":"personal"}'
```

Create customer:

```bash
curl -X POST http://localhost:8005/customers \
  -H 'Authorization: Bearer dev:agent-1:AGENT:tenant-1:agent' \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"tenant-1","account_id":"<account_id>","first_name":"Jane","last_name":"Doe"}'
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

## Implemented endpoints

- `POST /tenants`
- `POST /accounts`
- `POST /customers`
- `GET /customers/{customer_id}`
- `GET /customers`
- `GET /customers/{customer_id}/summary`
- `GET /health`

## Current limitations

- Contact/address tables exist, but create/update endpoints are not implemented yet.
- Identity-provider link table exists, but lookup endpoint is not implemented yet.
- Quote/policy/claims services do not yet call this service for live ownership validation.
- Repository class was deferred because the connector blocked repeated repository-file payloads; current API uses SQLAlchemy session access directly.

## Next quick deliverables

1. Add contact/address create endpoints.
2. Add identity-link create/lookup endpoints.
3. Add customer-service client package.
4. Integrate quote/policy/claims ownership validation with the client.
5. Add customer-service Postgres repository/API tests.
