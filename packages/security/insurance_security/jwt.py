"""JWT validation helpers for production authentication mode."""

from __future__ import annotations

from typing import Any

import jwt

from insurance_security.fastapi import ActorContext, Role
from insurance_security.settings import SecuritySettings


class JWTValidationError(ValueError):
    """Raised when a bearer JWT cannot be validated."""


def validate_jwt_token(token: str, settings: SecuritySettings) -> ActorContext:
    """Validate a signed JWT and convert claims into ActorContext.

    Phase 2 production path supports HS256 shared-secret validation and validates
    issuer/audience when configured. A JWKS/RS256 resolver should replace or
    extend this for external IdPs.
    """
    if settings.jwt_algorithm != "HS256":
        raise JWTValidationError("Only HS256 is implemented in this production-gap pass; add JWKS/RS256 before external IdP use")
    if not settings.jwt_hs256_secret:
        raise JWTValidationError("INSURANCE_JWT_HS256_SECRET is required in jwt auth mode")

    options: dict[str, Any] = {"require": ["sub"]}
    try:
        claims = jwt.decode(
            token,
            settings.jwt_hs256_secret,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options=options,
        )
    except jwt.PyJWTError as exc:
        raise JWTValidationError(str(exc)) from exc

    actor_id = str(claims.get("sub") or "")
    if not actor_id:
        raise JWTValidationError("JWT missing sub claim")

    role_values = claims.get("roles") or claims.get("role") or []
    if isinstance(role_values, str):
        role_values = [role_values]
    roles: set[Role] = set()
    for role_value in role_values:
        roles.add(Role(str(role_value).upper()))
    if not roles:
        raise JWTValidationError("JWT missing roles claim")

    return ActorContext(
        actor_id=actor_id,
        roles=frozenset(roles),
        raw_token_type="jwt",
        tenant_id=claims.get("tenant_id"),
        customer_id=claims.get("customer_id"),
    )
