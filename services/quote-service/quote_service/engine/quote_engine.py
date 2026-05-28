"""Quote Engine - wraps rating-dsl to generate and manage quotes."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from rating_dsl.engine import RatingResult, evaluate, EligibilityError
from rating_dsl.parser import load_product

from quote_service.domain.models import (
    Quote,
    QuoteInputSnapshot,
    QuoteRecalculationRequest,
    QuoteRecalculationResult,
    QuoteStatus,
    ReferralFlag,
)

logger = logging.getLogger(__name__)


class QuoteEngine:
    """Core engine for quote generation using the rating-dsl."""

    def __init__(self, product_yaml_path: str):
        self._product = load_product(product_yaml_path)
        self._product_hash = self._compute_product_hash()

    def _compute_product_hash(self) -> str:
        """Compute a hash of the loaded product config for audit trail."""
        # Hash the product YAML content
        import yaml
        with open(self._product.__dict__.get("_yaml_path", "/dev/null"), "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]

    def generate_quote(
        self,
        applicant_data: dict[str, Any],
        product_id: str | None = None,
        product_version: str | None = None,
        jurisdiction: str | None = None,
        validity_days: int = 30,
    ) -> Quote:
        """Generate a new quote from applicant data."""
        # Build input snapshot
        input_hash = hashlib.sha256(
            str(sorted(applicant_data.items())).encode()
        ).hexdigest()[:16]

        snapshot = QuoteInputSnapshot(
            applicant_data=applicant_data,
            product_id=product_id or self._product.product,
            product_version=product_version or self._product.version,
            jurisdiction=jurisdiction or self._product.jurisdiction,
            input_hash=input_hash,
            captured_at=datetime.utcnow(),
        )

        # Evaluate rating
        try:
            rating_result: RatingResult = evaluate(self._product, applicant_data)
        except EligibilityError as e:
            logger.warning("Eligibility error for quote: %s", e)
            return Quote(
                product_id=snapshot.product_id,
                product_version=snapshot.product_version,
                jurisdiction=snapshot.jurisdiction,
                status=QuoteStatus.DRAFT,
                reason_codes=["eligibility_failure"],
                bind_eligible=False,
                referral_flag=ReferralFlag.UNDERWRITER_REFERRAL,
                referral_reason=str(e),
                input_snapshot_hash=input_hash,
                expires_at=datetime.utcnow() + timedelta(days=validity_days),
            )

        # Build quote from rating result
        quote = Quote(
            product_id=snapshot.product_id,
            product_version=snapshot.product_version,
            jurisdiction=snapshot.jurisdiction,
            status=QuoteStatus.QUOTED,
            total_premium=float(rating_result.total_premium),
            coverages={k: float(v) for k, v in rating_result.coverage_dict.items()},
            reason_codes=rating_result.reason_codes if hasattr(rating_result, 'reason_codes') else [],
            surcharges_applied=rating_result.surcharges_applied,
            discounts_applied=rating_result.discounts_applied,
            bind_eligible=rating_result.is_valid and rating_result.eligibility_passed,
            rating_result_hash=hashlib.sha256(
                str(sorted(rating_result.coverage_dict.items())).encode()
            ).hexdigest()[:16],
            input_snapshot_hash=input_hash,
            expires_at=datetime.utcnow() + timedelta(days=validity_days),
        )

        # Check bind eligibility against risk appetite
        if not quote.bind_eligible:
            quote.referral_flag = ReferralFlag.UNDERWRITER_REFERRAL
            quote.referral_reason = "Quote failed eligibility checks"

        quote.mark_quoted()
        logger.info("Quote generated: %s, premium: %.2f", quote.quote_id, quote.total_premium)
        return quote

    def recalculate_quote(
        self,
        request: QuoteRecalculationRequest,
    ) -> QuoteRecalculationResult:
        """Recalculate a quote with updated applicant data."""
        # Evaluate with new data
        new_result = evaluate(self._product, request.updated_applicant_data)
        new_premium = float(new_result.total_premium)

        # We'd need the old premium from the stored quote
        # For now, return the result with placeholder
        return QuoteRecalculationResult(
            quote_id=request.quote_id,
            previous_premium=0.0,  # Would come from stored Quote
            new_premium=new_premium,
            premium_change=0.0,
            premium_change_pct=0.0,
            changed_factors=[],
            new_surcharges=new_result.surcharges_applied,
            new_discounts=new_result.discounts_applied,
            new_reason_codes=new_result.reason_codes if hasattr(new_result, 'reason_codes') else [],
            new_bind_eligible=new_result.is_valid and new_result.eligibility_passed,
            recalculation_hash=hashlib.sha256(
                str(sorted(request.updated_applicant_data.items())).encode()
            ).hexdigest()[:16],
        )

    def check_expiration(self, quote: Quote) -> bool:
        """Check if a quote has expired and update status if needed."""
        if quote.is_expired():
            quote.mark_expired()
            return True
        return False

    def explain_quote(self, quote: Quote) -> dict[str, Any]:
        """Generate an explainability report for a quote."""
        return {
            "quote_id": str(quote.quote_id),
            "product_id": quote.product_id,
            "product_version": quote.product_version,
            "jurisdiction": quote.jurisdiction,
            "total_premium": quote.total_premium,
            "coverages": quote.coverages,
            "surcharges": quote.surcharges_applied,
            "discounts": quote.discounts_applied,
            "reason_codes": quote.reason_codes,
            "bind_eligible": quote.bind_eligible,
            "referral_flag": quote.referral_flag,
            "referral_reason": quote.referral_reason,
            "rating_result_hash": quote.rating_result_hash,
            "input_snapshot_hash": quote.input_snapshot_hash,
            "expires_at": quote.expires_at.isoformat(),
            "created_at": quote.created_at.isoformat(),
        }
