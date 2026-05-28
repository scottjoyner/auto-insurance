"""Tests for the blockchain gateway service."""

import json
from unittest.mock import MagicMock, patch
import pytest
from blockchain_gateway.gateway import (
    BlockchainGateway,
    BlockchainGatewayError,
    PolicyRecord,
    AuditEventRecord,
    PolicyStatus,
    AuditEventType,
    hash_policy_id,
    hash_event_type,
    hash_commitment_hash,
)


class TestHashHelpers:
    """Test hash helper functions."""

    def test_hash_policy_id_string(self):
        """Test hashing a policy ID string."""
        result = hash_policy_id("test-policy-123")
        assert len(result) == 32  # bytes32

    def test_hash_policy_id_uuid(self):
        """Test hashing a UUID policy ID."""
        import uuid
        policy_uuid = uuid.uuid4()
        result = hash_policy_id(policy_uuid)
        assert len(result) == 32

    def test_hash_policy_id_deterministic(self):
        """Test that same input produces same output."""
        r1 = hash_policy_id("same-policy")
        r2 = hash_policy_id("same-policy")
        assert r1 == r2

    def test_hash_event_type_string(self):
        """Test hashing an event type string."""
        result = hash_event_type("BIND")
        assert len(result) == 32

    def test_hash_event_type_enum(self):
        """Test hashing an AuditEventType enum."""
        result = hash_event_type(AuditEventType.BIND)
        assert len(result) == 32

    def test_hash_event_type_deterministic(self):
        """Test that same input produces same output."""
        r1 = hash_event_type("BIND")
        r2 = hash_event_type("BIND")
        assert r1 == r2

    def test_hash_commitment_hash_with_0x_prefix(self):
        """Test hashing a commitment hash with 0x prefix."""
        result = hash_commitment_hash("0x1234567890abcdef")
        assert result == bytes.fromhex("1234567890abcdef")

    def test_hash_commitment_hash_without_0x_prefix(self):
        """Test hashing a commitment hash without 0x prefix."""
        result = hash_commitment_hash("1234567890abcdef")
        assert result == bytes.fromhex("1234567890abcdef")


class TestPolicyRecord:
    """Test PolicyRecord dataclass."""

    def test_from_tuple(self):
        """Test creating a PolicyRecord from a tuple."""
        data = (
            b'\x01' * 32,   # policyId bytes32
            b'\x02' * 32,   # commitmentHash bytes32
            1,               # status (ACTIVE)
            1704067200,      # committedAt
            b'\x03' * 20,   # committedBy address
        )
        record = PolicyRecord.from_tuple(data)
        assert record.policy_id == "0x" + "01" * 32
        assert record.commitment_hash == "0x" + "02" * 32
        assert record.status == PolicyStatus.ACTIVE
        assert record.committed_at == 1704067200

    def test_to_dict(self):
        """Test serializing a PolicyRecord to dict."""
        record = PolicyRecord(
            policy_id="0x01" * 32,
            commitment_hash="0x02" * 32,
            status=PolicyStatus.ACTIVE,
            committed_at=1704067200,
            committed_by="0x03" * 20,
        )
        d = record.to_dict()
        assert d["policy_id"] == "0x01" * 32
        assert d["status"] == "ACTIVE"
        assert d["committed_at"] == 1704067200


class TestAuditEventRecord:
    """Test AuditEventRecord dataclass."""

    def test_from_tuple(self):
        """Test creating an AuditEventRecord from a tuple."""
        data = (
            b'\x01' * 32,   # eventType bytes32
            b'\x02' * 32,   # policyId bytes32
            b'\x03' * 32,   # commitmentHash bytes32
            1704067200,      # committedAt
            b'\x04' * 20,   # committedBy address
        )
        record = AuditEventRecord.from_tuple(data)
        assert record.event_type == "0x" + "01" * 32
        assert record.policy_id == "0x" + "02" * 32
        assert record.committed_at == 1704067200

    def test_to_dict(self):
        """Test serializing an AuditEventRecord to dict."""
        record = AuditEventRecord(
            event_type="0x01" * 32,
            policy_id="0x02" * 32,
            commitment_hash="0x03" * 32,
            committed_at=1704067200,
            committed_by="0x04" * 20,
        )
        d = record.to_dict()
        assert d["event_type"] == "0x01" * 32
        assert d["committed_at"] == 1704067200


