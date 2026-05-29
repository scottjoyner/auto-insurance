FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/packages/security:/app/services/risk-appetite-service
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN python -m pip install --upgrade pip \
    && pip install "fastapi>=0.115" "uvicorn>=0.34" "pydantic>=2.10" "pydantic-settings>=2.7" "pyyaml>=6.0" "sqlalchemy>=2.0"

EXPOSE 8002
CMD ["uvicorn", "risk_appetite_service.api.app:app", "--host", "0.0.0.0", "--port", "8002"]
