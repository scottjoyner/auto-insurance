"""Customer-service validation helper for claims workflows."""

from __future__ import annotations

import httpx
from fastapi import HTTPException

from insurance_security.fastapi import ActorContext


def validate_actor_customer(
    *,
    actor: ActorContext,
    customer_service_url: str,
    bearer_token: str,
    timeout: float = 3.0,
) -> None:
    """Validate actor tenant/customer against customer-service."""
    if actor.is_privileged() and not actor.customer_id:
        return
    if not actor.customer_id:
        raise HTTPException(status_code=400, detail="customer_id is required for customer validation")
    if not actor.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required for customer validation")

    url = f"{customer_service_url.rstrip('/')}/customers/{actor.customer_id}"
    try:
        response = httpx.get(url, headers={"Authorization": f"Bearer {bearer_token}"}, timeout=timeout)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Customer validation service unavailable") from exc

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Customer not found")
    if response.status_code == 403:
        raise HTTPException(status_code=403, detail="Customer access denied")
    if response.status_code >= 400:
        raise HTTPException(status_code=503, detail="Customer validation failed")

    body = response.json()
    if body.get("tenant_id") != actor.tenant_id or body.get("customer_id") != actor.customer_id:
        raise HTTPException(status_code=403, detail="Customer ownership mismatch")
