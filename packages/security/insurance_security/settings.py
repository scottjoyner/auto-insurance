"""Shared security settings."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class SecuritySettings:
    auth_mode: str = "dev"
    jwt_issuer: str | None = None
    jwt_audience: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_hs256_secret: str | None = None
    jwt_jwks_url: str | None = None
    allow_dev_tokens: bool = True


def get_security_settings() -> SecuritySettings:
    return SecuritySettings(
        auth_mode=os.getenv("INSURANCE_AUTH_MODE", "dev").lower(),
        jwt_issuer=os.getenv("INSURANCE_JWT_ISSUER"),
        jwt_audience=os.getenv("INSURANCE_JWT_AUDIENCE"),
        jwt_algorithm=os.getenv("INSURANCE_JWT_ALGORITHM", "HS256"),
        jwt_hs256_secret=os.getenv("INSURANCE_JWT_HS256_SECRET"),
        jwt_jwks_url=os.getenv("INSURANCE_JWT_JWKS_URL"),
        allow_dev_tokens=os.getenv("INSURANCE_ALLOW_DEV_TOKENS", "true").lower() == "true",
    )