class TestPolicyStatus:
    """Test PolicyStatus enum."""

    def test_values(self):
        """Test PolicyStatus enum values."""
        assert PolicyStatus.PENDING == 0
        assert PolicyStatus.ACTIVE == 1
        assert PolicyStatus.ENDORSEMENT == 2
        assert PolicyStatus.CANCELLED == 3
        assert PolicyStatus.EXPIRED == 4

    def test_from_int(self):
        """Test creating PolicyStatus from int."""
        assert PolicyStatus(0) == PolicyStatus.PENDING
        assert PolicyStatus(1) == PolicyStatus.ACTIVE
        assert PolicyStatus(4) == PolicyStatus.EXPIRED


class TestAuditEventType:
    """Test AuditEventType enum."""

    def test_values(self):
        """Test AuditEventType enum values."""
        assert AuditEventType.BIND == 0
        assert AuditEventType.ENDORSEMENT == 1
        assert AuditEventType.CANCELLATION == 2
        assert AuditEventType.RENEWAL == 3
        assert AuditEventType.CLAIM_FILING == 4
        assert AuditEventType.CLAIM_SETTLEMENT == 5


class TestBlockchainGateway:
    """Test BlockchainGateway class."""

    @pytest.fixture
    def mock_w3(self, monkeypatch):
        """Create a mock Web3 instance."""
        mock_w3 = MagicMock()
        mock_w3.eth = MagicMock()
        mock_w3.eth.block_number = 1000
        mock_w3.eth.chain_id = 1337
        mock_w3.eth.gas_price = 20000000000
        mock_w3.eth.get_transaction_count = MagicMock(return_value=0)
        mock_w3.eth.send_raw_transaction = MagicMock(
            return_value=MagicMock(hex=MagicMock(return_value="0xtx123"))
        )
        mock_receipt = MagicMock()
        mock_receipt.status = 1
        mock_w3.eth.wait_for_transaction_receipt = MagicMock(
            return_value=mock_receipt
        )
        mock_contract = MagicMock()
        mock_w3.eth.contract = MagicMock(return_value=mock_contract)
        mock_w3.to_checksum_address = MagicMock(side_effect=lambda x: "0x" + x.hex() if isinstance(x, bytes) else x)
        mock_w3.is_connected = MagicMock(return_value=True)
        mock_w3.to_hex = MagicMock(side_effect=lambda x: "0x" + x.hex() if isinstance(x, bytes) else "0x" + x)
        # Patch Web3 methods at the class level to handle bytes properly
        monkeypatch.setattr("blockchain_gateway.gateway.Web3.to_hex", mock_w3.to_hex)
        monkeypatch.setattr("blockchain_gateway.gateway.Web3.to_checksum_address", mock_w3.to_checksum_address)
        # Return both mock_w3 and mock_contract for tests to configure
        return mock_w3, mock_contract

    @pytest.fixture
    def gateway(self, mock_w3):
        """Create a gateway with mocked web3."""
        mock_w3, mock_contract = mock_w3
        mock_contract.functions.commitPolicy = MagicMock()
        mock_contract.functions.updatePolicyStatus = MagicMock()
        mock_contract.functions.recordEvent = MagicMock()

        with patch("blockchain_gateway.gateway.Web3") as MockWeb3:
            MockWeb3.return_value = mock_w3

            gateway = BlockchainGateway(
                rpc_url="http://localhost:8545",
                policy_registry_address="0xPolicyRegistry",
                audit_event_registry_address="0xAuditEventRegistry",
                signer_address="0xSigner",
                signer_private_key="0x0123456789abcdef",
            )
            return gateway

    def test_init(self, mock_w3):
        """Test gateway initialization."""
        mock_w3, mock_contract = mock_w3
        with patch("blockchain_gateway.gateway.Web3") as MockWeb3:
            MockWeb3.return_value = mock_w3

            gateway = BlockchainGateway(
                rpc_url="http://localhost:8545",
                policy_registry_address="0xPolicyRegistry",
                audit_event_registry_address="0xAuditEventRegistry",
                signer_address="0xSigner",
                signer_private_key="0x0123456789abcdef",
            )
            assert gateway.signer_address == "0xSigner"
            assert gateway.signer_private_key == "0x0123456789abcdef"

    def test_commit_policy(self, gateway, mock_w3):
        """Test committing a policy."""
        mock_w3, mock_contract = mock_w3
        mock_func = MagicMock()
        mock_func.build_transaction = MagicMock(return_value={"gas": 500000})
        mock_contract.functions.commitPolicy = mock_func

        mock_w3.eth.account = MagicMock()
        mock_w3.eth.account.sign_transaction = MagicMock(
            return_value=MagicMock(raw_transaction="0xsigned")
        )

        tx_hash = gateway.commit_policy(
            policy_id="test-policy-123",
            commitment_hash="0xabc123",
            status=PolicyStatus.ACTIVE,
        )
        assert tx_hash == "0xtx123"

    def test_commit_policy_reverts(self, gateway, mock_w3):
        """Test commit_policy when transaction reverts."""
        mock_w3, mock_contract = mock_w3
        mock_func = MagicMock()
        mock_func.build_transaction = MagicMock(return_value={"gas": 500000})
        mock_contract.functions.commitPolicy = mock_func

        mock_w3.eth.account = MagicMock()
        mock_w3.eth.account.sign_transaction = MagicMock(
            return_value=MagicMock(raw_transaction="0xsigned")
        )
        mock_w3.eth.wait_for_transaction_receipt = MagicMock(
            return_value=MagicMock(status=0)  # Reverted
        )

        with pytest.raises(BlockchainGatewayError, match="commit_policy failed"):
            gateway.commit_policy(
                policy_id="test-policy-123",
                commitment_hash="0xabc123",
                status=PolicyStatus.ACTIVE,
            )

    def test_update_policy_status(self, gateway, mock_w3):
        """Test updating policy status."""
        mock_w3, mock_contract = mock_w3
        mock_func = MagicMock()
        mock_func.build_transaction = MagicMock(return_value={"gas": 300000})
        mock_contract.functions.updatePolicyStatus = mock_func

        mock_w3.eth.account = MagicMock()
        mock_w3.eth.account.sign_transaction = MagicMock(
            return_value=MagicMock(raw_transaction="0xsigned")
        )

        tx_hash = gateway.update_policy_status(
            policy_id="test-policy-123",
            new_status=PolicyStatus.CANCELLED,
        )
        assert tx_hash == "0xtx123"

    def test_get_policy(self, gateway, mock_w3):
        """Test getting a policy record."""
        mock_w3, mock_contract = mock_w3
        mock_func = MagicMock()
        mock_func.call.return_value = (
            b'\x01' * 32,   # policyId
            b'\x02' * 32,   # commitmentHash
            1,               # status
            1704067200,      # committedAt
            b'\x03' * 20,   # committedBy
        )
        mock_contract.functions.getPolicy.return_value = mock_func

        record = gateway.get_policy("test-policy-123")
        assert isinstance(record, PolicyRecord)
        assert record.status == PolicyStatus.ACTIVE

    def test_get_policy_status(self, gateway, mock_w3):
        """Test getting policy status."""
        mock_w3, mock_contract = mock_w3
        mock_contract.functions.getPolicyStatus.return_value.call.return_value = 1

        status = gateway.get_policy_status("test-policy-123")
        assert status == PolicyStatus.ACTIVE

    def test_get_commitment_hash(self, gateway, mock_w3):
        """Test getting commitment hash."""
        mock_w3, mock_contract = mock_w3
        mock_contract.functions.getCommitmentHash.return_value.call.return_value = b'\x01' * 32

        h = gateway.get_commitment_hash("test-policy-123")
        assert h == "0x" + "01" * 32

    def test_get_committed_at(self, gateway, mock_w3):
        """Test getting committed timestamp."""
        mock_w3, mock_contract = mock_w3
        mock_contract.functions.getCommittedAt.return_value.call.return_value = 1704067200

        ts = gateway.get_committed_at("test-policy-123")
        assert ts == 1704067200

    def test_policy_exists(self, gateway, mock_w3):
        """Test checking if policy exists."""
        mock_w3, mock_contract = mock_w3
        mock_contract.functions.policyExists.return_value.call.return_value = True

        assert gateway.policy_exists("test-policy-123") is True

    def test_get_policy_count(self, gateway, mock_w3):
        """Test getting policy count."""
        mock_w3, mock_contract = mock_w3
        mock_contract.functions.getPolicyCount.return_value.call.return_value = 10

        count = gateway.get_policy_count()
        assert count == 10

    def test_get_policy_by_index(self, gateway, mock_w3):
        """Test getting policy by index."""
        mock_w3, mock_contract = mock_w3
        mock_contract.functions.getPolicyByIndex.return_value.call.return_value = b'\x01' * 32

        policy_id = gateway.get_policy_by_index(0)
        assert policy_id == "0x" + "01" * 32

    def test_record_event(self, gateway, mock_w3):
        """Test recording an audit event."""
        mock_contract = MagicMock()
        mock_w3, mock_contract = mock_w3
        mock_func = MagicMock()
        mock_func.build_transaction = MagicMock(return_value={"gas": 500000})
        mock_contract.functions.recordEvent = mock_func

        mock_w3.eth.account = MagicMock()
        mock_w3.eth.account.sign_transaction = MagicMock(
            return_value=MagicMock(raw_transaction="0xsigned")
        )

        tx_hash = gateway.record_event(
            event_type=AuditEventType.BIND,
            policy_id="test-policy-123",
            commitment_hash="0xabc123",
        )
        assert tx_hash == "0xtx123"

    def test_record_event_string_type(self, gateway, mock_w3):
        """Test recording an event with string event type."""
        mock_w3, mock_contract = mock_w3
        mock_func = MagicMock()
        mock_func.build_transaction = MagicMock(return_value={"gas": 500000})
        mock_contract.functions.recordEvent = mock_func

        mock_w3.eth.account = MagicMock()
        mock_w3.eth.account.sign_transaction = MagicMock(
            return_value=MagicMock(raw_transaction="0xsigned")
        )

        tx_hash = gateway.record_event(
            event_type="BIND",
            policy_id="test-policy-123",
            commitment_hash="0xabc123",
        )
        assert tx_hash == "0xtx123"

    def test_record_event_reverts(self, gateway, mock_w3):
        """Test record_event when transaction reverts."""
        mock_w3, mock_contract = mock_w3
        mock_func = MagicMock()
        mock_func.build_transaction = MagicMock(return_value={"gas": 500000})
        mock_contract.functions.recordEvent = mock_func

        mock_w3.eth.account = MagicMock()
        mock_w3.eth.account.sign_transaction = MagicMock(
            return_value=MagicMock(raw_transaction="0xsigned")
        )
        mock_w3.eth.wait_for_transaction_receipt = MagicMock(
            return_value=MagicMock(status=0)
        )

        with pytest.raises(BlockchainGatewayError, match="record_event failed"):
            gateway.record_event(
                event_type=AuditEventType.BIND,
                policy_id="test-policy-123",
                commitment_hash="0xabc123",
            )

    def test_get_event(self, gateway, mock_w3):
        """Test getting an event by index."""
        mock_w3, mock_contract = mock_w3
        mock_contract.functions.getEvent.return_value.call.return_value = (
            b'\x01' * 32,
            b'\x02' * 32,
            b'\x03' * 32,
            1704067200,
            b'\x04' * 20,
        )

        event = gateway.get_event(0)
        assert isinstance(event, tuple)
        assert len(event) == 5

    def test_get_event_count(self, gateway, mock_w3):
        """Test getting event count."""
        mock_w3, mock_contract = mock_w3
        mock_contract.functions.getEventCount.return_value.call.return_value = 5

        count = gateway.get_event_count()
        assert count == 5

    def test_get_policy_events(self, gateway, mock_w3):
        """Test getting events for a policy."""
        mock_w3, mock_contract = mock_w3
        mock_contract.functions.getPolicyEvents.return_value.call.return_value = [0, 1, 2]

        events = gateway.get_policy_events("test-policy-123")
        assert events == [0, 1, 2]

    def test_get_events_by_type(self, gateway, mock_w3):
        """Test getting events by type."""
        mock_w3, mock_contract = mock_w3
        mock_contract.functions.getEventsByType.return_value.call.return_value = [0, 1]

        mock_w3.eth.contract.return_value = mock_contract

        events = gateway.get_events_by_type(AuditEventType.BIND)
        assert events == [0, 1]

    def test_is_connected(self, gateway, mock_w3):
        """Test checking connection."""
        assert gateway.is_connected() is True

    def test_get_chain_id(self, gateway, mock_w3):
        """Test getting chain ID."""
        assert gateway.get_chain_id() == 1337
