"""Tests for signer policy module."""

import json
import tempfile
from unittest.mock import MagicMock, patch
import pytest
from blockchain_gateway.signer_policy import (
    SignerPolicy,
    SignerPolicyError,
    SignerPolicyManager,
    PolicyAction,
)


class TestSignerPolicy:
    """Test SignerPolicy class."""

    def test_init_defaults(self):
        """Test initialization with defaults (allow_all=True)."""
        policy = SignerPolicy()
        assert policy.allow_all is True
        assert policy.policy_commiters == []
        assert policy.status_updaters == []
        assert policy.event_recorders == []

    def test_init_with_lists(self):
        """Test initialization with allowed and denied signers."""
        policy = SignerPolicy(
            policy_commiters=["0xAAA", "0xBBB"],
            status_updaters=["0xCCC"],
            event_recorders=["0xDDD"],
            allow_all=False,
        )
        assert policy.allow_all is False
        assert policy.policy_commiters == ["0xAAA", "0xBBB"]
        assert policy.status_updaters == ["0xCCC"]
        assert policy.event_recorders == ["0xDDD"]

    def test_is_policy_committer_allow_all(self):
        """Test is_policy_committer with allow_all=True."""
        policy = SignerPolicy(allow_all=True)
        assert policy.is_policy_committer("0xAnySigner") is True

    def test_is_policy_committer_allowed(self):
        """Test is_policy_committer with allowed signer."""
        policy = SignerPolicy(
            policy_commiters=["0xAAA", "0xBBB"],
            allow_all=False,
        )
        assert policy.is_policy_committer("0xAAA") is True
        assert policy.is_policy_committer("0xBBB") is True

    def test_is_policy_committer_denied(self):
        """Test is_policy_committer with non-allowed signer."""
        policy = SignerPolicy(
            policy_commiters=["0xAAA", "0xBBB"],
            allow_all=False,
        )
        assert policy.is_policy_committer("0xCCC") is False

    def test_is_status_updater_allow_all(self):
        """Test is_status_updater with allow_all=True."""
        policy = SignerPolicy(allow_all=True)
        assert policy.is_status_updater("0xAnySigner") is True

    def test_is_status_updater_allowed(self):
        """Test is_status_updater with allowed signer."""
        policy = SignerPolicy(
            status_updaters=["0xAAA", "0xBBB"],
            allow_all=False,
        )
        assert policy.is_status_updater("0xAAA") is True
        assert policy.is_status_updater("0xBBB") is True

    def test_is_status_updater_denied(self):
        """Test is_status_updater with non-allowed signer."""
        policy = SignerPolicy(
            status_updaters=["0xAAA", "0xBBB"],
            allow_all=False,
        )
        assert policy.is_status_updater("0xCCC") is False

    def test_is_event_recorder_allow_all(self):
        """Test is_event_recorder with allow_all=True."""
        policy = SignerPolicy(allow_all=True)
        assert policy.is_event_recorder("0xAnySigner") is True

    def test_is_event_recorder_allowed(self):
        """Test is_event_recorder with allowed signer."""
        policy = SignerPolicy(
            event_recorders=["0xAAA", "0xBBB"],
            allow_all=False,
        )
        assert policy.is_event_recorder("0xAAA") is True
        assert policy.is_event_recorder("0xBBB") is True

    def test_is_event_recorder_denied(self):
        """Test is_event_recorder with non-allowed signer."""
        policy = SignerPolicy(
            event_recorders=["0xAAA", "0xBBB"],
            allow_all=False,
        )
        assert policy.is_event_recorder("0xCCC") is False

    def test_can_perform_action_allow_all(self):
        """Test can_perform_action with allow_all=True."""
        policy = SignerPolicy(allow_all=True)
        assert policy.can_perform_action("0xAnySigner", PolicyAction.COMMIT_POLICY) is True
        assert policy.can_perform_action("0xAnySigner", PolicyAction.UPDATE_STATUS) is True
        assert policy.can_perform_action("0xAnySigner", PolicyAction.RECORD_EVENT) is True

    def test_can_perform_action_commit(self):
        """Test can_perform_action for commit policy."""
        policy = SignerPolicy(
            policy_commiters=["0xAAA"],
            allow_all=False,
        )
        assert policy.can_perform_action("0xAAA", PolicyAction.COMMIT_POLICY) is True
        assert policy.can_perform_action("0xBBB", PolicyAction.COMMIT_POLICY) is False

    def test_can_perform_action_update(self):
        """Test can_perform_action for update status."""
        policy = SignerPolicy(
            status_updaters=["0xAAA"],
            allow_all=False,
        )
        assert policy.can_perform_action("0xAAA", PolicyAction.UPDATE_STATUS) is True
        assert policy.can_perform_action("0xBBB", PolicyAction.UPDATE_STATUS) is False

    def test_can_perform_action_record(self):
        """Test can_perform_action for record event."""
        policy = SignerPolicy(
            event_recorders=["0xAAA"],
            allow_all=False,
        )
        assert policy.can_perform_action("0xAAA", PolicyAction.RECORD_EVENT) is True
        assert policy.can_perform_action("0xBBB", PolicyAction.RECORD_EVENT) is False

    def test_to_dict(self):
        """Test to_dict serialization."""
        policy = SignerPolicy(
            policy_commiters=["0xAAA"],
            status_updaters=["0xBBB"],
            event_recorders=["0xCCC"],
            allow_all=False,
        )
        d = policy.to_dict()
        assert d["policy_commiters"] == ["0xAAA"]
        assert d["status_updaters"] == ["0xBBB"]
        assert d["event_recorders"] == ["0xCCC"]
        assert d["allow_all"] is False


