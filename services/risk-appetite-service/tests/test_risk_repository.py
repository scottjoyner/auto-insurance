from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from risk_appetite_service.domain.models import RiskAppetitePolicy
from risk_appetite_service.engine.risk_engine import RiskAppetiteEngine
from risk_appetite_service.storage.database import Base
from risk_appetite_service.storage.orm import RiskAssessmentRecord, RiskPolicyApprovalRecord, RiskPolicyVersionRecord
from risk_appetite_service.storage.risk_repository import RiskPolicyLifecycleError, RiskRepository


def _session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return Session()


def _policy(version="1.0"):
    return RiskAppetitePolicy.from_dict(
        {
            "version": version,
            "effective_date": "2026-01-01",
            "categories": {
                "driver_age": {
                    "name": "driver_age",
                    "threshold_pct": 25.0,
                    "warning_pct": 18.0,
                    "action_on_threshold": "REFER",
                }
            },
            "capital_requirements": {"min_capital_ratio": 0.05},
            "reinsurance": {"retention_pct": 30.0, "total_capacity": 50000000.0},
            "decision_matrix": {},
        }
    )


def test_policy_lifecycle_records_approval_actions():
    session = _session()
    repository = RiskRepository(session)

    draft = repository.create_policy_draft(_policy(), actor_id="uw-1")
    submitted = repository.submit_policy(draft.id, actor_id="uw-1")
    approved = repository.approve_policy(draft.id, actor_id="uw-2")
    active = repository.activate_policy(draft.id, actor_id="uw-2")

    assert draft.id == active.id
    assert submitted is not None
    assert approved is not None
    assert active.status == "active"
    assert repository.get_active_policy_record().id == draft.id
    assert session.query(RiskPolicyVersionRecord).count() == 1
    assert session.query(RiskPolicyApprovalRecord).count() == 3


def test_invalid_policy_lifecycle_transitions_raise():
    session = _session()
    repository = RiskRepository(session)
    draft = repository.create_policy_draft(_policy(), actor_id="uw-1")

    with pytest.raises(RiskPolicyLifecycleError):
        repository.approve_policy(draft.id, actor_id="uw-2")

    submitted = repository.submit_policy(draft.id, actor_id="uw-1")
    assert submitted is not None

    with pytest.raises(RiskPolicyLifecycleError):
        repository.activate_policy(draft.id, actor_id="uw-2")


def test_save_assessment_records_policy_version():
    session = _session()
    repository = RiskRepository(session)
    policy = _policy()
    engine = RiskAppetiteEngine(policy)
    quote_id = uuid4()
    assessment = engine.assess(
        quote_id=quote_id,
        quote_data={"age": 35, "claims_3yr": 0, "vehicle_year": 2023, "total_premium": 100.0},
        portfolio_state={"available_capital": 10000000.0, "capital_ratio": 0.15},
    )

    record = repository.save_assessment(
        assessment=assessment,
        policy_version=policy.version,
        quote_data={"total_premium": 100.0},
        portfolio_state={"available_capital": 10000000.0},
        actor_id="agent-1",
    )

    assert record.policy_version == "1.0"
    assert record.quote_id == str(quote_id)
    assert session.query(RiskAssessmentRecord).count() == 1
