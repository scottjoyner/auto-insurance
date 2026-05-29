from datetime import datetime

import httpx

from insurance_orchestration.client import InsuranceWorkflowClient


def test_quote_assess_and_create_bind_request_flow():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append((request.method, str(request.url)))
        if str(request.url).endswith("/quotes"):
            return httpx.Response(
                200,
                json={
                    "quote_id": "quote-1",
                    "status": "QUOTED",
                    "bind_eligible": True,
                    "total_premium": 1200.0,
                },
            )
        if str(request.url).endswith("/assess"):
            return httpx.Response(200, json={"assessment_id": "risk-1", "quote_id": "quote-1", "decision": "ACCEPT"})
        if str(request.url).endswith("/bind-requests"):
            assert request.headers["Idempotency-Key"] == "bind:quote-1"
            return httpx.Response(200, json={"bind_request_id": "bind-1", "quote_id": "quote-1", "policy_id": "policy-1"})
        raise AssertionError(f"Unexpected URL: {request.url}")

    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    class MockClient(httpx.Client):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    httpx.Client = MockClient
    try:
        client = InsuranceWorkflowClient(
            quote_base_url="https://quote.local",
            risk_base_url="https://risk.local",
            policy_base_url="https://policy.local",
            bearer_token="system:orchestrator",
        )
        result = client.quote_assess_and_create_bind_request(
            applicant_data={"age": 35},
            portfolio_state={"available_capital": 1000000},
            effective_date=datetime(2026, 1, 1),
        )
    finally:
        httpx.Client = original_client

    assert result.quote["quote_id"] == "quote-1"
    assert result.risk_assessment["decision"] == "ACCEPT"
    assert result.bind_request["bind_request_id"] == "bind-1"
    assert len(requests) == 3
