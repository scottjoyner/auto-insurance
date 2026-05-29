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


def test_fnol_requires_authentication():
    client = _client()
    response = client.post("/claims/fnol", json=_payload())
    assert response.status_code == 401
    app.dependency_overrides.clear()


def test_create_get_and_list_claim_for_owner():
    client = _client()
    created = client.post("/claims/fnol", json=_payload(), headers=_headers())
    assert created.status_code == 200
    claim_id = created.json()["claim_id"]

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
