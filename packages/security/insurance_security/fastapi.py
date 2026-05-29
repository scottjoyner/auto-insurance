"""FastAPI authentication and authorization helpers.

This module intentionally implements a small development-time bearer-token
contract. It is not a production identity provider. The contract gives every
service a shared deny-by-default authorization layer while the platform is still
in prototype mode.

Accepted development tokens:
- ``dev:<actor_id>:<ROLE>[,<ROLE>...]``
- ``dev:<actor_id>:<ROLE>[,<ROLE>...]:<tenant_id>:<customer_id>``
- ``system:<actor_id>``

Production hardening work remains in P0/P1: JWT signature verification, key
rotation, issuer/audience checks, tenant scoping, and centralized policy
decision logging.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from fastapi import Depends, Header, HTTPException, status


class Role(StrEnum):
    """Canonical authorization roles for the insurance operating system."""

    CUSTOMER = "CUSTOMER"
    AGENT = "AGENT"
    UNDERWRITER_L1 = "UNDERWRITER_L1"
    UNDERWRITER_L2 = "UNDERWRITER_L2"
    CLAIMS_MANAGER = "CLAIMS_MANAGER"
    TREASURY_APPROVER = "TREASURY_APPROVER"
    SMART_CONTRACT_SIGNER = "SMART_CONTRACT_SIGNER"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"


@dataclass(frozen=True)
class ActorContext:
    """Authenticated caller context injected into service endpoints."""

    actor_id: str
    roles: frozenset[Role]
    raw_token_type: str = "development"
    tenant_id: str | None = None
    customer_id: str | None = None

    def has_any_role(self, allowed_roles: Iterable[Role]) -> bool:
        return bool(self.roles.intersection(set(allowed_roles)))

    def is_privileged(self) -> bool:
        return self.has_any_role({Role.SYSTEM, Role.ADMIN, Role.UNDERWRITER_L1, Role.UNDERWRITER_L2})

    def can_access_customer(self, customer_id: str | None, tenant_id: str | None = None) -> bool:
        """Return whether actor can access a customer-owned resource.

        Prototype rule: system/admin/underwriters can access all resources;
        agents are tenant-scoped when tenant_id is provided; customers are
        restricted to their own customer_id.
        """
        if self.is_privileged():
            return True
        if tenant_id and self.tenant_id and self.tenant_id != tenant_id:
            return False
        if self.has_any_role({Role.AGENT}) and (tenant_id is None or self.tenant_id == tenant_id):
            return True
        if self.has_any_role({Role.CUSTOMER}) and customer_id and self.customer_id == customer_id:
            return True
        return False


def _parse_dev_token(token: str) -> ActorContext:
    """Parse the prototype bearer-token contract.

    This intentionally avoids accepting arbitrary opaque tokens. Unknown role
    strings and malformed tokens fail closed.
    """

    if token.startswith("system:"):
        _, actor_id = token.split(":", 1)
        if not actor_id:
            raise ValueError("system token missing actor id")
        return ActorContext(actor_id=actor_id, roles=frozenset({Role.SYSTEM}))

    if not token.startswith("dev:"):
        raise ValueError("unsupported token type")

    parts = token.split(":")
    if len(parts) not in {3, 5}:
        raise ValueError("expected dev:<actor_id>:<roles>[:<tenant_id>:<customer_id>]")

    _, actor_id, role_csv = parts[:3]
    tenant_id = parts[3] if len(parts) == 5 and parts[3] else None
    customer_id = parts[4] if len(parts) == 5 and parts[4] else None
    if not actor_id or not role_csv:
        raise ValueError("token missing actor id or roles")

    roles: set[Role] = set()
    for role_text in role_csv.split(","):
        role_text = role_text.strip().upper()
        if not role_text:
            continue
        roles.add(Role(role_text))

    if not roles:
        raise ValueError("token has no valid roles")

    return ActorContext(actor_id=actor_id, roles=frozenset(roles), tenant_id=tenant_id, customer_id=customer_id)


def get_actor_context(authorization: str | None = Header(default=None)) -> ActorContext:
    """Resolve the current actor from the Authorization header."""

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[len(prefix) :].strip()
    try:
        return _parse_dev_token(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_roles(*allowed_roles: Role):
    """FastAPI dependency factory that enforces role-based access.

    ``SYSTEM`` and ``ADMIN`` are privileged roles and are accepted for every
    protected endpoint. Health endpoints should not use this dependency.
    """

    allowed = frozenset(allowed_roles)
    privileged = frozenset({Role.SYSTEM, Role.ADMIN})

    def dependency(actor: ActorContext = Depends(get_actor_context)) -> ActorContext:
        if actor.has_any_role(allowed.union(privileged)):
            return actor
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role for this operation",
        )

    return dependency
