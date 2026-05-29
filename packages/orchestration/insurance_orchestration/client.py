"""HTTP orchestration client for quote -> risk -> policy workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import httpx


@dataclass(frozen=True)
class WorkflowResult:
    quote: dict[str, Any]
    risk_assessment: dict[str, Any]
    bind_request: dict[str, Any] | None = None


class InsuranceWorkflowClient:
    """Small orchestration helper for service-to-service workflows.

    This client is intentionally explicit: each step sends/receives snapshots so
    quote, risk, and policy services remain separately auditable.
    """

    def __init__(
        self,
        quote_base_url: str,
        risk_base_url: str,
        policy_base_url: str,
        bearer_token: str,
        timeout: float = 10.0,
    ) -> None:
        self.quote_base_url = quote_base_url.rstrip("/")
        self.risk_base_url = risk_base_url.rstrip("/")
        self.policy_base_url = policy_base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {bearer_token}"}
        self.timeout = timeout

    def quote_and_assess(
        self,
        applicant_data: dict[str, Any],
        portfolio_state: dict[str, Any],
        validity_days: int = 30,
    ) -> WorkflowResult:
        with httpx.Client(timeout=self.timeout) as client:
            quote_response = client.post(
                f"{self.quote_base_url}/quotes",
                headers=self.headers,
                json={"applicant_data": applicant_data, "validity_days": validity_days},
            )
            quote_response.raise_for_status()
            quote = quote_response.json()

            risk_response = client.post(
                f"{self.risk_base_url}/assess",
                headers=self.headers,
                json={
                    "quote_id": quote["quote_id"],
                    "quote_data": quote,
                    "portfolio_state": portfolio_state,
                },
            )
            risk_response.raise_for_status()
            risk_assessment = risk_response.json()

        return WorkflowResult(quote=quote, risk_assessment=risk_assessment)

    def quote_assess_and_create_bind_request(
        self,
        applicant_data: dict[str, Any],
        portfolio_state: dict[str, Any],
        effective_date: datetime | None = None,
        term_days: int = 365,
        request_key: str | None = None,
    ) -> WorkflowResult:
        result = self.quote_and_assess(applicant_data, portfolio_state)
        effective_date = effective_date or datetime.utcnow()
        expiration_date = effective_date + timedelta(days=term_days)
        request_key = request_key or f"bind:{result.quote['quote_id']}"

        with httpx.Client(timeout=self.timeout) as client:
            bind_response = client.post(
                f"{self.policy_base_url}/bind-requests",
                headers={**self.headers, "Idempotency-Key": request_key},
                json={
                    "quote_id": result.quote["quote_id"],
                    "effective_date": effective_date.isoformat(),
                    "expiration_date": expiration_date.isoformat(),
                    "quote_snapshot": result.quote,
                    "risk_assessment_snapshot": result.risk_assessment,
                    "request_key": request_key,
                },
            )
            bind_response.raise_for_status()
            bind_request = bind_response.json()

        return WorkflowResult(
            quote=result.quote,
            risk_assessment=result.risk_assessment,
            bind_request=bind_request,
        )