class TestPolicyAction:
    """Test PolicyAction enum."""

    def test_values(self):
        """Test enum values."""
        assert PolicyAction.COMMIT_POLICY.value == "commit_policy"
        assert PolicyAction.UPDATE_STATUS.value == "update_status"
        assert PolicyAction.RECORD_EVENT.value == "record_event"


class TestSignerPolicyManager:
    """Test SignerPolicyManager class."""

    def test_init(self):
        """Test initialization."""
        manager = SignerPolicyManager()
        assert manager.policy is not None
        assert manager.policy.allow_all is True

    def test_load_from_dict(self):
        """Test loading policy from dict."""
        manager = SignerPolicyManager()
        config = {
            "policy_commiters": ["0xAAA", "0xBBB"],
            "status_updaters": ["0xCCC"],
            "event_recorders": ["0xDDD"],
            "allow_all": False,
        }
        manager.load_from_dict(config)
        assert manager.policy.allow_all is False
        assert manager.policy.policy_commiters == ["0xAAA", "0xBBB"]
        assert manager.policy.status_updaters == ["0xCCC"]
        assert manager.policy.event_recorders == ["0xDDD"]

    def test_load_from_dict_defaults(self):
        """Test loading policy from dict with defaults."""
        manager = SignerPolicyManager()
        manager.load_from_dict({})
        assert manager.policy.allow_all is False
        assert manager.policy.policy_commiters == []
        assert manager.policy.status_updaters == []
        assert manager.policy.event_recorders == []

    def test_enforce_allowed(self):
        """Test enforce with allowed signer (no exception)."""
        manager = SignerPolicyManager()
        manager.load_from_dict({
            "policy_commiters": ["0xAAA"],
            "allow_all": False,
        })
        # Should not raise
        manager.enforce("0xAAA", PolicyAction.COMMIT_POLICY)

    def test_enforce_denied(self):
        """Test enforce with denied signer (raises exception)."""
        manager = SignerPolicyManager()
        manager.load_from_dict({
            "policy_commiters": ["0xAAA"],
            "allow_all": False,
        })
        with pytest.raises(SignerPolicyError, match="not authorized"):
            manager.enforce("0xBBB", PolicyAction.COMMIT_POLICY)

    def test_is_enforced_allowed(self):
        """Test is_enforced with allowed signer."""
        manager = SignerPolicyManager()
        manager.load_from_dict({
            "policy_commiters": ["0xAAA"],
            "allow_all": False,
        })
        assert manager.is_enforced("0xAAA", PolicyAction.COMMIT_POLICY) is True

    def test_is_enforced_denied(self):
        """Test is_enforced with denied signer."""
        manager = SignerPolicyManager()
        manager.load_from_dict({
            "policy_commiters": ["0xAAA"],
            "allow_all": False,
        })
        assert manager.is_enforced("0xBBB", PolicyAction.COMMIT_POLICY) is False

    def test_add_policy_committer(self):
        """Test add_policy_committer."""
        manager = SignerPolicyManager()
        manager.add_policy_committer("0xAAA")
        assert "0xAAA" in manager.policy.policy_commiters

    def test_add_policy_committer_duplicate(self):
        """Test add_policy_committer with duplicate address."""
        manager = SignerPolicyManager()
        manager.add_policy_committer("0xAAA")
        manager.add_policy_committer("0xAAA")
        assert manager.policy.policy_commiters.count("0xAAA") == 1

    def test_add_status_updater(self):
        """Test add_status_updater."""
        manager = SignerPolicyManager()
        manager.add_status_updater("0xAAA")
        assert "0xAAA" in manager.policy.status_updaters

    def test_add_event_recorder(self):
        """Test add_event_recorder."""
        manager = SignerPolicyManager()
        manager.add_event_recorder("0xAAA")
        assert "0xAAA" in manager.policy.event_recorders


class TestSignerPolicyError:
    """Test SignerPolicyError exception."""

    def test_exception(self):
        """Test that it's a proper exception."""
        with pytest.raises(SignerPolicyError, match="test error"):
            raise SignerPolicyError("test error")
