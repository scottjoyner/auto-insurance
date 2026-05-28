"""Tests for the outbox store."""

import json
import pytest
from blockchain_gateway.outbox import (
    OutboxEntry,
    OutboxStore,
    OutboxStatus,
)


class TestOutboxEntry:
    """Test OutboxEntry dataclass."""

    def test_defaults(self):
        """Test default values."""
        entry = OutboxEntry(
            id="test-1",
            event_type="COMMIT_POLICY",
            payload=json.dumps({"policy_id": "0x123"}),
            contract="policy_registry",
            method="commitPolicy",
            status=OutboxStatus.PENDING,
            tx_hash=None,
            retry_count=0,
            last_error=None,
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
        )
        assert entry.id == "test-1"
        assert entry.event_type == "COMMIT_POLICY"
        assert entry.status == "pending"
        assert entry.tx_hash is None
        assert entry.retry_count == 0
        assert entry.last_error is None
        assert entry.next_retry_at is None

    def test_to_dict(self):
        """Test serializing entry to dict."""
        entry = OutboxEntry(
            id="test-1",
            event_type="COMMIT_POLICY",
            payload=json.dumps({"policy_id": "0x123"}),
            contract="policy_registry",
            method="commitPolicy",
            status=OutboxStatus.PENDING,
            tx_hash=None,
            retry_count=0,
            last_error=None,
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
        )
        d = entry.to_dict()
        assert d["id"] == "test-1"
        assert d["event_type"] == "COMMIT_POLICY"
        assert d["contract"] == "policy_registry"
        assert d["status"] == "pending"

    def test_from_dict(self):
        """Test deserializing entry from dict."""
        d = {
            "id": "test-1",
            "event_type": "COMMIT_POLICY",
            "payload": json.dumps({"policy_id": "0x123"}),
            "contract": "policy_registry",
            "method": "commitPolicy",
            "status": "pending",
            "tx_hash": None,
            "retry_count": 0,
            "last_error": None,
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-01T00:00:00+00:00",
            "next_retry_at": None,
        }
        entry = OutboxEntry.from_dict(d)
        assert entry.id == "test-1"
        assert entry.event_type == "COMMIT_POLICY"

    def test_from_row(self):
        """Test deserializing entry from DB row."""
        row = (
            "test-1", "COMMIT_POLICY", json.dumps({"policy_id": "0x123"}),
            "policy_registry", "commitPolicy", "pending",
            None, 0, None,
            "2024-01-01T00:00:00+00:00", "2024-01-01T00:00:00+00:00",
            None,
        )
        entry = OutboxEntry.from_row(row)
        assert entry.id == "test-1"
        assert entry.event_type == "COMMIT_POLICY"
        assert json.loads(entry.payload) == {"policy_id": "0x123"}


