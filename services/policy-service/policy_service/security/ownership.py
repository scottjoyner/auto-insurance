"""Policy ownership guard helpers."""

from __future__ import annotations

from fastapi import HTTPException
from insurance_security.fastapi import ActorContext
from policy_service.storage.orm import BindRequestRecord, PolicyRecord
from sqlalchemy.orm import Session


def stamp_bind_owner(session: Session, bind_request_id: str, actor: ActorContext) -> None:
    record = session.get(BindRequestRecord, str(bind_request_id))
    if record is None:
        raise HTTPException(status_code=404, detail="Bind request not found")
    if actor.tenant_id and not record.tenant_id:
        record.tenant_id = actor.tenant_id
    if actor.customer_id and not record.customer_id:
        record.customer_id = actor.customer_id
    session.commit()


def stamp_policy_owner_from_bind(session: Session, policy_id: str, bind_request_id: str) -> None:
    policy = session.get(PolicyRecord, str(policy_id))
    bind_request = session.get(BindRequestRecord, str(bind_request_id))
    if policy is None or bind_request is None:
        return
    policy.tenant_id = bind_request.tenant_id
    policy.customer_id = bind_request.customer_id
    session.commit()


def require_bind_access(session: Session, bind_request_id: str, actor: ActorContext) -> BindRequestRecord:
    record = session.get(BindRequestRecord, str(bind_request_id))
    if record is None:
        raise HTTPException(status_code=404, detail="Bind request not found")
    if not actor.can_access_customer(record.customer_id, record.tenant_id):
        raise HTTPException(status_code=403, detail="Bind request access denied")
    return record


def require_policy_access(session: Session, policy_id: str, actor: ActorContext) -> PolicyRecord:
    record = session.get(PolicyRecord, str(policy_id))
    if record is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    if not actor.can_access_customer(record.customer_id, record.tenant_id):
        raise HTTPException(status_code=403, detail="Policy access denied")
    return record


def scoped_policy_query(session: Session, actor: ActorContext):
    query = session.query(PolicyRecord)
    if actor.is_privileged():
        return query
    if actor.tenant_id:
        query = query.filter(PolicyRecord.tenant_id == actor.tenant_id)
    if actor.customer_id:
        query = query.filter(PolicyRecord.customer_id == actor.customer_id)
    return query
