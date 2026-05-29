from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from quote_service.api.app import app, get_quote_repository, init_engine
from quote_service.storage.database import Base
from quote_service.storage.quote_repository import QuoteRepository


PRODUCT_YAML = "data/sample-products/sample_personal_auto_v1.yml"


def _repository_override():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    session = Session()
    repository = QuoteRepository(session)
    return lambda: repository


def _client():
    init_engine(PRODUCT_YAML)
    app.dependency_overrides[get_quote_repository] = _repository_override()
    return TestClient(app)


def _headers(role="AGENT"):
    return {"Authorization": f"Bearer dev:test-user:{role}"}


def _quote_payload():
    return {
        "applicant_data": {
            "age": 35,
            "vehicle_year": 2023,
            "coverage_type": "standard",
            "vehicle_value": 25000,
            "driving_years": 15,
            "claims_3yr": 0,
            "credit_tier": "a",
        },
        "validity_days": 30,
    }


def test_quote_creation_requires_auth():
    client = _client()
    response = client.post("/quotes", json=_quote_payload())
    assert response.status_code == 401
    app.dependency_overrides.clear()


def test_quote_create_get_explain_and_accept_flow():
    client = _client()
    created = client.post("/quotes", json=_quote_payload(), headers=_headers("AGENT"))
    assert created.status_code == 200
    quote_id = created.json()["quote_id"]

    fetched = client.get(f"/quotes/{quote_id}", headers=_headers("AGENT"))
    assert fetched.status_code == 200
    assert fetched.json()["quote_id"] == quote_id

    explained = client.get(f"/quotes/{quote_id}/explain", headers=_headers("AGENT"))
    assert explained.status_code == 200
    assert explained.json()["quote_id"] == quote_id
    assert "Total Premium" in explained.json()["text_explanation"]

    accepted = client.post(f"/quotes/{quote_id}/accept", headers=_headers("UNDERWRITER_L1"))
    if created.json()["bind_eligible"]:
        assert accepted.status_code == 200
        assert accepted.json()["status"] == "CONVERTED"
    else:
        assert accepted.status_code == 409
    app.dependency_overrides.clear()
