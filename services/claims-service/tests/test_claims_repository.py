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


def _claim(repository: ClaimsRepository, customer_id="customer-1"):
    return repository.create_fnol(
        policy_id="policy-1",
        tenant_id="tenant-1",
        customer_id=customer_id,
        loss_type="collision",
        loss_date=datetime(2026, 1, 1),
        loss_location="Charlotte, NC",
        description="Minor accident",
        police_report_indicator=False,
        injuries_indicator=False,
        preferred_contact_method="email",
        fnol_payload={"source": "test"},
        actor_id=customer_id,
    )


def test_create_fnol_persists_claim_status_history_and_event():
    session = _session()
    repository = ClaimsRepository(session)

    claim = _claim(repository)

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
        _claim(repository, customer_id=customer_id)

    results = repository.list(tenant_id="tenant-1", customer_id="customer-1")
    assert len(results) == 1
    assert results[0].customer_id == "customer-1"


def test_evidence_reserve_and_denial_workflow_emit_events():
    session = _session()
    repository = ClaimsRepository(session)
    claim = _claim(repository)

    evidence = repository.add_evidence(
        claim_id=claim.claim_id,
        evidence_type="photo",
        source="customer",
        uri="s3://bucket/photo.jpg",
        checksum="abc123",
        visibility="internal",
        actor_id="customer-1",
    )
    reserve = repository.recommend_reserve(
        claim_id=claim.claim_id,
        amount=2500.0,
        reason="Initial estimate",
        actor_id="adjuster-1",
    )
    approved = repository.approve_reserve(reserve_id=reserve.id, actor_id="claims-manager-1")
    denial = repository.mark_denial_review(
        claim_id=claim.claim_id,
        reason="Coverage exclusion review",
        actor_id="claims-manager-1",
    )

    assert evidence.evidence_id
    assert reserve.status == "pending_approval"
    assert approved.status == "approved"
    assert denial.status == "denied pending manager review"
    assert denial.queue == "Denial Review"
    assert session.query(ClaimEventRecord).count() == 5
    assert session.query(ClaimStatusHistoryRecord).count() == 2
