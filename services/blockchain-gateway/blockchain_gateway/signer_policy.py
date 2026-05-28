"""Signer policy enforcement for blockchain operations.

Controls which addresses can:
- Commit policies (must be in signer whitelist)
- Update policy status (must have UPDATE role)
- Record audit events (must be in event recorder whitelist)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class PolicyAction(str, Enum):
    COMMIT_POLICY = "commit_policy"
    UPDATE_STATUS = "update_status"
    RECORD_EVENT = "record_event"


@dataclass
class SignerPolicy:
    """Signer policy configuration."""
    # Addresses allowed to commit policies
    policy_commiters: list[str] = field(default_factory=list)

    # Addresses allowed to update policy status
    status_updaters: list[str] = field(default_factory=list)

    # Addresses allowed to record audit events
    event_recorders: list[str] = field(default_factory=list)

    # Default: allow all when no config loaded (dev-friendly)
    allow_all: bool = True

    def is_policy_committer(self, address: str) -> bool:
        """Check if an address can commit policies."""
        if self.allow_all:
            return True
        return address in self.policy_commiters

    def is_status_updater(self, address: str) -> bool:
        """Check if an address can update policy status."""
        if self.allow_all:
            return True
        return address in self.status_updaters

    def is_event_recorder(self, address: str) -> bool:
        """Check if an address can record audit events."""
        if self.allow_all:
            return True
        return address in self.event_recorders

    def can_perform_action(self, address: str, action: PolicyAction) -> bool:
        """Check if an address can perform a specific action."""
        if self.allow_all:
            return True
        if action == PolicyAction.COMMIT_POLICY:
            return self.is_policy_committer(address)
        elif action == PolicyAction.UPDATE_STATUS:
            return self.is_status_updater(address)
        elif action == PolicyAction.RECORD_EVENT:
            return self.is_event_recorder(address)
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_commiters": self.policy_commiters,
            "status_updaters": self.status_updaters,
            "event_recorders": self.event_recorders,
            "allow_all": self.allow_all,
        }


class SignerPolicyError(Exception):
    """Raised when a signer is not authorized."""
    pass


class SignerPolicyManager:
    """Manages signer policy configuration."""

    def __init__(self):
        self._policy = SignerPolicy()

    @property
    def policy(self) -> SignerPolicy:
        return self._policy

    def load_from_dict(self, config: dict[str, Any]) -> None:
        """Load policy from a dict."""
        self._policy = SignerPolicy(
            policy_commiters=config.get("policy_commiters", []),
            status_updaters=config.get("status_updaters", []),
            event_recorders=config.get("event_recorders", []),
            allow_all=config.get("allow_all", False),
        )
        logger.info("Signer policy loaded: %s", self._policy.to_dict())

    def load_from_yaml(self, path: str) -> None:
        """Load policy from a YAML file."""
        try:
            import yaml
            with open(path, "r") as f:
                config = yaml.safe_load(f)
            self.load_from_dict(config)
        except FileNotFoundError:
            logger.warning("Signer policy file not found: %s (using defaults)", path)
            self._policy = SignerPolicy()

    def enforce(self, address: str, action: PolicyAction) -> None:
        """Enforce signer policy. Raises SignerPolicyError if not authorized."""
        if not self._policy.can_perform_action(address, action):
            raise SignerPolicyError(
                f"Signer {address} is not authorized to perform {action.value}"
            )

    def is_enforced(self, address: str, action: PolicyAction) -> bool:
        """Check if signer is authorized without raising."""
        return self._policy.can_perform_action(address, action)

    def add_policy_committer(self, address: str) -> None:
        """Add an address to the policy committers list."""
        if address not in self._policy.policy_commiters:
            self._policy.policy_commiters.append(address)
            logger.info("Added policy committer: %s", address)

    def add_status_updater(self, address: str) -> None:
        """Add an address to the status updaters list."""
        if address not in self._policy.status_updaters:
            self._policy.status_updaters.append(address)
            logger.info("Added status updater: %s", address)

    def add_event_recorder(self, address: str) -> None:
        """Add an address to the event recorders list."""
        if address not in self._policy.event_recorders:
            self._policy.event_recorders.append(address)
            logger.info("Added event recorder: %s", address)
