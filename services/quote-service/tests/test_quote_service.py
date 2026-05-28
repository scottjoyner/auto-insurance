"""Tests for the Quote Service."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from quote_service.domain.models import (
    Quote,
    QuoteInputSnapshot,
    QuoteRecalculationRequest,
    QuoteStatus,
    ReferralFlag,
)
from quote_service.engine.explainability import QuoteExplainability
from quote_service.engine.expiration_handler import QuoteExpirationHandler
from quote_service.storage.quote_store import store


# ---------------------------------------------------------------------------
# Domain model tests
# ---------------------------------------------------------------------------


class TestQuoteInputSnapshot:
    def test_create(self):
        snapshot = QuoteInputSnapshot.create(
            applicant_data={"age": 35, "vehicle_year": 2023},
            product_id="test_auto_v1",
            product_version="1.0",
            jurisdiction="SAMPLE",
            input_hash="abc123",
        )
        assert snapshot.product_id == "test_auto_v1"
        assert snapshot.product_version == "1.0"
        assert snapshot.jurisdiction == "SAMPLE"
        assert snapshot.input_hash == "abc123"
        assert isinstance(snapshot.captured_at, datetime)

    def test_frozen(self):
        snapshot = QuoteInputSnapshot.create(
            applicant_data={"age": 35},
            product_id="test",
            product_version="1.0",
            jurisdiction="SAMPLE",
            input_hash="abc",
        )
        with pytest.raises(Exception):
            object.__setattr__(snapshot, "product_id", "other")


class TestQuote:
    def test_default_state(self):
        q = Quote(product_id="test", product_version="1.0")
        assert q.status == QuoteStatus.DRAFT
        assert q.total_premium == 0.0
        assert q.bind_eligible is False
        assert q.referral_flag == ReferralFlag.NONE

    def test_mark_quoted(self):
        q = Quote(product_id="test", product_version="1.0")
        q.mark_quoted()
        assert q.status == QuoteStatus.QUOTED

    def test_mark_expired(self):
        q = Quote(product_id="test", product_version="1.0")
        q.mark_expired()
        assert q.status == QuoteStatus.EXPIRED

    def test_to_dict(self):
        q = Quote(
            product_id="test_auto_v1",
            product_version="1.0",
            jurisdiction="SAMPLE",
            total_premium=150.0,
            coverages={"liability": 80.0, "collision": 50.0, "comprehensive": 20.0},
            reason_codes=[],
            surcharges_applied=["young_driver"],
            discounts_applied=["clean_driver"],
            bind_eligible=True,
        )
        d = q.to_dict()
        assert d["product_id"] == "test_auto_v1"
        assert d["total_premium"] == 150.0
        assert d["bind_eligible"] is True
        assert "quote_id" in d
        assert "expires_at" in d
        assert "created_at" in d

    def test_is_expired_future(self):
        q = Quote(
            product_id="test",
            product_version="1.0",
            expires_at=datetime.utcnow() + timedelta(days=1),
        )
        assert q.is_expired() is False

    def test_is_expired_past(self):
        q = Quote(
            product_id="test",
            product_version="1.0",
            expires_at=datetime.utcnow() - timedelta(days=1),
        )
        assert q.is_expired() is True


# ---------------------------------------------------------------------------
# Explainability tests
# ---------------------------------------------------------------------------


class TestQuoteExplainability:
    def test_explain_dict(self):
        q = Quote(
            product_id="test_auto_v1",
            product_version="1.0",
            jurisdiction="SAMPLE",
            total_premium=150.0,
            coverages={"liability": 80.0, "collision": 50.0, "comprehensive": 20.0},
            surcharges_applied=["young_driver"],
            discounts_applied=["clean_driver"],
            reason_codes=[],
            bind_eligible=True,
        )
        report = QuoteExplainability.explain(q)
        assert report["quote_id"] == str(q.quote_id)
        assert report["summary"]["total_premium"] == 150.0
        assert report["summary"]["num_coverages"] == 3
        assert report["premium_breakdown"]["coverages"] == q.coverages
        assert report["eligibility"]["eligible"] is True

    def test_explain_text(self):
        q = Quote(
            product_id="test_auto_v1",
            product_version="1.0",
            total_premium=150.0,
            coverages={"liability": 80.0, "collision": 50.0, "comprehensive": 20.0},
            surcharges_applied=["young_driver"],
            discounts_applied=["clean_driver"],
            reason_codes=["age_factor"],
            bind_eligible=False,
            referral_flag=ReferralFlag.UNDERWRITER_REFERRAL,
            referral_reason="Age factor requires review",
        )
        text = QuoteExplainability.explain_text(q)
        assert "Quote:" in text
        assert "$150.00" in text
        assert "liability" in text.lower()
        assert "Bind Eligible: No" in text
        assert "UNDERWRITER_REFERRAL" in text

    def test_referral_none(self):
        q = Quote(
            product_id="test",
            product_version="1.0",
            referral_flag=ReferralFlag.NONE,
        )
        report = QuoteExplainability.explain(q)
        assert report["referral"]["referral_required"] is False


# ---------------------------------------------------------------------------
# Expiration handler tests
# ---------------------------------------------------------------------------


class TestQuoteExpirationHandler:
    def setup_method(self):
        self.handler = QuoteExpirationHandler()
        # Clear store
        store._quotes.clear()

    def test_check_and_expire_nothing_expired(self):
        q = Quote(
            product_id="test",
            product_version="1.0",
            expires_at=datetime.utcnow() + timedelta(days=1),
        )
        store.save(q)
        count = self.handler.check_and_expire()
        assert count == 0
        assert store.get(q.quote_id).status == QuoteStatus.QUOTED

    def test_check_and_expire_with_expired(self):
        q = Quote(
            product_id="test",
            product_version="1.0",
            expires_at=datetime.utcnow() - timedelta(days=1),
        )
        store.save(q)
        count = self.handler.check_and_expire()
        assert count == 1
        assert store.get(q.quote_id).status == QuoteStatus.EXPIRED

    def test_extend_quote(self):
        q = Quote(
            product_id="test",
            product_version="1.0",
            expires_at=datetime.utcnow() + timedelta(days=1),
        )
        store.save(q)
        new_date = datetime.utcnow() + timedelta(days=60)
        result = self.handler.extend_quote(q.quote_id, new_date)
        assert result is True
        assert store.get(q.quote_id).expires_at == new_date

    def test_extend_expired_quote_fails(self):
        q = Quote(
            product_id="test",
            product_version="1.0",
            expires_at=datetime.utcnow() - timedelta(days=1),
        )
        store.save(q)
        result = self.handler.extend_quote(q.quote_id)
        assert result is False

    def test_get_active_quotes(self):
        active = Quote(
            product_id="test",
            product_version="1.0",
            expires_at=datetime.utcnow() + timedelta(days=1),
        )
        expired = Quote(
            product_id="test2",
            product_version="1.0",
            expires_at=datetime.utcnow() - timedelta(days=1),
        )
        store.save(active)
        store.save(expired)
        active_quotes = self.handler.get_active_quotes()
        assert len(active_quotes) == 1
        assert active_quotes[0].quote_id == active.quote_id

    def test_get_quote_details(self):
        q = Quote(
            product_id="test",
            product_version="1.0",
            total_premium=150.0,
            expires_at=datetime.utcnow() + timedelta(days=30),
            coverages={"liability": 80.0},
            bind_eligible=True,
        )
        store.save(q)
        details = self.handler.get_quote_details(q.quote_id)
        assert details is not None
        assert details["total_premium"] == 150.0
        assert details["is_expired"] is False
        assert details["bind_eligible"] is True

    def test_get_quote_details_not_found(self):
        details = self.handler.get_quote_details(uuid4())
        assert details is None


# ---------------------------------------------------------------------------
# Quote store tests
# ---------------------------------------------------------------------------


class TestQuoteStore:
    def setup_method(self):
        store._quotes.clear()

    def test_save_and_get(self):
        q = Quote(product_id="test", product_version="1.0")
        store.save(q)
        retrieved = store.get(q.quote_id)
        assert retrieved is not None
        assert retrieved.quote_id == q.quote_id

    def test_delete(self):
        q = Quote(product_id="test", product_version="1.0")
        store.save(q)
        result = store.delete(q.quote_id)
        assert result is True
        assert store.get(q.quote_id) is None

    def test_delete_nonexistent(self):
        result = store.delete(uuid4())
        assert result is False

    def test_count(self):
        assert store.count() == 0
        q1 = Quote(product_id="test1", product_version="1.0")
        q2 = Quote(product_id="test2", product_version="1.0")
        store.save(q1)
        store.save(q2)
        assert store.count() == 2

    def test_get_all_with_filter(self):
        q1 = Quote(product_id="test1", product_version="1.0")
        q1.mark_quoted()
        q2 = Quote(product_id="test2", product_version="1.0")
        q2.mark_expired()
        store.save(q1)
        store.save(q2)
        quoted = store.get_all(QuoteStatus.QUOTED)
        assert len(quoted) == 1
        assert quoted[0].quote_id == q1.quote_id

    def test_update(self):
        q = Quote(product_id="test", product_version="1.0")
        q.mark_quoted()
        store.save(q)
        q.mark_expired()
        store.update(q)
        assert store.get(q.quote_id).status == QuoteStatus.EXPIRED
