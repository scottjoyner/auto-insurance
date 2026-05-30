"""Claims service settings."""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings


class ClaimsSettings(BaseSettings):
    database_url: str = "sqlite:///./claims_service.db"
    auto_create_schema: bool = True
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    allow_credentials: bool = False
    log_level: str = "INFO"

    # Customer service validation
    validate_customer: bool = False
    customer_service_url: str = "http://customer-service:8005"
    customer_validation_timeout_seconds: float = 3.0

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    model_config = {"env_prefix": "CLAIMS_SERVICE_"}


settings = ClaimsSettings()
