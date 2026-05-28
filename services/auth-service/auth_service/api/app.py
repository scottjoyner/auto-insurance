from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Any

import jwt
from eth_account.messages import encode_defunct
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from web3 import Web3

from auth_service.config.settings import settings

app = FastAPI(title="Auth Service", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory nonce cache for login flows.
_nonce_store: dict[str, str] = {}


class NonceResponse(BaseModel):
    address: str
    nonce: str


class VerifyRequest(BaseModel):
    address: str
    signature: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    address: str
    expires_at: str


def _generate_nonce() -> str:
    return secrets.token_urlsafe(16)


@app.get("/auth/nonce", response_model=NonceResponse)
def get_nonce(address: str = Query(..., description="Ethereum address to authenticate")):
    normalized = Web3.to_checksum_address(address)
    nonce = _generate_nonce()
    _nonce_store[normalized] = nonce
    return NonceResponse(address=normalized, nonce=nonce)


@app.post("/auth/verify", response_model=TokenResponse)
def verify_signature(req: VerifyRequest):
    try:
        normalized = Web3.to_checksum_address(req.address)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid address: {exc}")

    nonce = _nonce_store.get(normalized)
    if not nonce:
        raise HTTPException(status_code=400, detail="Nonce not found or expired")

    message = encode_defunct(text=nonce)
    try:
        recovered = Web3().eth.account.recover_message(message, signature=req.signature)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Signature verification failed: {exc}")

    if Web3.to_checksum_address(recovered) != normalized:
        raise HTTPException(status_code=403, detail="Signature does not match address")

    token = jwt.encode(
        {
            "sub": normalized,
            "iss": settings.issuer,
            "exp": datetime.utcnow() + timedelta(minutes=settings.token_expiry_minutes),
        },
        settings.auth_service_secret_key,
        algorithm="HS256",
    )
    return TokenResponse(access_token=token)


def _decode_token(auth_header: str | None) -> dict[str, Any]:
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    token = auth_header.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(
            token,
            settings.auth_service_secret_key,
            algorithms=["HS256"],
            issuer=settings.issuer,
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")


@app.get("/auth/me", response_model=MeResponse)
def me(authorization: str | None = Header(None)):
    payload = _decode_token(authorization)
    return MeResponse(address=payload["sub"], expires_at=datetime.utcfromtimestamp(payload["exp"]).isoformat())
