from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from policy_service.api.app import app, get_repository
from policy_service.storage.database import Base
from policy_service.storage.policy_repository import PolicyRepository


def _repository_override():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    session = Session()
    repository = PolicyRepository(session)
    return lambda: repository


def _client():
    app.dependency_overrides[get_repository] = _repository_override()
    return TestClient(app)


def _headers(role="AGENT"):
    return {"Authorization": f"Bearer dev:test-user:{role}"}


def _bind_payload(**overrides):
    now = datetime.utcnow()
    payload = {
        "quote_id": str(uuid4()),
        "effective_date": now.isoformat(),
        "expiration_date": (now + timedelta(days=365)).isoformat(),
        "quote_snapshot": {"status": "QUOTED", "bind_eligible": True, "total_premium": 1200.0},
        "risk_assessment_snapshot": {"decision": "ACCEPT"},
        "request_key": "api-bind-1",
    }
    payload.update(overrides)
    return payload


def test_bind_request_requires_auth():
    client = _client()
    response = client.post("/bind-requests", json={})
    assert response.status_code == 401
    app.dependency_overrides.clear()


def test_bind_request_and_approval_flow():
    client = _client()
    payload = _bind_payload()

    created = client.post("/bind-requests", json=payload, headers=_headers("AGENT"))
    duplicate = client.post("/bind-requests", json=payload, headers={**_headers("AGENT"), "Idempotency-Key": "api-bind-1"})

    assert created.status_code == 200
    assert duplicate.status_code == 200
    assert duplicate.json()["bind_request_id"] == created.json()["bind_request_id"]

    approved = client.post(
        f"/bind-requests/{created.json()['bind_request_id']}/approve",
        json={"approval_status": "approved", "comments": "Approved"},
        headers=_headers("UNDERWRITER_L1"),
    )
    assert approved.status_code == 200
    assert approved.json()["state"] == "active"

    policy = client.get(f"/policies/{approved.json()['policy_id']}", headers=_headers("AGENT"))
    assert policy.status_code == 200
    assert policy.json()["policy_id"] == approved.json()["policy_id"]
    app.dependency_overrides.clear()


def test_bind_request_blocks_decline_decision():
    client = _client()
    payload = _bind_payload(risk_assessment_snapshot={"decision": "DECLINE"}, request_key="decline-bind")
    response = client.post("/bind-requests", json=payload, headers=_headers("AGENT"))
    assert response.status_code == 409
    assert "risk_decision_requires_adverse_action_review" in response.json()["detail"]["reason_codes"]
    app.dependency_overrides.clear()


def test_bind_request_blocks_non_bind_eligible_quote():
    client = _client()
    payload = _bind_payload(quote_snapshot={"status": "QUOTED", "bind_eligible": False, "total_premium": 1200.0}, request_key="non-bind")
    response = client.post("/bind-requests", json=payload, headers=_headers("AGENT"))
    assert response.status_code == 409
    assert "quote_not_bind_eligible" in response.json()["detail"]["reason_codes"]
    app.dependency_overrides.clear()