class TestOutboxStore:
    """Test OutboxStore class."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create a temporary outbox store."""
        db_path = tmp_path / "test_outbox.db"
        return OutboxStore(str(db_path))

    def test_insert_entry(self, store):
        """Test inserting an entry."""
        entry = OutboxEntry(
            id="test-1",
            event_type="COMMIT_POLICY",
            payload=json.dumps({"policy_id": "0x123"}),
            contract="policy_registry",
            method="commitPolicy",
            status=OutboxStatus.PENDING,
            tx_hash=None,
            retry_count=0,
            last_error=None,
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
        )
        result_id = store.insert(entry)
        assert result_id == "test-1"
        retrieved = store.get_entry("test-1")
        assert retrieved is not None
        assert retrieved.id == "test-1"

    def test_insert_duplicate_entry(self, store):
        """Test inserting a duplicate entry (IGNORE)."""
        entry = OutboxEntry(
            id="test-1",
            event_type="COMMIT_POLICY",
            payload=json.dumps({"policy_id": "0x123"}),
            contract="policy_registry",
            method="commitPolicy",
            status=OutboxStatus.PENDING,
            tx_hash=None,
            retry_count=0,
            last_error=None,
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
        )
        store.insert(entry)
        store.insert(entry)  # Should be IGNOREd
        assert store.get_pending_count() == 1

    def test_get_entry(self, store):
        """Test retrieving an entry by ID."""
        entry = OutboxEntry(
            id="test-1",
            event_type="COMMIT_POLICY",
            payload=json.dumps({"policy_id": "0x123"}),
            contract="policy_registry",
            method="commitPolicy",
            status=OutboxStatus.PENDING,
            tx_hash=None,
            retry_count=0,
            last_error=None,
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
        )
        store.insert(entry)
        retrieved = store.get_entry("test-1")
        assert retrieved is not None
        assert retrieved.id == "test-1"

    def test_get_entry_not_found(self, store):
        """Test retrieving a non-existent entry."""
        assert store.get_entry("nonexistent") is None

    def test_mark_submitted(self, store):
        """Test marking an entry as submitted."""
        entry = OutboxEntry(
            id="test-1",
            event_type="COMMIT_POLICY",
            payload=json.dumps({"policy_id": "0x123"}),
            contract="policy_registry",
            method="commitPolicy",
            status=OutboxStatus.PENDING,
            tx_hash=None,
            retry_count=0,
            last_error=None,
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
        )
        store.insert(entry)
        store.mark_submitted("test-1", "0xtx123")
        updated = store.get_entry("test-1")
        assert updated.status == "submitted"
        assert updated.tx_hash == "0xtx123"

    def test_mark_committed(self, store):
        """Test marking an entry as committed."""
        entry = OutboxEntry(
            id="test-1",
            event_type="COMMIT_POLICY",
            payload=json.dumps({"policy_id": "0x123"}),
            contract="policy_registry",
            method="commitPolicy",
            status=OutboxStatus.SUBMITTED,
            tx_hash="0xtx123",
            retry_count=0,
            last_error=None,
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
        )
        store.insert(entry)
        store.mark_committed("test-1")
        updated = store.get_entry("test-1")
        assert updated.status == "committed"

    def test_mark_failed(self, store):
        """Test marking an entry as failed."""
        entry = OutboxEntry(
            id="test-1",
            event_type="COMMIT_POLICY",
            payload=json.dumps({"policy_id": "0x123"}),
            contract="policy_registry",
            method="commitPolicy",
            status=OutboxStatus.PENDING,
            tx_hash=None,
            retry_count=0,
            last_error=None,
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
        )
        store.insert(entry)
        store.mark_failed("test-1", "connection error")
        updated = store.get_entry("test-1")
        assert updated.status == "failed"
        assert updated.last_error == "connection error"
        assert updated.retry_count == 1
        assert updated.next_retry_at is not None

    def test_get_pending_entries(self, store):
        """Test getting pending entries."""
        for i in range(3):
            entry = OutboxEntry(
                id=f"p{i}",
                event_type="COMMIT_POLICY",
                payload=json.dumps({"policy_id": f"0x{i}"}),
                contract="policy_registry",
                method="commitPolicy",
                status=OutboxStatus.PENDING,
                tx_hash=None,
                retry_count=0,
                last_error=None,
                created_at="2024-01-01T00:00:00+00:00",
                updated_at="2024-01-01T00:00:00+00:00",
            )
            store.insert(entry)

        pending = store.get_pending_entries()
        assert len(pending) == 3

    def test_get_pending_entries_respects_limit(self, store):
        """Test that get_pending_entries respects the limit parameter."""
        for i in range(5):
            entry = OutboxEntry(
                id=f"p{i}",
                event_type="COMMIT_POLICY",
                payload=json.dumps({"policy_id": f"0x{i}"}),
                contract="policy_registry",
                method="commitPolicy",
                status=OutboxStatus.PENDING,
                tx_hash=None,
                retry_count=0,
                last_error=None,
                created_at="2024-01-01T00:00:00+00:00",
                updated_at="2024-01-01T00:00:00+00:00",
            )
            store.insert(entry)

        pending = store.get_pending_entries(limit=3)
        assert len(pending) == 3

    def test_get_pending_count(self, store):
        """Test getting pending count."""
        for i in range(3):
            entry = OutboxEntry(
                id=f"p{i}",
                event_type="COMMIT_POLICY",
                payload=json.dumps({"policy_id": f"0x{i}"}),
                contract="policy_registry",
                method="commitPolicy",
                status=OutboxStatus.PENDING,
                tx_hash=None,
                retry_count=0,
                last_error=None,
                created_at="2024-01-01T00:00:00+00:00",
                updated_at="2024-01-01T00:00:00+00:00",
            )
            store.insert(entry)

        assert store.get_pending_count() == 3

    def test_get_stats(self, store):
        """Test getting outbox stats."""
        # Add entries in different statuses
        for i in range(2):
            entry = OutboxEntry(
                id=f"p{i}",
                event_type="COMMIT_POLICY",
                payload=json.dumps({"policy_id": f"0x{i}"}),
                contract="policy_registry",
                method="commitPolicy",
                status=OutboxStatus.PENDING,
                tx_hash=None,
                retry_count=0,
                last_error=None,
                created_at="2024-01-01T00:00:00+00:00",
                updated_at="2024-01-01T00:00:00+00:00",
            )
            store.insert(entry)

        entry = OutboxEntry(
            id="s1",
            event_type="COMMIT_POLICY",
            payload=json.dumps({"policy_id": "0x100"}),
            contract="policy_registry",
            method="commitPolicy",
            status=OutboxStatus.SUBMITTED,
            tx_hash="0xtx1",
            retry_count=0,
            last_error=None,
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
        )
        store.insert(entry)

        stats = store.get_stats()
        assert stats["pending"] == 2
        assert stats["submitted"] == 1
        assert stats["committed"] == 0
        assert stats["failed"] == 0

    def test_get_events_in_window(self, store):
        """Test getting events in a time window."""
        entry = OutboxEntry(
            id="test-1",
            event_type="COMMIT_POLICY",
            payload=json.dumps({
                "event_type": "BIND",
                "commitment_hash": "0xabc123",
                "policy_id": "0x123",
            }),
            contract="policy_registry",
            method="commitPolicy",
            status=OutboxStatus.PENDING,
            tx_hash=None,
            retry_count=0,
            last_error=None,
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
        )
        store.insert(entry)

        from datetime import datetime, timezone
        start = datetime(2023, 12, 31, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, tzinfo=timezone.utc)

        events = store.get_events_in_window(start, end)
        assert len(events) == 1
        assert events[0]["id"] == "test-1"
        assert events[0]["event_type"] == "BIND"
        assert events[0]["commitment_hash"] == "0xabc123"
        assert events[0]["committed_by"] == "local"

    def test_events_in_window_excludes_committed(self, store):
        """Test that get_events_in_window excludes committed entries."""
        entry = OutboxEntry(
            id="committed-1",
            event_type="COMMIT_POLICY",
            payload=json.dumps({}),
            contract="policy_registry",
            method="commitPolicy",
            status=OutboxStatus.COMMITTED,
            tx_hash="0xtx1",
            retry_count=0,
            last_error=None,
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
        )
        store.insert(entry)

        from datetime import datetime, timezone
        start = datetime(2023, 12, 31, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, tzinfo=timezone.utc)

        events = store.get_events_in_window(start, end)
        assert len(events) == 0
