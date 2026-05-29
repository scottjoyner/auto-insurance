"""Quote ownership guard helpers.

These helpers centralize tenant/customer checks while the quote repository is
being migrated to first-class ownership-aware query methods.
"""

from __future__ import annotations

from fastapi import HTTPException
from insurance_security.fastapi import ActorContext
from quote_service.storage.orm import QuoteRecord
from sqlalchemy.orm import Session


def require_quote_access(session: Session, quote_id: str, actor: ActorContext) -> QuoteRecord:
    """Load a quote record and enforce tenant/customer ownership."""
    record = session.get(QuoteRecord, str(quote_id))
    if record is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    if not actor.can_access_customer(record.customer_id, record.tenant_id):
        raise HTTPException(status_code=403, detail="Quote access denied")
    return record


def quote_list_scope(actor: ActorContext) -> dict[str, str | None]:
    """Return safe tenant/customer filters for list endpoints."""
    if actor.is_privileged():
        return {"tenant_id": None, "customer_id": None}
    if actor.customer_id:
        return {"tenant_id": actor.tenant_id, "customer_id": actor.customer_id}
    return {"tenant_id": actor.tenant_id, "customer_id": None}
