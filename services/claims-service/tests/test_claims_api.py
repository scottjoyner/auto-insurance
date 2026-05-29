from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from claims_service.api import app, get_repository
from claims_service.database import Base
from claims_service.repository import ClaimsRepository


def _repository_override():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    session = Session()
    repository = ClaimsRepository(session)
    return lambda: repository


def _client():
    app.dependency_overrides[get_repository] = _repository_override()
    return TestClient(app)


def _headers(role="CUSTOMER", tenant="tenant-1", customer="customer-1"):
    return {"Authorization": f"Bearer dev:test-user:{role}:{tenant}:{customer}"}


def _payload(policy_id="policy-1", injuries=False):
    return {
        "policy_id": policy_id,
        "loss_type": "collision",
        "loss_date": datetime(2026, 1, 1).isoformat(),
        "loss_location": "Charlotte, NC",
        "description": "Minor accident",
        "police_report_indicator": False,
        "injuries_indicator": injuries,
        "preferred_contact_method": "email",
    }


def _create_claim(client):
    created = client.post("/claims/fnol", json=_payload(), headers=_headers())
    assert created.status_code == 200
    return created.json()["claim_id"]


def test_fnol_requires_authentication():
    client = _client()
    response = client.post("/claims/fnol", json=_payload())
    assert response.status_code == 401
    app.dependency_overrides.clear()


def test_create_get_and_list_claim_for_owner():
    client = _client()
    claim_id = _create_claim(client)

    detail = client.get(f"/claims/{claim_id}", headers=_headers())
    assert detail.status_code == 200
    assert detail.json()["claim_id"] == claim_id

    listed = client.get("/claims", headers=_headers())
    assert listed.status_code == 200
    assert {item["claim_id"] for item in listed.json()} == {claim_id}
    app.dependency_overrides.clear()


def test_customer_cannot_read_another_customer_claim():
    client = _client()
    created = client.post("/claims/fnol", json=_payload(), headers=_headers("CUSTOMER", "tenant-1", "customer-1"))
    assert created.status_code == 200
    claim_id = created.json()["claim_id"]

    forbidden = client.get(f"/claims/{claim_id}", headers=_headers("CUSTOMER", "tenant-1", "customer-2"))
    assert forbidden.status_code == 403
    app.dependency_overrides.clear()


def test_injury_claim_routes_to_manager_approval():
    client = _client()
    created = client.post("/claims/fnol", json=_payload(injuries=True), headers=_headers())
    assert created.status_code == 200
    assert created.json()["severity"] == "high"
    assert created.json()["queue"] == "Manager Approval"
    app.dependency_overrides.clear()


def test_add_evidence_metadata():
    client = _client()
    claim_id = _create_claim(client)
    response = client.post(
        f"/claims/{claim_id}/evidence",
        json={"evidence_type": "photo", "uri": "s3://bucket/photo.jpg", "checksum": "abc123"},
        headers=_headers(),
    )
    assert response.status_code == 200
    assert response.json()["evidence_type"] == "photo"
    assert response.json()["checksum"] == "abc123"
    app.dependency_overrides.clear()


def test_reserve_requires_manager_approval():
    client = _client()
    claim_id = _create_claim(client)
    reserve = client.post(
        f"/claims/{claim_id}/reserves",
        json={"amount": 2500.0, "reason": "Initial estimate"},
        headers=_headers("AGENT", "tenant-1", "customer-1"),
    )
    assert reserve.status_code == 200
    assert reserve.json()["status"] == "pending_approval"

    denied = client.post(f"/claims/reserves/{reserve.json()['id']}/approve", headers=_headers("AGENT", "tenant-1", "customer-1"))
    assert denied.status_code == 403

    approved = client.post(f"/claims/reserves/{reserve.json()['id']}/approve", headers=_headers("CLAIMS_MANAGER", "tenant-1", "customer-1"))
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    app.dependency_overrides.clear()


def test_denial_review_generates_notice_draft():
    client = _client()
    claim_id = _create_claim(client)
    response = client.post(
        f"/claims/{claim_id}/denial-review",
        json={
            "reason": "Coverage exclusion review",
            "customer_name": "Jane Doe",
            "jurisdiction": "NC",
            "reason_codes": ["coverage_exclusion_review"],
        },
        headers=_headers("CLAIMS_MANAGER", "tenant-1", "customer-1"),
    )
    assert response.status_code == 200
    assert response.json()["claim"]["status"] == "denied pending manager review"
    assert "coverage_exclusion_review" in response.json()["adverse_action_notice_draft"]
    app.dependency_overrides.clear()
