"""Shared security settings."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any


class SecuritySettingsError(ValueError):
    """Raised when security settings are not production-safe."""


@dataclass(frozen=True)
class SecuritySettings:
    auth_mode: str = "dev"
    jwt_issuer: str | None = None
    jwt_audience: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_hs256_secret: str | None = None
    jwt_jwks_url: str | None = None
    allow_dev_tokens: bool = True
    jwt_roles_claim: str = "roles"
    jwt_role_map: dict[str, str] | None = None


def _parse_role_map(raw_value: str | None) -> dict[str, str] | None:
    if not raw_value:
        return None
    try:
        parsed: Any = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise SecuritySettingsError("INSURANCE_JWT_ROLE_MAP must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise SecuritySettingsError("INSURANCE_JWT_ROLE_MAP must be a JSON object")
    role_map: dict[str, str] = {}
    for source, target in parsed.items():
        if not isinstance(source, str) or not isinstance(target, str):
            raise SecuritySettingsError("INSURANCE_JWT_ROLE_MAP keys and values must be strings")
        role_map[source] = target
    return role_map


def get_security_settings() -> SecuritySettings:
    return SecuritySettings(
        auth_mode=os.getenv("INSURANCE_AUTH_MODE", "dev").lower(),
        jwt_issuer=os.getenv("INSURANCE_JWT_ISSUER"),
        jwt_audience=os.getenv("INSURANCE_JWT_AUDIENCE"),
        jwt_algorithm=os.getenv("INSURANCE_JWT_ALGORITHM", "HS256"),
        jwt_hs256_secret=os.getenv("INSURANCE_JWT_HS256_SECRET"),
        jwt_jwks_url=os.getenv("INSURANCE_JWT_JWKS_URL"),
        allow_dev_tokens=os.getenv("INSURANCE_ALLOW_DEV_TOKENS", "true").lower() == "true",
        jwt_roles_claim=os.getenv("INSURANCE_JWT_ROLES_CLAIM", "roles"),
        jwt_role_map=_parse_role_map(os.getenv("INSURANCE_JWT_ROLE_MAP")),
    )


def validate_security_settings(settings: SecuritySettings | None = None) -> SecuritySettings:
    """Validate security settings and fail closed for production JWT mode.

    Dev mode remains permissive for local development. JWT mode requires issuer,
    audience, and a signing configuration. HS256 requires a shared secret. All
    asymmetric algorithms require a JWKS URL.
    """
    settings = settings or get_security_settings()
    auth_mode = settings.auth_mode.lower()
    if auth_mode not in {"dev", "jwt"}:
        raise SecuritySettingsError(f"Unsupported INSURANCE_AUTH_MODE: {settings.auth_mode}")
    if auth_mode == "dev":
        return settings

    if not settings.jwt_issuer:
        raise SecuritySettingsError("INSURANCE_JWT_ISSUER is required when INSURANCE_AUTH_MODE=jwt")
    if not settings.jwt_audience:
        raise SecuritySettingsError("INSURANCE_JWT_AUDIENCE is required when INSURANCE_AUTH_MODE=jwt")
    if not settings.jwt_algorithm:
        raise SecuritySettingsError("INSURANCE_JWT_ALGORITHM is required when INSURANCE_AUTH_MODE=jwt")
    if not settings.jwt_roles_claim:
        raise SecuritySettingsError("INSURANCE_JWT_ROLES_CLAIM cannot be empty")

    algorithm = settings.jwt_algorithm.upper()
    if algorithm == "HS256":
        if not settings.jwt_hs256_secret:
            raise SecuritySettingsError("INSURANCE_JWT_HS256_SECRET is required when INSURANCE_JWT_ALGORITHM=HS256")
    else:
        if not settings.jwt_jwks_url:
            raise SecuritySettingsError("INSURANCE_JWT_JWKS_URL is required for asymmetric JWT algorithms")

    return settings
