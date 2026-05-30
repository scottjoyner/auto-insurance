from types import SimpleNamespace

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jwt import PyJWKClientError

from insurance_security.fastapi import ActorContext, Role, require_roles


app = FastAPI()


@app.get("/protected")
def protected(actor: ActorContext = Depends(require_roles(Role.AGENT))):
    return {
        "actor_id": actor.actor_id,
        "roles": sorted(actor.roles),
        "tenant_id": actor.tenant_id,
        "customer_id": actor.customer_id,
        "token_type": actor.raw_token_type,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


client = TestClient(app)


def _jwt(claims, secret="test-secret"):
    return jwt.encode(claims, secret, algorithm="HS256")


def _rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


class FakeJWKClient:
    def __init__(self, public_key):
        self.public_key = public_key

    def get_signing_key_from_jwt(self, token):
        return SimpleNamespace(key=self.public_key)


class FailingJWKClient:
    def __init__(self, *args, **kwargs):
        pass

    def get_signing_key_from_jwt(self, token):
        raise PyJWKClientError("unknown kid")


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
    response = client.get("/protected", headers={"Authorization": "Bearer dev:user-1:AGENT:tenant-1:customer-1"})
    assert response.status_code == 200
    body = response.json()
    assert body["actor_id"] == "user-1"
    assert body["tenant_id"] == "tenant-1"
    assert body["customer_id"] == "customer-1"


def test_system_role_passes_as_privileged():
    response = client.get("/protected", headers={"Authorization": "Bearer system:svc-risk"})
    assert response.status_code == 200


def test_jwt_auth_mode_validates_signed_token(monkeypatch):
    monkeypatch.setenv("INSURANCE_AUTH_MODE", "jwt")
    monkeypatch.setenv("INSURANCE_JWT_HS256_SECRET", "test-secret")
    monkeypatch.setenv("INSURANCE_JWT_ISSUER", "auto-insurance-test")
    monkeypatch.setenv("INSURANCE_JWT_AUDIENCE", "auto-insurance-api")
    token = _jwt(
        {
            "sub": "agent-1",
            "roles": ["AGENT"],
            "tenant_id": "tenant-1",
            "customer_id": "customer-1",
            "iss": "auto-insurance-test",
            "aud": "auto-insurance-api",
        }
    )
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["actor_id"] == "agent-1"
    assert body["token_type"] == "jwt"
    assert body["tenant_id"] == "tenant-1"


def test_jwt_auth_mode_maps_external_group_claim(monkeypatch):
    monkeypatch.setenv("INSURANCE_AUTH_MODE", "jwt")
    monkeypatch.setenv("INSURANCE_JWT_HS256_SECRET", "test-secret")
    monkeypatch.setenv("INSURANCE_JWT_ISSUER", "auto-insurance-test")
    monkeypatch.setenv("INSURANCE_JWT_AUDIENCE", "auto-insurance-api")
    monkeypatch.setenv("INSURANCE_JWT_ROLES_CLAIM", "groups")
    monkeypatch.setenv("INSURANCE_JWT_ROLE_MAP", '{"insurance-agents":"AGENT"}')
    token = _jwt(
        {
            "sub": "agent-1",
            "groups": ["insurance-agents"],
            "tenant_id": "tenant-1",
            "customer_id": "customer-1",
            "iss": "auto-insurance-test",
            "aud": "auto-insurance-api",
        }
    )
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["roles"] == ["AGENT"]


def test_jwt_auth_mode_rejects_unmapped_external_group(monkeypatch):
    monkeypatch.setenv("INSURANCE_AUTH_MODE", "jwt")
    monkeypatch.setenv("INSURANCE_JWT_HS256_SECRET", "test-secret")
    monkeypatch.setenv("INSURANCE_JWT_ISSUER", "auto-insurance-test")
    monkeypatch.setenv("INSURANCE_JWT_AUDIENCE", "auto-insurance-api")
    monkeypatch.setenv("INSURANCE_JWT_ROLES_CLAIM", "groups")
    token = _jwt(
        {
            "sub": "agent-1",
            "groups": ["insurance-agents"],
            "iss": "auto-insurance-test",
            "aud": "auto-insurance-api",
        }
    )
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_jwt_auth_mode_rejects_bad_signature(monkeypatch):
    monkeypatch.setenv("INSURANCE_AUTH_MODE", "jwt")
    monkeypatch.setenv("INSURANCE_JWT_HS256_SECRET", "test-secret")
    token = _jwt({"sub": "agent-1", "roles": ["AGENT"]}, secret="wrong-secret")
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_jwt_auth_mode_rejects_wrong_issuer(monkeypatch):
    monkeypatch.setenv("INSURANCE_AUTH_MODE", "jwt")
    monkeypatch.setenv("INSURANCE_JWT_HS256_SECRET", "test-secret")
    monkeypatch.setenv("INSURANCE_JWT_ISSUER", "expected-issuer")
    token = _jwt({"sub": "agent-1", "roles": ["AGENT"], "iss": "wrong-issuer"})
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_jwt_auth_mode_rejects_wrong_audience(monkeypatch):
    monkeypatch.setenv("INSURANCE_AUTH_MODE", "jwt")
    monkeypatch.setenv("INSURANCE_JWT_HS256_SECRET", "test-secret")
    monkeypatch.setenv("INSURANCE_JWT_AUDIENCE", "expected-audience")
    token = _jwt({"sub": "agent-1", "roles": ["AGENT"], "aud": "wrong-audience"})
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_jwt_auth_mode_rejects_missing_roles(monkeypatch):
    monkeypatch.setenv("INSURANCE_AUTH_MODE", "jwt")
    monkeypatch.setenv("INSURANCE_JWT_HS256_SECRET", "test-secret")
    token = _jwt({"sub": "agent-1"})
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_jwt_mode_rejects_dev_token_when_dev_tokens_disabled(monkeypatch):
    monkeypatch.setenv("INSURANCE_AUTH_MODE", "jwt")
    monkeypatch.setenv("INSURANCE_ALLOW_DEV_TOKENS", "false")
    monkeypatch.setenv("INSURANCE_JWT_HS256_SECRET", "test-secret")
    response = client.get("/protected", headers={"Authorization": "Bearer dev:user-1:AGENT"})
    assert response.status_code == 401


def test_rs256_jwks_auth_mode_validates_signed_token(monkeypatch):
    private_key, public_key = _rsa_keypair()
    monkeypatch.setenv("INSURANCE_AUTH_MODE", "jwt")
    monkeypatch.setenv("INSURANCE_JWT_ALGORITHM", "RS256")
    monkeypatch.setenv("INSURANCE_JWT_JWKS_URL", "https://idp.example.test/.well-known/jwks.json")
    monkeypatch.setenv("INSURANCE_JWT_ISSUER", "https://idp.example.test/")
    monkeypatch.setenv("INSURANCE_JWT_AUDIENCE", "auto-insurance-api")
    monkeypatch.setattr("insurance_security.jwt.PyJWKClient", lambda url: FakeJWKClient(public_key))
    token = jwt.encode(
        {
            "sub": "agent-1",
            "roles": ["AGENT"],
            "tenant_id": "tenant-1",
            "customer_id": "customer-1",
            "iss": "https://idp.example.test/",
            "aud": "auto-insurance-api",
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )

    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["actor_id"] == "agent-1"
    assert body["token_type"] == "jwt"
    assert body["tenant_id"] == "tenant-1"
    assert body["customer_id"] == "customer-1"


def test_rs256_jwks_auth_mode_rejects_unknown_kid(monkeypatch):
    private_key, _ = _rsa_keypair()
    monkeypatch.setenv("INSURANCE_AUTH_MODE", "jwt")
    monkeypatch.setenv("INSURANCE_JWT_ALGORITHM", "RS256")
    monkeypatch.setenv("INSURANCE_JWT_JWKS_URL", "https://idp.example.test/.well-known/jwks.json")
    monkeypatch.setenv("INSURANCE_JWT_ISSUER", "https://idp.example.test/")
    monkeypatch.setenv("INSURANCE_JWT_AUDIENCE", "auto-insurance-api")
    monkeypatch.setattr("insurance_security.jwt.PyJWKClient", lambda url: FailingJWKClient())
    token = jwt.encode(
        {
            "sub": "agent-1",
            "roles": ["AGENT"],
            "iss": "https://idp.example.test/",
            "aud": "auto-insurance-api",
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "unknown-key"},
    )

    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
