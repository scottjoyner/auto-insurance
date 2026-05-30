"""Customer service API."""

from __future__ import annotations

from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from insurance_observability import CorrelationIdMiddleware
from insurance_security.fastapi import ActorContext, Role, require_roles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from customer_service.config import settings
from customer_service.database import create_schema, get_session
from customer_service.models import (
    AccountRecord,
    AddressRecord,
    ContactRecord,
    CustomerEventRecord,
    CustomerRecord,
    IdentityLinkRecord,
    TenantRecord,
)

app = FastAPI(title="Customer Service", version="0.1.0")
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.on_event("startup")
def startup_event():
    if settings.auto_create_schema:
        create_schema()


admin_actor = require_roles(Role.ADMIN, Role.SYSTEM)
customer_read_actor = require_roles(Role.CUSTOMER, Role.AGENT, Role.UNDERWRITER_L1, Role.CLAIMS_MANAGER, Role.ADMIN, Role.SYSTEM)
customer_write_actor = require_roles(Role.AGENT, Role.ADMIN, Role.SYSTEM)


class TenantInput(BaseModel):
    tenant_id: str
    name: str


class AccountInput(BaseModel):
    tenant_id: str
    name: str
    account_type: str = "personal"


class CustomerInput(BaseModel):
    tenant_id: str
    account_id: str
    first_name: str = ""
    last_name: str = ""


class ContactInput(BaseModel):
    contact_type: str = "email"
    value: str
    is_primary: bool = False


class AddressInput(BaseModel):
    address_type: str = "mailing"
    line1: str
    line2: str = ""
    city: str
    state: str
    postal_code: str
    country: str = "US"


class IdentityLinkInput(BaseModel):
    provider: str
    subject: str


class CustomerResponse(BaseModel):
    customer_id: str
    tenant_id: str
    account_id: str
    display_name: str
    status: str


class ContactResponse(BaseModel):
    contact_id: str
    customer_id: str
    contact_type: str
    value: str
    is_primary: bool


class AddressResponse(BaseModel):
    address_id: str
    customer_id: str
    address_type: str
    line1: str
    line2: str
    city: str
    state: str
    postal_code: str
    country: str


class IdentityLinkResponse(BaseModel):
    identity_link_id: str
    tenant_id: str
    customer_id: str
    provider: str
    subject: str


class CustomerSummary(BaseModel):
    customer: CustomerResponse
    contacts: list[ContactResponse] = Field(default_factory=list)
    addresses: list[AddressResponse] = Field(default_factory=list)


def _customer_response(record: CustomerRecord) -> CustomerResponse:
    return CustomerResponse(
        customer_id=record.customer_id,
        tenant_id=record.tenant_id,
        account_id=record.account_id,
        display_name=record.display_name,
        status=record.status,
    )


def _contact_response(record: ContactRecord) -> ContactResponse:
    return ContactResponse(
        contact_id=record.contact_id,
        customer_id=record.customer_id,
        contact_type=record.contact_type,
        value=record.value,
        is_primary=record.is_primary,
    )


def _address_response(record: AddressRecord) -> AddressResponse:
    return AddressResponse(
        address_id=record.address_id,
        customer_id=record.customer_id,
        address_type=record.address_type,
        line1=record.line1,
        line2=record.line2,
        city=record.city,
        state=record.state,
        postal_code=record.postal_code,
        country=record.country,
    )


def _identity_response(record: IdentityLinkRecord) -> IdentityLinkResponse:
    return IdentityLinkResponse(
        identity_link_id=record.identity_link_id,
        tenant_id=record.tenant_id,
        customer_id=record.customer_id,
        provider=record.provider,
        subject=record.subject,
    )


def _require_customer_access(record: CustomerRecord | None, actor: ActorContext) -> CustomerRecord:
    if record is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    if not actor.can_access_customer(record.customer_id, record.tenant_id):
        raise HTTPException(status_code=403, detail="Customer access denied")
    return record


def _require_tenant_scope(tenant_id: str, actor: ActorContext) -> None:
    if actor.is_privileged():
        return
    if actor.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant access denied")


@app.post("/tenants")
def create_tenant(input_data: TenantInput, actor: ActorContext = Depends(admin_actor), session: Session = Depends(get_session)):
    existing = session.get(TenantRecord, input_data.tenant_id)
    if existing is not None:
        return {"tenant_id": existing.tenant_id, "name": existing.name, "status": existing.status}
    tenant = TenantRecord(tenant_id=input_data.tenant_id, name=input_data.name, created_by_actor_id=actor.actor_id)
    session.add(tenant)
    session.add(CustomerEventRecord(event_id=str(uuid4()), event_type="TenantCreated", aggregate_id=tenant.tenant_id, actor_id=actor.actor_id, payload={"name": tenant.name}))
    session.commit()
    return {"tenant_id": tenant.tenant_id, "name": tenant.name, "status": tenant.status}


@app.post("/accounts")
def create_account(input_data: AccountInput, actor: ActorContext = Depends(admin_actor), session: Session = Depends(get_session)):
    if session.get(TenantRecord, input_data.tenant_id) is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    account = AccountRecord(account_id=str(uuid4()), tenant_id=input_data.tenant_id, name=input_data.name, account_type=input_data.account_type, created_by_actor_id=actor.actor_id)
    session.add(account)
    session.add(CustomerEventRecord(event_id=str(uuid4()), event_type="AccountCreated", aggregate_id=account.account_id, actor_id=actor.actor_id, payload={"tenant_id": account.tenant_id}))
    session.commit()
    return {"account_id": account.account_id, "tenant_id": account.tenant_id, "name": account.name, "status": account.status}


