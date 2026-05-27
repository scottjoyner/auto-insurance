# Infrastructure — Local Development

## Purpose

Local development environment for the insurance operating system architecture prototype.

## Services

| Service | Port | Description |
|---|---|---|
| quote-service | 8001 | Quote generation with deterministic rating |
| risk-appetite-service | 8002 | Risk appetite evaluation |
| policy-service | 8003 | Policy lifecycle management |
| blockchain-gateway | 8004 | Blockchain commitment gateway (local Anvil) |
| anvil (EVM) | 8545 | Local EVM for contract deployment |
| claims-service | 8005 | Claims intake and workflow |
| treasury-service | 8006 | Premium allocation and treasury |
| ai-agent-orchestrator | 8007 | AI agent with tool permissions |
| crm-service | 8008 | Customer relationship management |
| compliance-service | 8009 | Compliance and audit |
| notification-service | 8010 | Communication channel (HTTP API) |
| analytics-service | 8011 | Analytics and reporting |

## Docker Compose

```yaml
version: "3.9"

services:
  anvil:
    image: ghcr.io/foundry-rs/foundry:latest
    command: anvil --chain-id 31337 --port 8545 --host 0.0.0.0
    ports:
      - "8545:8545"
    volumes:
      - anvil-data:/data

  quote-service:
    build:
      context: .
      dockerfile: services/quote-service/Dockerfile
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/quote_service
      - RATING_DSL_PATH=/app/data/rating-dsl
      - RISK_APPETITE_PATH=/app/governance/risk_appetite_policy.yml
    depends_on:
      - db

  risk-appetite-service:
    build:
      context: .
      dockerfile: services/risk-appetite-service/Dockerfile
    ports:
      - "8002:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/risk_service
      - RISK_APPETITE_PATH=/app/governance/risk_appetite_policy.yml
    depends_on:
      - db

  policy-service:
    build:
      context: .
      dockerfile: services/policy-service/Dockerfile
    ports:
      - "8003:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/policy_service
      - BLOCKCHAIN_GATEWAY_URL=http://blockchain-gateway:8000
    depends_on:
      - db
      - blockchain-gateway

  blockchain-gateway:
    build:
      context: .
      dockerfile: services/blockchain-gateway/Dockerfile
    ports:
      - "8004:8000"
    environment:
      - ANVIL_URL=http://anvil:8545
      - CONTRACT_DEPLOYED=false
    depends_on:
      - anvil

  claims-service:
    build:
      context: .
      dockerfile: services/claims-service/Dockerfile
    ports:
      - "8005:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/claims_service
    depends_on:
      - db

  treasury-service:
    build:
      context: .
      dockerfile: services/treasury-service/Dockerfile
    ports:
      - "8006:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/treasury_service
      - TREASURY_POLICY_PATH=/app/governance/treasury_policy.yml
    depends_on:
      - db

  ai-agent-orchestrator:
    build:
      context: .
      dockerfile: services/ai-agent-orchestrator/Dockerfile
    ports:
      - "8007:8000"
    environment:
      - QUOTE_SERVICE_URL=http://quote-service:8000
      - RISK_SERVICE_URL=http://risk-appetite-service:8000
      - POLICY_SERVICE_URL=http://policy-service:8000
      - CLAIMS_SERVICE_URL=http://claims-service:8000
      - AI_MODEL_PROVIDER=TBD
      - AI_MODEL_NAME=TBD
      - AI_MODEL_VERSION=TBD
    depends_on:
      - quote-service
      - risk-appetite-service
      - policy-service
      - claims-service

  crm-service:
    build:
      context: .
      dockerfile: services/crm-service/Dockerfile
    ports:
      - "8008:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/crm_service
    depends_on:
      - db

  compliance-service:
    build:
      context: .
      dockerfile: services/compliance-service/Dockerfile
    ports:
      - "8009:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/compliance_service
    depends_on:
      - db

  notification-service:
    build:
      context: .
      dockerfile: services/notification-service/Dockerfile
    ports:
      - "8010:8000"
    environment:
      - COMMUNICATION_MODE=web_chat
    depends_on:
      - crm-service

  analytics-service:
    build:
      context: .
      dockerfile: services/analytics-service/Dockerfile
    ports:
      - "8011:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/analytics_service
    depends_on:
      - db

  db:
    image: postgres:16
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=quote_service
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  anvil-data:
  postgres-data:
```

## Local Development Commands

```bash
# Start all services
docker compose up -d

# Deploy contracts to local Anvil
cd services/blockchain-gateway
npx hardhat run scripts/deploy.js --network anvil

# Run all service tests
docker compose run --rm quote-service pytest
docker compose run --rm risk-appetite-service pytest
docker compose run --rm policy-service pytest

# Run blockchain tests
cd services/blockchain-gateway
npx hardhat test

# Stop all services
docker compose down

# Stop and remove data
docker compose down -v
```
