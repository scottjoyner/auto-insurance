"""Blockchain gateway configuration."""

from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field


class BlockchainGatewaySettings(BaseSettings):
    """Settings for the Blockchain Gateway service."""

    # Connection
    rpc_url: str = "http://localhost:8545"
    chain_id: int = 31337

    # Contract addresses (set after deployment)
    policy_registry_address: str = ""
    audit_event_registry_address: str = ""

    # Signer
    signer_private_key: str = ""
    signer_policy_file: str = "signer-policy.yaml"

    # Outbox
    outbox_db_path: str = "outbox.db"
    outbox_poll_interval_seconds: int = 5
    max_retries: int = 5
    retry_backoff_base: int = 2

    # Reconciliation
    reconciliation_enabled: bool = False
    reconciliation_cron: str = "0 */6 * * *"  # every 6 hours
    reconciliation_window_hours: int = 24

    # API
    log_level: str = "INFO"

    model_config = {"env_prefix": "BLOCKCHAIN_GATEWAY_", "env_file": ".env"}


settings = BlockchainGatewaySettings()
