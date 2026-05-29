FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/packages/security:/app/packages/observability:/app/packages/documents:/app/services/claims-service
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN python -m pip install --upgrade pip \
    && pip install "fastapi>=0.115" "uvicorn>=0.34" "pydantic>=2.10" "pydantic-settings>=2.7" "sqlalchemy>=2.0" "PyJWT>=2.10"

EXPOSE 8004
CMD ["uvicorn", "claims_service.api:app", "--host", "0.0.0.0", "--port", "8004"]
