"""Policy service configuration."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class PolicyServiceSettings(BaseSettings):
    """Settings for the Policy Service."""

    database_url: str = "sqlite+aiosqlite:///./policy-service.db"
    log_level: str = "INFO"
    bind_request_expiry_hours: int = 24
    approval_request_expiry_hours: int = 24
    blockchain_gateway_url: str = "http://localhost:8545"

    model_config = {"env_prefix": "POLICY_SERVICE_"}


settings = PolicyServiceSettings()
