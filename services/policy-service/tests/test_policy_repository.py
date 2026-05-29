from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from policy_service.storage.database import Base
from policy_service.storage.orm import ApprovalRecord, BindRequestRecord, PolicyEventRecord, PolicyRecord
from policy_service.storage.policy_repository import PolicyRepository


def _session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return Session()


def test_create_bind_request_creates_pending_approval_and_event():
    session = _session()
    repository = PolicyRepository(session)
    quote_id = uuid4()

    bind_request = repository.create_bind_request(
        quote_id=quote_id,
        effective_date=datetime.utcnow(),
        expiration_date=datetime.utcnow() + timedelta(days=365),
        quote_snapshot={"total_premium": 1200.0},
        risk_assessment_snapshot={"decision": "ACCEPT"},
        actor_id="agent-1",
    )

    assert bind_request.quote_id == str(quote_id)
    assert bind_request.status == "pending_approval"
    assert bind_request.total_premium == 1200.0
    assert session.query(BindRequestRecord).count() == 1
    assert session.query(ApprovalRecord).count() == 1
    assert session.query(PolicyEventRecord).count() == 1


def test_duplicate_bind_request_key_returns_existing_record():
    session = _session()
    repository = PolicyRepository(session)
    quote_id = uuid4()

    first = repository.create_bind_request(
        quote_id=quote_id,
        effective_date=datetime.utcnow(),
        expiration_date=datetime.utcnow() + timedelta(days=365),
        quote_snapshot={"total_premium": 1200.0},
        risk_assessment_snapshot={"decision": "ACCEPT"},
        actor_id="agent-1",
        request_key="bind-quote-1",
    )
    second = repository.create_bind_request(
        quote_id=quote_id,
        effective_date=datetime.utcnow(),
        expiration_date=datetime.utcnow() + timedelta(days=365),
        quote_snapshot={"total_premium": 1200.0},
        risk_assessment_snapshot={"decision": "ACCEPT"},
        actor_id="agent-1",
        request_key="bind-quote-1",
    )

    assert second.bind_request_id == first.bind_request_id
    assert second.policy_id == first.policy_id
    assert session.query(BindRequestRecord).count() == 1
    assert session.query(ApprovalRecord).count() == 1
    assert session.query(PolicyEventRecord).count() == 1


def test_approve_bind_request_creates_active_policy():
    session = _session()
    repository = PolicyRepository(session)
    bind_request = repository.create_bind_request(
        quote_id=uuid4(),
        effective_date=datetime.utcnow(),
        expiration_date=datetime.utcnow() + timedelta(days=365),
        quote_snapshot={"total_premium": 1200.0},
        risk_assessment_snapshot={"decision": "ACCEPT"},
        actor_id="agent-1",
    )

    policy = repository.approve_bind_request(bind_request.bind_request_id, actor_id="uw-1", comments="Approved")
    second_policy = repository.approve_bind_request(bind_request.bind_request_id, actor_id="uw-1", comments="Approved again")

    assert policy is not None
    assert second_policy is not None
    assert policy.policy_id == bind_request.policy_id
    assert second_policy.policy_id == policy.policy_id
    assert policy.state == "active"
    assert session.query(PolicyRecord).count() == 1
    assert session.query(PolicyEventRecord).count() == 3
