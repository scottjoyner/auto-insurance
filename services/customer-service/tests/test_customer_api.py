from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from customer_service.api import app
from customer_service.database import Base, get_session


def _session_override():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    session = Session()

    def override():
        return session

    return override


def _client():
    app.dependency_overrides[get_session] = _session_override()
    return TestClient(app)


def _headers(role="ADMIN", tenant="tenant-1", customer="customer-1"):
    return {"Authorization": f"Bearer dev:test-user:{role}:{tenant}:{customer}"}


def _seed_customer(client, tenant_id="tenant-1", first_name="Jane", last_name="Doe"):
    tenant = client.post("/tenants", json={"tenant_id": tenant_id, "name": tenant_id}, headers=_headers("ADMIN", tenant_id, "admin"))
    assert tenant.status_code == 200
    account = client.post("/accounts", json={"tenant_id": tenant_id, "name": "Household"}, headers=_headers("ADMIN", tenant_id, "admin"))
    assert account.status_code == 200
    customer = client.post(
        "/customers",
        json={"tenant_id": tenant_id, "account_id": account.json()["account_id"], "first_name": first_name, "last_name": last_name},
        headers=_headers("AGENT", tenant_id, "agent"),
    )
    assert customer.status_code == 200
    return customer.json()


def test_customer_creation_requires_auth():
    client = _client()
    response = client.post("/tenants", json={"tenant_id": "tenant-1", "name": "Tenant"})
    assert response.status_code == 401
    app.dependency_overrides.clear()


def test_create_tenant_account_customer_and_read():
    client = _client()
    customer = _seed_customer(client)

    fetched = client.get(f"/customers/{customer['customer_id']}", headers=_headers("CUSTOMER", "tenant-1", customer["customer_id"]))
    assert fetched.status_code == 200
    assert fetched.json()["display_name"] == "Jane Doe"

    summary = client.get(f"/customers/{customer['customer_id']}/summary", headers=_headers("CUSTOMER", "tenant-1", customer["customer_id"]))
    assert summary.status_code == 200
    assert summary.json()["customer"]["customer_id"] == customer["customer_id"]
    app.dependency_overrides.clear()


def test_customer_search_scopes_to_actor_tenant():
    client = _client()
    first = _seed_customer(client, tenant_id="tenant-1", first_name="Jane", last_name="Doe")
    second = _seed_customer(client, tenant_id="tenant-2", first_name="John", last_name="Smith")

    listed = client.get("/customers", headers=_headers("AGENT", "tenant-1", "agent"))
    assert listed.status_code == 200
    ids = {customer["customer_id"] for customer in listed.json()}
    assert first["customer_id"] in ids
    assert second["customer_id"] not in ids
    app.dependency_overrides.clear()


def test_customer_cannot_read_cross_tenant_customer():
    client = _client()
    customer = _seed_customer(client, tenant_id="tenant-1")

    denied = client.get(f"/customers/{customer['customer_id']}", headers=_headers("CUSTOMER", "tenant-2", customer["customer_id"]))
    assert denied.status_code == 403
    app.dependency_overrides.clear()
