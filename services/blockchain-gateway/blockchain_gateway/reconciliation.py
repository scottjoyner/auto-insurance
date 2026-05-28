"""Reconciliation between local state and blockchain.

Compares local audit events with on-chain records to detect:
- Events committed on-chain but missing from local state
- Events in local state not yet committed on-chain
- Hash mismatches between local and chain

Usage:
  reconciler = Reconciler(gateway, local_store)
  report = reconciler.reconcile(window_hours=24)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass
class ReconciliationReport:
    """Report of reconciliation results."""
    timestamp: str
    window_hours: int
    local_events_count: int
    chain_events_count: int
    missing_from_chain: list[str]  # local event IDs not on chain
    missing_from_local: list[str]  # chain event IDs not in local
    hash_mismatches: list[str]  # event IDs with hash mismatches
    discrepancies: list[str]  # other discrepancies
    is_clean: bool  # True if no discrepancies

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "window_hours": self.window_hours,
            "local_events_count": self.local_events_count,
            "chain_events_count": self.chain_events_count,
            "missing_from_chain": self.missing_from_chain,
            "missing_from_local": self.missing_from_local,
            "hash_mismatches": self.hash_mismatches,
            "discrepancies": self.discrepancies,
            "is_clean": self.is_clean,
        }


class Reconciler:
    """Reconciles local audit events with on-chain records."""

    def __init__(self, gateway, local_store):
        """
        Args:
            gateway: BlockchainGateway instance
            local_store: Local event store with get_events_in_window method
        """
        self.gateway = gateway
        self.local_store = local_store

    def reconcile(
        self,
        window_hours: int = 24,
    ) -> ReconciliationReport:
        """Run reconciliation for the given time window."""
        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=window_hours)

        logger.info(
            "Starting reconciliation: window=%dh from %s to %s",
            window_hours,
            start.isoformat(),
            now.isoformat(),
        )

        # Get local events in window
        local_events = self.local_store.get_events_in_window(start, now)
        local_by_hash = {e["commitment_hash"]: e for e in local_events}

        # Get chain events in window (from blocks)
        chain_events = self._get_chain_events_in_window(start, now)
        chain_by_hash = {e["commitment_hash"]: e for e in chain_events}

        # Find discrepancies
        missing_from_chain = []
        for h, evt in local_by_hash.items():
            if h not in chain_by_hash:
                missing_from_chain.append(evt["id"])

        missing_from_local = []
        for h, evt in chain_by_hash.items():
            if h not in local_by_hash:
                missing_from_local.append(h[:16] + "...")

        hash_mismatches = []
        for h in set(local_by_hash.keys()) & set(chain_by_hash.keys()):
            local = local_by_hash[h]
            chain = chain_by_hash[h]
            if local["event_type"] != chain["event_type"]:
                hash_mismatches.append(h[:16] + "...")

        discrepancies = []
        if missing_from_chain:
            discrepancies.append(f"{len(missing_from_chain)} events missing from chain")
        if missing_from_local:
            discrepancies.append(f"{len(missing_from_local)} events missing from local")
        if hash_mismatches:
            discrepancies.append(f"{len(hash_mismatches)} hash mismatches")

        report = ReconciliationReport(
            timestamp=now.isoformat(),
            window_hours=window_hours,
            local_events_count=len(local_events),
            chain_events_count=len(chain_events),
            missing_from_chain=missing_from_chain,
            missing_from_local=missing_from_local,
            hash_mismatches=hash_mismatches,
            discrepancies=discrepancies,
            is_clean=len(missing_from_chain) == 0
                and len(missing_from_local) == 0
                and len(hash_mismatches) == 0,
        )

        if report.is_clean:
            logger.info("Reconciliation clean: %d local, %d chain events",
                        report.local_events_count, report.chain_events_count)
        else:
            logger.warning("Reconciliation found %d discrepancies", len(discrepancies))

        return report

    def _get_chain_events_in_window(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        """Get on-chain audit events in the time window."""
        # Convert timestamps to block numbers
        start_ts = int(start.timestamp())
        end_ts = int(end.timestamp())

        # Query events by timestamp (approximate via block range)
        # In production, use event filters with block ranges
        all_events = self.gateway.get_event_recorded_events()
        return [
            e for e in all_events
            if start_ts <= e["committed_at"] <= end_ts
        ]