@app.post("/customers", response_model=CustomerResponse)
def create_customer(input_data: CustomerInput, actor: ActorContext = Depends(customer_write_actor), session: Session = Depends(get_session)):
    _require_tenant_scope(input_data.tenant_id, actor)
    account = session.get(AccountRecord, input_data.account_id)
    if account is None or account.tenant_id != input_data.tenant_id:
        raise HTTPException(status_code=404, detail="Account not found")
    display_name = f"{input_data.first_name} {input_data.last_name}".strip() or "Unnamed Customer"
    record = CustomerRecord(customer_id=str(uuid4()), tenant_id=input_data.tenant_id, account_id=input_data.account_id, first_name=input_data.first_name, last_name=input_data.last_name, display_name=display_name, created_by_actor_id=actor.actor_id)
    session.add(record)
    session.add(CustomerEventRecord(event_id=str(uuid4()), event_type="CustomerCreated", aggregate_id=record.customer_id, actor_id=actor.actor_id, payload={"tenant_id": record.tenant_id, "account_id": record.account_id}))
    session.commit()
    return _customer_response(record)


@app.post("/customers/{customer_id}/contacts", response_model=ContactResponse)
def create_contact(customer_id: str, input_data: ContactInput, actor: ActorContext = Depends(customer_write_actor), session: Session = Depends(get_session)):
    customer = _require_customer_access(session.get(CustomerRecord, customer_id), actor)
    record = ContactRecord(contact_id=str(uuid4()), tenant_id=customer.tenant_id, customer_id=customer.customer_id, contact_type=input_data.contact_type, value=input_data.value, is_primary=input_data.is_primary)
    session.add(record)
    session.add(CustomerEventRecord(event_id=str(uuid4()), event_type="CustomerContactCreated", aggregate_id=customer.customer_id, actor_id=actor.actor_id, payload={"contact_type": record.contact_type}))
    session.commit()
    return _contact_response(record)


@app.post("/customers/{customer_id}/addresses", response_model=AddressResponse)
def create_address(customer_id: str, input_data: AddressInput, actor: ActorContext = Depends(customer_write_actor), session: Session = Depends(get_session)):
    customer = _require_customer_access(session.get(CustomerRecord, customer_id), actor)
    record = AddressRecord(address_id=str(uuid4()), tenant_id=customer.tenant_id, customer_id=customer.customer_id, address_type=input_data.address_type, line1=input_data.line1, line2=input_data.line2, city=input_data.city, state=input_data.state, postal_code=input_data.postal_code, country=input_data.country)
    session.add(record)
    session.add(CustomerEventRecord(event_id=str(uuid4()), event_type="CustomerAddressCreated", aggregate_id=customer.customer_id, actor_id=actor.actor_id, payload={"address_type": record.address_type}))
    session.commit()
    return _address_response(record)


@app.post("/customers/{customer_id}/identity-links", response_model=IdentityLinkResponse)
def create_identity_link(customer_id: str, input_data: IdentityLinkInput, actor: ActorContext = Depends(admin_actor), session: Session = Depends(get_session)):
    customer = _require_customer_access(session.get(CustomerRecord, customer_id), actor)
    record = IdentityLinkRecord(identity_link_id=str(uuid4()), tenant_id=customer.tenant_id, customer_id=customer.customer_id, provider=input_data.provider, subject=input_data.subject)
    session.add(record)
    session.add(CustomerEventRecord(event_id=str(uuid4()), event_type="CustomerIdentityLinked", aggregate_id=customer.customer_id, actor_id=actor.actor_id, payload={"provider": record.provider}))
    session.commit()
    return _identity_response(record)


@app.get("/identity-links/{provider}/{subject}", response_model=IdentityLinkResponse)
def get_identity_link(provider: str, subject: str, actor: ActorContext = Depends(admin_actor), session: Session = Depends(get_session)):
    record = session.query(IdentityLinkRecord).filter(IdentityLinkRecord.provider == provider).filter(IdentityLinkRecord.subject == subject).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Identity link not found")
    return _identity_response(record)


@app.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str, actor: ActorContext = Depends(customer_read_actor), session: Session = Depends(get_session)):
    return _customer_response(_require_customer_access(session.get(CustomerRecord, customer_id), actor))


@app.get("/customers", response_model=list[CustomerResponse])
def search_customers(q: str | None = Query(default=None), limit: int = Query(default=100, ge=1, le=500), actor: ActorContext = Depends(customer_read_actor), session: Session = Depends(get_session)):
    query = session.query(CustomerRecord).order_by(CustomerRecord.created_at.desc())
    if not actor.is_privileged() and actor.tenant_id:
        query = query.filter(CustomerRecord.tenant_id == actor.tenant_id)
    if not actor.is_privileged() and actor.customer_id:
        query = query.filter(CustomerRecord.customer_id == actor.customer_id)
    if q:
        query = query.filter(CustomerRecord.display_name.like(f"%{q}%"))
    return [_customer_response(record) for record in query.limit(limit).all()]


@app.get("/customers/{customer_id}/summary", response_model=CustomerSummary)
def customer_summary(customer_id: str, actor: ActorContext = Depends(customer_read_actor), session: Session = Depends(get_session)):
    record = _require_customer_access(session.get(CustomerRecord, customer_id), actor)
    contacts = session.query(ContactRecord).filter(ContactRecord.customer_id == customer_id).all()
    addresses = session.query(AddressRecord).filter(AddressRecord.customer_id == customer_id).all()
    return CustomerSummary(customer=_customer_response(record), contacts=[_contact_response(item) for item in contacts], addresses=[_address_response(item) for item in addresses])


@app.get("/health")
def health():
    return {"status": "healthy", "service": "customer-service", "persistence": "sqlalchemy"}
