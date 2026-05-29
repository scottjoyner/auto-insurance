from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from quote_service.domain.models import Quote, QuoteStatus
from quote_service.storage.database import Base
from quote_service.storage.orm import QuoteRecord
from quote_service.storage.quote_repository import QuoteRepository


def _session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return Session()


def test_save_and_get_quote_round_trip():
    session = _session()
    repository = QuoteRepository(session)
    quote = Quote(
        product_id="sample_personal_auto_v1",
        product_version="1.0",
        jurisdiction="SAMPLE",
        status=QuoteStatus.QUOTED,
        total_premium=250.50,
        coverages={"liability": 120.0, "collision": 130.5},
        reason_codes=[],
        surcharges_applied=["young_driver"],
        discounts_applied=["good_driver"],
        bind_eligible=True,
        expires_at=datetime.utcnow() + timedelta(days=30),
        rating_result_hash="rating-hash",
        input_snapshot_hash="input-hash",
    )
    quote._applicant_data = {"age": 35, "coverage_type": "standard"}

    saved = repository.save(quote, actor_id="tester")
    loaded = repository.get(saved.quote_id)

    assert loaded is not None
    assert loaded.quote_id == quote.quote_id
    assert loaded.total_premium == 250.50
    assert loaded.coverages["liability"] == 120.0
    assert loaded.input_snapshot_hash == "input-hash"
    assert loaded._applicant_data["coverage_type"] == "standard"


def test_list_filters_by_status():
    session = _session()
    repository = QuoteRepository(session)

    quoted = Quote(product_id="p1", product_version="1.0", status=QuoteStatus.QUOTED)
    expired = Quote(product_id="p2", product_version="1.0", status=QuoteStatus.EXPIRED)
    repository.save(quoted)
    repository.save(expired)

    results = repository.list(status=QuoteStatus.QUOTED)
    assert len(results) == 1
    assert results[0].quote_id == quoted.quote_id
