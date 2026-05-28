from __future__ import annotations

from pydantic_settings import BaseSettings


class AuthServiceSettings(BaseSettings):
    auth_service_secret_key: str = "CHANGE_ME_REPLACE_IN_PROD"
    token_expiry_minutes: int = 60
    issuer: str = "auto-insurance-auth-service"

    model_config = {"env_prefix": "AUTH_SERVICE_"}


settings = AuthServiceSettings()
