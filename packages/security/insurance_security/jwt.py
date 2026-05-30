"""JWT validation helpers for production authentication mode."""

from __future__ import annotations

from typing import Any

import jwt
from jwt import PyJWKClient

from insurance_security.fastapi import ActorContext, Role
from insurance_security.settings import SecuritySettings


class JWTValidationError(ValueError):
    """Raised when a bearer JWT cannot be validated."""


def _decode_hs256(token: str, settings: SecuritySettings) -> dict[str, Any]:
    if not settings.jwt_hs256_secret:
        raise JWTValidationError("INSURANCE_JWT_HS256_SECRET is required in HS256 jwt auth mode")
    return jwt.decode(
        token,
        settings.jwt_hs256_secret,
        algorithms=["HS256"],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        options={"require": ["sub"]},
    )


def _decode_jwks(token: str, settings: SecuritySettings) -> dict[str, Any]:
    if not settings.jwt_jwks_url:
        raise JWTValidationError("INSURANCE_JWT_JWKS_URL is required in RS256 jwt auth mode")
    client = PyJWKClient(settings.jwt_jwks_url)
    signing_key = client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=[settings.jwt_algorithm],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        options={"require": ["sub"]},
    )


def _extract_role_values(claims: dict[str, Any], settings: SecuritySettings) -> list[str]:
    raw_roles = claims.get(settings.jwt_roles_claim) or claims.get("roles") or claims.get("role") or []
    if isinstance(raw_roles, str):
        return [raw_roles]
    if isinstance(raw_roles, list | tuple | set):
        return [str(value) for value in raw_roles]
    raise JWTValidationError("JWT roles claim must be a string or list")


def _map_role(role_value: str, settings: SecuritySettings) -> Role:
    role_map = settings.jwt_role_map or {}
    mapped = role_map.get(role_value, role_map.get(role_value.lower(), role_value))
    return Role(str(mapped).upper())


def validate_jwt_token(token: str, settings: SecuritySettings) -> ActorContext:
    """Validate a signed JWT and convert claims into ActorContext.

    Supported production modes:
    - HS256 with INSURANCE_JWT_HS256_SECRET for internal/test deployments.
    - RS256/ES256/etc. with INSURANCE_JWT_JWKS_URL through PyJWT PyJWKClient.
    """
    try:
        if settings.jwt_algorithm == "HS256":
            claims = _decode_hs256(token, settings)
        else:
            claims = _decode_jwks(token, settings)
    except jwt.PyJWTError as exc:
        raise JWTValidationError(str(exc)) from exc

    actor_id = str(claims.get("sub") or "")
    if not actor_id:
        raise JWTValidationError("JWT missing sub claim")

    role_values = _extract_role_values(claims, settings)
    roles: set[Role] = set()
    for role_value in role_values:
        roles.add(_map_role(role_value, settings))
    if not roles:
        raise JWTValidationError("JWT missing roles claim")

    return ActorContext(
        actor_id=actor_id,
        roles=frozenset(roles),
        raw_token_type="jwt",
        tenant_id=claims.get("tenant_id"),
        customer_id=claims.get("customer_id"),
    )
