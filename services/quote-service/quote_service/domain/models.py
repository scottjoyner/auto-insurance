"""Quote domain models for the Quote Service."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class QuoteStatus(StrEnum):
    DRAFT = "DRAFT"
    QUOTED = "QUOTED"
    EXPIRED = "EXPIRED"
    WITHDRAWN = "WITHDRAWN"
    CONVERTED = "CONVERTED"


class ReferralFlag(StrEnum):
    NONE = "none"
    RISK_APPETITE_REFERRAL = "risk_appetite_referral"
    UNDERWRITER_REFERRAL = "underwriter_referral"
    MANUAL_REVIEW = "manual_review"
    AI_CONFIDENCE_LOW = "ai_confidence_low"


@dataclass(frozen=True)
class QuoteInputSnapshot:
    """Immutable snapshot of applicant data used for a quote."""
    applicant_data: dict[str, Any]
    product_id: str
    product_version: str
    jurisdiction: str
    input_hash: str
    captured_at: datetime

    @classmethod
    def create(
        cls,
        applicant_data: dict[str, Any],
        product_id: str,
        product_version: str,
        jurisdiction: str,
        input_hash: str,
    ) -> QuoteInputSnapshot:
        return cls(
            applicant_data=applicant_data,
            product_id=product_id,
            product_version=product_version,
            jurisdiction=jurisdiction,
            input_hash=input_hash,
            captured_at=datetime.utcnow(),
        )


@dataclass
class Quote:
    """A generated insurance quote."""
    quote_id: UUID = field(default_factory=uuid4)
    product_id: str = ""
    product_version: str = ""
    jurisdiction: str = ""
    status: QuoteStatus = QuoteStatus.DRAFT
    total_premium: float = 0.0
    coverages: dict[str, float] = field(default_factory=dict)
    reason_codes: list[str] = field(default_factory=list)
    surcharges_applied: list[str] = field(default_factory=list)
    discounts_applied: list[str] = field(default_factory=list)
    bind_eligible: bool = False
    referral_flag: ReferralFlag = ReferralFlag.NONE
    referral_reason: str = ""
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    created_at: datetime = field(default_factory=lambda: datetime.utcnow())
    accepted_at: datetime | None = None
    rating_result_hash: str = ""
    input_snapshot_hash: str = ""
    ai_confidence_score: float | None = None
    _applicant_data: dict[str, Any] = field(default_factory=dict, repr=False)

    def mark_quoted(self) -> None:
        self.status = QuoteStatus.QUOTED

    def mark_expired(self) -> None:
        self.status = QuoteStatus.EXPIRED

    def mark_withdrawn(self) -> None:
        self.status = QuoteStatus.WITHDRAWN

    def mark_converted(self) -> None:
        self.status = QuoteStatus.CONVERTED

    def is_expired(self) -> bool:
        return self.status != QuoteStatus.EXPIRED and datetime.utcnow() > self.expires_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "quote_id": str(self.quote_id),
            "product_id": self.product_id,
            "product_version": self.product_version,
            "jurisdiction": self.jurisdiction,
            "status": self.status,
            "total_premium": self.total_premium,
            "coverages": {k: float(v) for k, v in self.coverages.items()},
            "reason_codes": self.reason_codes,
            "surcharges_applied": self.surcharges_applied,
            "discounts_applied": self.discounts_applied,
            "bind_eligible": self.bind_eligible,
            "referral_flag": self.referral_flag,
            "referral_reason": self.referral_reason,
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "rating_result_hash": self.rating_result_hash,
            "ai_confidence_score": self.ai_confidence_score,
        }


@dataclass
class QuoteRecalculationRequest:
    """Request to recalculate an existing quote with updated data."""
    quote_id: UUID
    updated_applicant_data: dict[str, Any]
    reason: str = ""


@dataclass
class QuoteRecalculationResult:
    """Result of a quote recalculation."""
    quote_id: UUID
    previous_premium: float
    new_premium: float
    premium_change: float
    premium_change_pct: float
    changed_factors: list[str] = field(default_factory=list)
    new_surcharges: list[str] = field(default_factory=list)
    new_discounts: list[str] = field(default_factory=list)
    new_reason_codes: list[str] = field(default_factory=list)
    new_bind_eligible: bool = False
    new_referral_flag: ReferralFlag = ReferralFlag.NONE
    recalculation_hash: str = ""
