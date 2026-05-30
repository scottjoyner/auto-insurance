# Customer Service Environment

Owner: Platform Engineering  
Audience: engineering, operations  
Last reviewed: 2026-05-29  
Status: active service configuration reference

## Variables

```bash
CUSTOMER_SERVICE_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
CUSTOMER_SERVICE_ALLOW_CREDENTIALS=false
CUSTOMER_SERVICE_DATABASE_URL=sqlite:////app/customer_service.db
CUSTOMER_SERVICE_AUTO_CREATE_SCHEMA=true
```

## Local service port

The intended local port is `8005`.

## Production notes

- Use Postgres instead of SQLite.
- Disable automatic schema creation after migrations are adopted.
- Require JWT/JWKS authentication through the shared security package.
- Do not log customer contact, address, or identity-provider subject values without redaction.
