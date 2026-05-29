from insurance_documents import render_adverse_action_notice, render_policy_packet


def test_adverse_action_notice_includes_reason_codes():
    notice = render_adverse_action_notice(
        customer_name="Jane Doe",
        quote_id="quote-1",
        jurisdiction="NC",
        reason_codes=["risk_decision_requires_adverse_action_review"],
    )
    assert "quote-1" in notice
    assert "risk_decision_requires_adverse_action_review" in notice
    assert "draft" in notice.lower()


def test_policy_packet_includes_policy_summary():
    packet = render_policy_packet(
        {
            "policy_id": "policy-1",
            "quote_id": "quote-1",
            "total_premium": 1200.0,
            "bind_packet": {"quote_snapshot": {"coverages": {"liability": 500.0}}},
        }
    )
    assert "policy-1" in packet
    assert "liability" in packet
    assert "1200.0" in packet
