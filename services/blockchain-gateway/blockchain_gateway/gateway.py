"""Core blockchain gateway - wraps PolicyRegistry and AuditEventRegistry contracts."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Any
from uuid import UUID

from web3 import Web3
from web3.types import LogReceipt, TxReceipt

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Contract ABIs (embedded from Hardhat artifacts)
# ---------------------------------------------------------------------------

_POLICY_REGISTRY_ABI = [
    {"type": "event", "name": "PolicyCommitted", "inputs": [
        {"name": "policyId", "type": "bytes32", "indexed": True},
        {"name": "commitmentHash", "type": "bytes32", "indexed": False},
        {"name": "status", "type": "uint8", "indexed": False},
        {"name": "committedAt", "type": "uint256", "indexed": False},
        {"name": "committedBy", "type": "address", "indexed": False},
    ]},
    {"type": "event", "name": "PolicyStatusUpdated", "inputs": [
        {"name": "policyId", "type": "bytes32", "indexed": True},
        {"name": "newStatus", "type": "uint8", "indexed": False},
        {"name": "updatedAt", "type": "uint256", "indexed": False},
        {"name": "updatedBy", "type": "address", "indexed": False},
    ]},
    {"type": "function", "name": "commitPolicy", "inputs": [
        {"name": "policyId", "type": "bytes32"},
        {"name": "commitmentHash", "type": "bytes32"},
        {"name": "status", "type": "uint8"},
    ], "outputs": [{"type": "uint256"}], "stateMutability": "nonpayable"},
    {"type": "function", "name": "updatePolicyStatus", "inputs": [
        {"name": "policyId", "type": "bytes32"},
        {"name": "newStatus", "type": "uint8"},
    ], "outputs": [], "stateMutability": "nonpayable"},
    {"type": "function", "name": "getPolicy", "inputs": [
        {"name": "policyId", "type": "bytes32"},
    ], "outputs": [{"type": "tuple", "components": [
        {"name": "policyId", "type": "bytes32"},
        {"name": "commitmentHash", "type": "bytes32"},
        {"name": "status", "type": "uint8"},
        {"name": "committedAt", "type": "uint256"},
        {"name": "committedBy", "type": "address"},
    ]}], "stateMutability": "view"},
    {"type": "function", "name": "getCommitmentHash", "inputs": [
        {"name": "policyId", "type": "bytes32"},
    ], "outputs": [{"type": "bytes32"}], "stateMutability": "view"},
    {"type": "function", "name": "getCommittedAt", "inputs": [
        {"name": "policyId", "type": "bytes32"},
    ], "outputs": [{"type": "uint256"}], "stateMutability": "view"},
    {"type": "function", "name": "getPolicyByIndex", "inputs": [
        {"name": "index", "type": "uint256"},
    ], "outputs": [{"type": "bytes32"}], "stateMutability": "view"},
    {"type": "function", "name": "getPolicyCount", "inputs": [], "outputs": [
        {"type": "uint256"}
    ], "stateMutability": "view"},
    {"type": "function", "name": "policyExists", "inputs": [
        {"name": "policyId", "type": "bytes32"},
    ], "outputs": [{"type": "bool"}], "stateMutability": "view"},
    {"type": "function", "name": "getPolicyStatus", "inputs": [
        {"name": "policyId", "type": "bytes32"},
    ], "outputs": [{"type": "uint8"}], "stateMutability": "view"},
]

_AUDIT_EVENT_REGISTRY_ABI = [
    {"type": "event", "name": "AuditEventRecorded", "inputs": [
        {"name": "eventType", "type": "bytes32", "indexed": True},
        {"name": "policyId", "type": "bytes32", "indexed": True},
        {"name": "commitmentHash", "type": "bytes32", "indexed": False},
        {"name": "committedAt", "type": "uint256", "indexed": False},
        {"name": "committedBy", "type": "address", "indexed": False},
    ]},
    {"type": "function", "name": "recordEvent", "inputs": [
        {"name": "eventTypeHash", "type": "bytes32"},
        {"name": "policyIdHash", "type": "bytes32"},
        {"name": "commitmentHash", "type": "bytes32"},
    ], "outputs": [{"type": "uint256"}], "stateMutability": "nonpayable"},
    {"type": "function", "name": "getEvent", "inputs": [
        {"name": "index", "type": "uint256"},
    ], "outputs": [{"type": "tuple", "components": [
        {"name": "eventType", "type": "bytes32"},
        {"name": "policyId", "type": "bytes32"},
        {"name": "commitmentHash", "type": "bytes32"},
        {"name": "committedAt", "type": "uint256"},
        {"name": "committedBy", "type": "address"},
    ]}], "stateMutability": "view"},
    {"type": "function", "name": "getEventCount", "inputs": [], "outputs": [
        {"type": "uint256"}
    ], "stateMutability": "view"},
    {"type": "function", "name": "getPolicyEvents", "inputs": [
        {"name": "policyIdHash", "type": "bytes32"},
    ], "outputs": [{"type": "uint256[]"}], "stateMutability": "view"},
    {"type": "function", "name": "getEventsByType", "inputs": [
        {"name": "eventTypeHash", "type": "bytes32"},
    ], "outputs": [{"type": "uint256[]"}], "stateMutability": "view"},
]


# ---------------------------------------------------------------------------
# Enums and dataclasses
# ---------------------------------------------------------------------------

class PolicyStatus(IntEnum):
    """On-chain policy status (matches Solidity enum)."""
    PENDING = 0
    ACTIVE = 1
    ENDORSEMENT = 2
    CANCELLED = 3
    EXPIRED = 4


class AuditEventType(IntEnum):
    """On-chain event type (matches Solidity enum)."""
    BIND = 0
    ENDORSEMENT = 1
    CANCELLATION = 2
    RENEWAL = 3
    CLAIM_FILING = 4
    CLAIM_SETTLEMENT = 5


@dataclass
class PolicyRecord:
    """A policy record from the on-chain registry."""
    policy_id: str  # hex bytes32
    commitment_hash: str  # hex bytes32
    status: PolicyStatus
    committed_at: int  # unix timestamp
    committed_by: str  # hex address

    @classmethod
    def from_tuple(cls, data: tuple) -> "PolicyRecord":
        return cls(
            policy_id=Web3.to_hex(data[0]),
            commitment_hash=Web3.to_hex(data[1]),
            status=PolicyStatus(int(data[2])),
            committed_at=int(data[3]),
            committed_by=Web3.to_checksum_address(data[4]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "commitment_hash": self.commitment_hash,
            "status": self.status.name,
            "committed_at": self.committed_at,
            "committed_by": self.committed_by,
        }


@dataclass
class AuditEventRecord:
    """An audit event record from the on-chain registry."""
    event_type: str  # event type name
    policy_id: str  # hex bytes32
    commitment_hash: str  # hex bytes32
    committed_at: int  # unix timestamp
    committed_by: str  # hex address

    @classmethod
    def from_tuple(cls, data: tuple) -> "AuditEventRecord":
        # data layout from Solidity struct:
        # [0]=eventType(bytes32), [1]=policyId(bytes32),
        # [2]=commitmentHash(bytes32), [3]=committedAt(uint256),
        # [4]=committedBy(address)
        return cls(
            event_type=Web3.to_hex(data[0]),
            policy_id=Web3.to_hex(data[1]),
            commitment_hash=Web3.to_hex(data[2]),
            committed_at=int(data[3]),
            committed_by=Web3.to_checksum_address(data[4]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "policy_id": self.policy_id,
            "commitment_hash": self.commitment_hash,
            "committed_at": self.committed_at,
            "committed_by": self.committed_by,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def hash_policy_id(policy_id: str | UUID) -> bytes:
    """Hash a policy ID string to bytes32 (SHA-256, truncated)."""
    if isinstance(policy_id, UUID):
        policy_id = str(policy_id)
    h = hashlib.sha256(policy_id.encode()).digest()
    return h[:32]


def hash_event_type(event_type: AuditEventType | str) -> bytes:
    """Hash an event type string to bytes32 (SHA-256, truncated)."""
    if isinstance(event_type, AuditEventType):
        event_type = event_type.name
    h = hashlib.sha256(event_type.encode()).digest()
    return h[:32]


def hash_commitment_hash(commitment_hash: str) -> bytes:
    """Convert a hex commitment hash string to bytes."""
    if isinstance(commitment_hash, str):
        if commitment_hash.startswith("0x"):
            return bytes.fromhex(commitment_hash[2:])
        return bytes.fromhex(commitment_hash)
    return commitment_hash


# ---------------------------------------------------------------------------
# Gateway
# ---------------------------------------------------------------------------

class BlockchainGateway:
    """Core gateway that wraps PolicyRegistry and AuditEventRegistry contracts."""

    def __init__(
        self,
        rpc_url: str,
        policy_registry_address: str,
        audit_event_registry_address: str,
        signer_address: str | None = None,
        signer_private_key: str | None = None,
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.signer_address = signer_address
        self.signer_private_key = signer_private_key

        # PolicyRegistry
        self._policy_registry = self.w3.eth.contract(
            address=Web3.to_checksum_address(policy_registry_address),
            abi=_POLICY_REGISTRY_ABI,
        )
        # AuditEventRegistry
        self._audit_event_registry = self.w3.eth.contract(
            address=Web3.to_checksum_address(audit_event_registry_address),
            abi=_AUDIT_EVENT_REGISTRY_ABI,
        )

        logger.info(
            "Gateway initialized: rpc=%s policy=%s events=%s signer=%s",
            rpc_url,
            policy_registry_address,
            audit_event_registry_address,
            signer_address,
        )

    # ---- Policy operations ----

    def commit_policy(
        self,
        policy_id: str | UUID,
        commitment_hash: str,
        status: PolicyStatus,
    ) -> str:
        """Commit a new policy to the registry. Returns tx hash."""
        policy_id_bytes = hash_policy_id(policy_id)
        commitment_bytes = hash_commitment_hash(commitment_hash)
        status_int = int(status)

        tx = self._policy_registry.functions.commitPolicy(
            policy_id_bytes, commitment_bytes, status_int
        ).build_transaction({
            "from": self.signer_address,
            "nonce": self.w3.eth.get_transaction_count(self.signer_address),
            "gas": 500000,
            "gasPrice": self.w3.eth.gas_price,
        })

        signed = self.w3.eth.account.sign_transaction(tx, self.signer_private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status != 1:
            raise BlockchainGatewayError(
                f"commit_policy failed: tx {tx_hash.hex()} reverted"
            )

        logger.info("Policy committed: %s tx=%s", policy_id, tx_hash.hex())
        return tx_hash.hex()

    def update_policy_status(
        self,
        policy_id: str | UUID,
        new_status: PolicyStatus,
    ) -> str:
        """Update the status of an existing policy. Returns tx hash."""
        policy_id_bytes = hash_policy_id(policy_id)
        status_int = int(new_status)

        tx = self._policy_registry.functions.updatePolicyStatus(
            policy_id_bytes, status_int
        ).build_transaction({
            "from": self.signer_address,
            "nonce": self.w3.eth.get_transaction_count(self.signer_address),
            "gas": 300000,
            "gasPrice": self.w3.eth.gas_price,
        })

        signed = self.w3.eth.account.sign_transaction(tx, self.signer_private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status != 1:
            raise BlockchainGatewayError(
                f"update_policy_status failed: tx {tx_hash.hex()} reverted"
            )

        logger.info("Policy status updated: %s -> %s tx=%s", policy_id, new_status.name, tx_hash.hex())
        return tx_hash.hex()

    def get_policy(self, policy_id: str | UUID) -> PolicyRecord:
        """Get a policy record by ID."""
        policy_id_bytes = hash_policy_id(policy_id)
        data = self._policy_registry.functions.getPolicy(policy_id_bytes).call()
        return PolicyRecord.from_tuple(data)

    def get_policy_status(self, policy_id: str | UUID) -> PolicyStatus:
        """Get the status of a policy."""
        policy_id_bytes = hash_policy_id(policy_id)
        status_int = self._policy_registry.functions.getPolicyStatus(policy_id_bytes).call()
        return PolicyStatus(status_int)

    def get_commitment_hash(self, policy_id: str | UUID) -> str:
        """Get the commitment hash of a policy."""
        policy_id_bytes = hash_policy_id(policy_id)
        h = self._policy_registry.functions.getCommitmentHash(policy_id_bytes).call()
        return Web3.to_hex(h)

    def get_committed_at(self, policy_id: str | UUID) -> int:
        """Get the committed timestamp of a policy."""
        policy_id_bytes = hash_policy_id(policy_id)
        return self._policy_registry.functions.getCommittedAt(policy_id_bytes).call()

    def policy_exists(self, policy_id: str | UUID) -> bool:
        """Check if a policy has been committed."""
        policy_id_bytes = hash_policy_id(policy_id)
        return self._policy_registry.functions.policyExists(policy_id_bytes).call()

    def get_policy_count(self) -> int:
        """Get total number of committed policies."""
        return self._policy_registry.functions.getPolicyCount().call()

    def get_policy_by_index(self, index: int) -> str:
        """Get a policy ID by index (hex bytes32)."""
        h = self._policy_registry.functions.getPolicyByIndex(index).call()
        return Web3.to_hex(h)

    # ---- Audit event operations ----

    def record_event(
        self,
        event_type: AuditEventType | str,
        policy_id: str | UUID,
        commitment_hash: str,
    ) -> str:
        """Record an audit event. Returns tx hash."""
        event_type_bytes = hash_event_type(event_type)
        policy_id_bytes = hash_policy_id(policy_id)
        commitment_bytes = hash_commitment_hash(commitment_hash)

        tx = self._audit_event_registry.functions.recordEvent(
            event_type_bytes, policy_id_bytes, commitment_bytes
        ).build_transaction({
            "from": self.signer_address,
            "nonce": self.w3.eth.get_transaction_count(self.signer_address),
            "gas": 500000,
            "gasPrice": self.w3.eth.gas_price,
        })

        signed = self.w3.eth.account.sign_transaction(tx, self.signer_private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status != 1:
            raise BlockchainGatewayError(
                f"record_event failed: tx {tx_hash.hex()} reverted"
            )

        logger.info("Event recorded: %s for %s tx=%s", event_type, policy_id, tx_hash.hex())
        return tx_hash.hex()

    def get_event(self, index: int) -> tuple:
        """Get an audit event by index. Returns raw (eventType, policyId, commitmentHash, committedAt, committedBy)."""
        return self._audit_event_registry.functions.getEvent(index).call()

    def get_event_count(self) -> int:
        """Get total number of audit events."""
        return self._audit_event_registry.functions.getEventCount().call()

    def get_policy_events(self, policy_id: str | UUID) -> list[int]:
        """Get event indices for a policy."""
        policy_id_bytes = hash_policy_id(policy_id)
        return self._audit_event_registry.functions.getPolicyEvents(policy_id_bytes).call()

    def get_events_by_type(self, event_type: AuditEventType | str) -> list[int]:
        """Get event indices by event type."""
        event_type_bytes = hash_event_type(event_type)
        return self._audit_event_registry.functions.getEventsByType(event_type_bytes).call()

    # ---- Event log queries ----

    def get_policy_committed_events(
        self,
        from_block: int = 0,
        to_block: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query PolicyCommitted events."""
        if to_block is None:
            to_block = self.w3.eth.block_number
        logs = self._policy_registry.events.PolicyCommitted().get_logs(
            fromBlock=from_block, toBlock=to_block
        )
        return [
            {
                "block_number": log["blockNumber"],
                "tx_hash": log["transactionHash"].hex(),
                "policy_id": Web3.to_hex(log["args"]["policyId"]),
                "commitment_hash": Web3.to_hex(log["args"]["commitmentHash"]),
                "status": PolicyStatus(log["args"]["status"]).name,
                "committed_at": log["args"]["committedAt"],
                "committed_by": Web3.to_checksum_address(log["args"]["committedBy"]),
            }
            for log in logs
        ]

    def get_event_recorded_events(
        self,
        from_block: int = 0,
        to_block: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query AuditEventRecorded events."""
        if to_block is None:
            to_block = self.w3.eth.block_number
        logs = self._audit_event_registry.events.AuditEventRecorded().get_logs(
            fromBlock=from_block, toBlock=to_block
        )
        return [
            {
                "block_number": log["blockNumber"],
                "tx_hash": log["transactionHash"].hex(),
                "event_type": Web3.to_hex(log["args"]["eventType"]),
                "policy_id": Web3.to_hex(log["args"]["policyId"]),
                "commitment_hash": Web3.to_hex(log["args"]["commitmentHash"]),
                "committed_at": log["args"]["committedAt"],
                "committed_by": Web3.to_checksum_address(log["args"]["committedBy"]),
            }
            for log in logs
        ]

    # ---- Health ----

    def is_connected(self) -> bool:
        """Check if the gateway is connected to the RPC."""
        try:
            return self.w3.is_connected()
        except Exception:
            return False

    def get_chain_id(self) -> int:
        """Get the current chain ID."""
        return self.w3.eth.chain_id


class BlockchainGatewayError(Exception):
    """Raised when a blockchain operation fails."""
    pass
