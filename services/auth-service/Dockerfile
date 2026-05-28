FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY . .

RUN python -m pip install --upgrade pip
RUN pip install .

EXPOSE 8005
CMD ["uvicorn", "auth_service.api.app:app", "--host", "0.0.0.0", "--port", "8005"]
