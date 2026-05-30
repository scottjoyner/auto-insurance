import httpx
import pytest
from fastapi import HTTPException

from insurance_security.fastapi import ActorContext, Role
from quote_service.integrations.customer_validation import validate_actor_customer


class DummyResponse:
    def __init__(self, status_code, body=None):
        self.status_code = status_code
        self._body = body or {}

    def json(self):
        return self._body


def _actor(role=Role.CUSTOMER, tenant_id="tenant-1", customer_id="customer-1"):
    return ActorContext(
        actor_id="actor-1",
        roles=frozenset({role}),
        tenant_id=tenant_id,
        customer_id=customer_id,
    )


def test_validate_actor_customer_accepts_matching_customer(monkeypatch):
    def fake_get(url, headers, timeout):
        return DummyResponse(200, {"tenant_id": "tenant-1", "customer_id": "customer-1"})

    monkeypatch.setattr(httpx, "get", fake_get)

    validate_actor_customer(
        actor=_actor(),
        customer_service_url="http://customer-service:8005",
        bearer_token="token",
    )


def test_validate_actor_customer_rejects_missing_customer_id():
    with pytest.raises(HTTPException) as exc:
        validate_actor_customer(
            actor=_actor(customer_id=None),
            customer_service_url="http://customer-service:8005",
            bearer_token="token",
        )
    assert exc.value.status_code == 400


def test_validate_actor_customer_rejects_not_found(monkeypatch):
    def fake_get(url, headers, timeout):
        return DummyResponse(404)

    monkeypatch.setattr(httpx, "get", fake_get)

    with pytest.raises(HTTPException) as exc:
        validate_actor_customer(
            actor=_actor(),
            customer_service_url="http://customer-service:8005",
            bearer_token="token",
        )
    assert exc.value.status_code == 404


def test_validate_actor_customer_rejects_ownership_mismatch(monkeypatch):
    def fake_get(url, headers, timeout):
        return DummyResponse(200, {"tenant_id": "tenant-2", "customer_id": "customer-1"})

    monkeypatch.setattr(httpx, "get", fake_get)

    with pytest.raises(HTTPException) as exc:
        validate_actor_customer(
            actor=_actor(),
            customer_service_url="http://customer-service:8005",
            bearer_token="token",
        )
    assert exc.value.status_code == 403


def test_validate_actor_customer_fails_closed_when_service_unavailable(monkeypatch):
    def fake_get(url, headers, timeout):
        raise httpx.ConnectError("unavailable")

    monkeypatch.setattr(httpx, "get", fake_get)

    with pytest.raises(HTTPException) as exc:
        validate_actor_customer(
            actor=_actor(),
            customer_service_url="http://customer-service:8005",
            bearer_token="token",
        )
    assert exc.value.status_code == 503
