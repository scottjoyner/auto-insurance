"""Quote ownership guard helpers."""

from __future__ import annotations

from fastapi import HTTPException
from insurance_security.fastapi import ActorContext
from quote_service.storage.orm import QuoteRecord
from sqlalchemy.orm import Session


def stamp_quote_owner(session: Session, quote_id: str, actor: ActorContext) -> None:
    """Persist tenant/customer ownership metadata on a quote record."""
    record = session.get(QuoteRecord, str(quote_id))
    if record is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    if actor.tenant_id and not record.tenant_id:
        record.tenant_id = actor.tenant_id
    if actor.customer_id and not record.customer_id:
        record.customer_id = actor.customer_id
    session.commit()


def require_quote_access(session: Session, quote_id: str, actor: ActorContext) -> QuoteRecord:
    """Load a quote record and enforce tenant/customer ownership."""
    record = session.get(QuoteRecord, str(quote_id))
    if record is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    if not actor.can_access_customer(record.customer_id, record.tenant_id):
        raise HTTPException(status_code=403, detail="Quote access denied")
    return record


def scoped_quote_query(session: Session, actor: ActorContext):
    """Return a query scoped to the actor's tenant/customer access."""
    query = session.query(QuoteRecord)
    if actor.is_privileged():
        return query
    if actor.tenant_id:
        query = query.filter(QuoteRecord.tenant_id == actor.tenant_id)
    if actor.customer_id:
        query = query.filter(QuoteRecord.customer_id == actor.customer_id)
    return query


def quote_list_scope(actor: ActorContext) -> dict[str, str | None]:
    """Return safe tenant/customer filters for list endpoints."""
    if actor.is_privileged():
        return {"tenant_id": None, "customer_id": None}
    if actor.customer_id:
        return {"tenant_id": actor.tenant_id, "customer_id": actor.customer_id}
    return {"tenant_id": actor.tenant_id, "customer_id": None}
