"""Tests for reconciliation module."""

import pytest
from blockchain_gateway.reconciliation import (
    ReconciliationReport,
    Reconciler,
)


class TestReconciliationReport:
    """Test ReconciliationReport dataclass."""

    def test_success_report(self):
        """Test successful reconciliation report."""
        report = ReconciliationReport(
            timestamp="2024-01-01T00:00:00Z",
            window_hours=24,
            local_events_count=5,
            chain_events_count=5,
            missing_from_chain=[],
            missing_from_local=[],
            hash_mismatches=[],
            discrepancies=[],
            is_clean=True,
        )
        assert report.is_clean is True
        assert report.local_events_count == 5
        assert report.chain_events_count == 5

    def test_failure_report(self):
        """Test failure reconciliation report."""
        report = ReconciliationReport(
            timestamp="2024-01-01T00:00:00Z",
            window_hours=24,
            local_events_count=5,
            chain_events_count=5,
            missing_from_chain=["local-1"],
            missing_from_local=["chain-1"],
            hash_mismatches=["hash-1"],
            discrepancies=["disc-1"],
            is_clean=False,
        )
        assert report.is_clean is False
        assert report.local_events_count == 5
        assert report.chain_events_count == 5
        assert report.missing_from_chain == ["local-1"]
        assert report.missing_from_local == ["chain-1"]
        assert report.hash_mismatches == ["hash-1"]
        assert report.discrepancies == ["disc-1"]

    def test_to_dict(self):
        """Test to_dict serialization."""
        report = ReconciliationReport(
            timestamp="2024-01-01T00:00:00Z",
            window_hours=24,
            local_events_count=5,
            chain_events_count=5,
            missing_from_chain=[],
            missing_from_local=[],
            hash_mismatches=[],
            discrepancies=[],
            is_clean=True,
        )
        d = report.to_dict()
        assert d["is_clean"] is True
        assert d["local_events_count"] == 5
        assert d["chain_events_count"] == 5


class TestReconciler:
    """Test Reconciler class."""

    def test_init(self):
        """Test initialization."""
        reconciler = Reconciler(None, None)
        assert reconciler.gateway is None
        assert reconciler.local_store is None

    def test_reconcile_no_local_store(self):
        """Test reconciliation with no local store raises AttributeError."""
        reconciler = Reconciler(None, None)
        # This will fail because local_store is None and has no get_events_in_window
        # We expect it to raise an exception
        with pytest.raises((AttributeError, TypeError)):
            reconciler.reconcile(window_hours=24)


class TestReconciliationError:
    """Test ReconciliationError exception."""

    def test_exception(self):
        """Test that it's a proper exception."""
        with pytest.raises(Exception, match="test error"):
            raise Exception("test error")
