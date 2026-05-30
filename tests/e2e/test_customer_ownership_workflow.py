from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from claims_service.api import app as claims_app
from claims_service.api import get_repository as get_claims_repository
from claims_service.database import Base as ClaimsBase
from claims_service.repository import ClaimsRepository
from customer_service.api import app as customer_app
from customer_service.database import Base as CustomerBase
from customer_service.database import get_session as get_customer_session
from policy_service.api.app import app as policy_app
from policy_service.api.app import get_repository as get_policy_repository
from policy_service.storage.database import Base as PolicyBase
from policy_service.storage.policy_repository import PolicyRepository
from quote_service.api.app import app as quote_app
from quote_service.api.app import get_quote_repository, init_engine
from quote_service.storage.database import Base as QuoteBase
from quote_service.storage.quote_repository import QuoteRepository


PRODUCT_YAML = "data/sample-products/sample_personal_auto_v1.yml"


def _session(base):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return Session()


def _customer_client():
    session = _session(CustomerBase)

    def override():
        return session

    customer_app.dependency_overrides[get_customer_session] = override
    return TestClient(customer_app)


def _quote_client():
    init_engine(PRODUCT_YAML)
    session = _session(QuoteBase)
    repository = QuoteRepository(session)
    quote_app.dependency_overrides[get_quote_repository] = lambda: repository
    return TestClient(quote_app)


def _policy_client():
    session = _session(PolicyBase)
    repository = PolicyRepository(session)
    policy_app.dependency_overrides[get_policy_repository] = lambda: repository
    return TestClient(policy_app)


def _claims_client():
    session = _session(ClaimsBase)
    repository = ClaimsRepository(session)
    claims_app.dependency_overrides[get_claims_repository] = lambda: repository
    return TestClient(claims_app)


def _headers(role="AGENT", tenant="tenant-1", customer="customer-1"):
    return {"Authorization": f"Bearer dev:test-user:{role}:{tenant}:{customer}"}


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


def _bind_payload(quote):
    now = datetime.utcnow()
    return {
        "quote_id": quote["quote_id"],
        "effective_date": now.isoformat(),
        "expiration_date": (now + timedelta(days=365)).isoformat(),
        "quote_snapshot": quote,
        "risk_assessment_snapshot": {"decision": "ACCEPT"},
        "request_key": f"bind-{quote['quote_id']}",
    }


def _claim_payload(policy_id):
    return {
        "policy_id": policy_id,
        "loss_type": "collision",
        "loss_date": datetime.utcnow().isoformat(),
        "loss_location": "city",
        "description": "workflow test",
        "police_report_indicator": False,
        "injuries_indicator": False,
        "preferred_contact_method": "email",
    }


def test_customer_quote_policy_claim_ownership_workflow():
    customer_client = _customer_client()
    quote_client = _quote_client()
    policy_client = _policy_client()
    claims_client = _claims_client()

    tenant = customer_client.post(
        "/tenants",
        json={"tenant_id": "tenant-1", "name": "Tenant One"},
        headers=_headers("ADMIN", "tenant-1", "admin"),
    )
    assert tenant.status_code == 200

    account = customer_client.post(
        "/accounts",
        json={"tenant_id": "tenant-1", "name": "Household"},
        headers=_headers("ADMIN", "tenant-1", "admin"),
    )
    assert account.status_code == 200

    customer = customer_client.post(
        "/customers",
        json={
            "tenant_id": "tenant-1",
            "account_id": account.json()["account_id"],
            "first_name": "Workflow",
            "last_name": "Customer",
        },
        headers=_headers("AGENT", "tenant-1", "agent"),
    )
    assert customer.status_code == 200
    customer_id = customer.json()["customer_id"]
    owned_headers = _headers("CUSTOMER", "tenant-1", customer_id)
    other_headers = _headers("CUSTOMER", "tenant-1", "other-customer")

    quote = quote_client.post("/quotes", json=_quote_payload(), headers=owned_headers)
    assert quote.status_code == 200
    quote_id = quote.json()["quote_id"]
    assert quote_client.get(f"/quotes/{quote_id}", headers=owned_headers).status_code == 200
    assert quote_client.get(f"/quotes/{quote_id}", headers=other_headers).status_code == 403

    bind = policy_client.post("/bind-requests", json=_bind_payload(quote.json()), headers=_headers("AGENT", "tenant-1", customer_id))
    assert bind.status_code == 200
    bind_id = bind.json()["bind_request_id"]
    assert policy_client.get(f"/bind-requests/{bind_id}", headers=_headers("AGENT", "tenant-1", customer_id)).status_code == 200
    assert policy_client.get(f"/bind-requests/{bind_id}", headers=_headers("AGENT", "tenant-1", "other-customer")).status_code == 403

    approved = policy_client.post(
        f"/bind-requests/{bind_id}/approve",
        json={"approval_status": "approved", "comments": "approved"},
        headers=_headers("UNDERWRITER_L1", "tenant-1", customer_id),
    )
    assert approved.status_code == 200
    policy_id = approved.json()["policy_id"]
    assert policy_client.get(f"/policies/{policy_id}", headers=_headers("AGENT", "tenant-1", customer_id)).status_code == 200
    assert policy_client.get(f"/policies/{policy_id}", headers=_headers("AGENT", "tenant-1", "other-customer")).status_code == 403

    claim = claims_client.post("/claims/fnol", json=_claim_payload(policy_id), headers=owned_headers)
    assert claim.status_code == 200
    claim_id = claim.json()["claim_id"]
    assert claims_client.get(f"/claims/{claim_id}", headers=owned_headers).status_code == 200
    assert claims_client.get(f"/claims/{claim_id}", headers=other_headers).status_code == 403

    customer_app.dependency_overrides.clear()
    quote_app.dependency_overrides.clear()
    policy_app.dependency_overrides.clear()
    claims_app.dependency_overrides.clear()
