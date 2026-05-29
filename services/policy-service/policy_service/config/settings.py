"""Policy service configuration."""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings


class PolicyServiceSettings(BaseSettings):
    """Settings for the Policy Service."""

    database_url: str = "sqlite:///./policy-service.db"
    auto_create_schema: bool = True
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    allow_credentials: bool = False
    log_level: str = "INFO"
    bind_request_expiry_hours: int = 24
    approval_request_expiry_hours: int = 24
    blockchain_gateway_url: str = "http://localhost:8545"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    model_config = {"env_prefix": "POLICY_SERVICE_"}


settings = PolicyServiceSettings()
