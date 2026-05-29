from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from claims_service.database import Base
from claims_service.models import ClaimEventRecord, ClaimStatusHistoryRecord
from claims_service.repository import ClaimsRepository


def _session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return Session()


def test_create_fnol_persists_claim_status_history_and_event():
    session = _session()
    repository = ClaimsRepository(session)

    claim = repository.create_fnol(
        policy_id="policy-1",
        tenant_id="tenant-1",
        customer_id="customer-1",
        loss_type="collision",
        loss_date=datetime(2026, 1, 1),
        loss_location="Charlotte, NC",
        description="Minor accident",
        police_report_indicator=False,
        injuries_indicator=False,
        preferred_contact_method="email",
        fnol_payload={"source": "test"},
        actor_id="customer-1",
    )

    assert claim.claim_id
    assert claim.tenant_id == "tenant-1"
    assert claim.customer_id == "customer-1"
    assert claim.severity == "low"
    assert session.query(ClaimStatusHistoryRecord).count() == 1
    assert session.query(ClaimEventRecord).count() == 1


def test_list_scopes_by_customer():
    session = _session()
    repository = ClaimsRepository(session)
    for customer_id in ["customer-1", "customer-2"]:
        repository.create_fnol(
            policy_id=f"policy-{customer_id}",
            tenant_id="tenant-1",
            customer_id=customer_id,
            loss_type="collision",
            loss_date=datetime(2026, 1, 1),
            loss_location="Charlotte, NC",
            description="Minor accident",
            police_report_indicator=False,
            injuries_indicator=False,
            preferred_contact_method="email",
            fnol_payload={},
            actor_id=customer_id,
        )

    results = repository.list(tenant_id="tenant-1", customer_id="customer-1")
    assert len(results) == 1
    assert results[0].customer_id == "customer-1"
