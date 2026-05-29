import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from insurance_security.fastapi import ActorContext, Role, require_roles


app = FastAPI()


@app.get("/protected")
def protected(actor: ActorContext = Depends(require_roles(Role.AGENT))):
    return {"actor_id": actor.actor_id, "roles": sorted(actor.roles)}


@app.get("/health")
def health():
    return {"status": "healthy"}


client = TestClient(app)


def test_health_is_public():
    response = client.get("/health")
    assert response.status_code == 200


def test_missing_token_is_rejected():
    response = client.get("/protected")
    assert response.status_code == 401


def test_wrong_role_is_forbidden():
    response = client.get("/protected", headers={"Authorization": "Bearer dev:user-1:CUSTOMER"})
    assert response.status_code == 403


def test_allowed_role_passes():
    response = client.get("/protected", headers={"Authorization": "Bearer dev:user-1:AGENT"})
    assert response.status_code == 200
    assert response.json()["actor_id"] == "user-1"


def test_system_role_passes_as_privileged():
    response = client.get("/protected", headers={"Authorization": "Bearer system:svc-risk"})
    assert response.status_code == 200
