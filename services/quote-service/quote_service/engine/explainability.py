"""Quote explainability - generates human-readable explanations for quote decisions."""

from __future__ import annotations

from typing import Any

from quote_service.domain.models import Quote, ReferralFlag


class QuoteExplainability:
    """Generates explainability reports for quotes."""

    @staticmethod
    def explain(quote: Quote) -> dict[str, Any]:
        """Generate a comprehensive explainability report for a quote."""
        report = {
            "quote_id": str(quote.quote_id),
            "summary": QuoteExplainability._build_summary(quote),
            "premium_breakdown": QuoteExplainability._build_premium_breakdown(quote),
            "factor_analysis": QuoteExplainability._build_factor_analysis(quote),
            "eligibility": QuoteExplainability._build_eligibility_report(quote),
            "referral": QuoteExplainability._build_referral_report(quote),
            "audit_trail": {
                "product_id": quote.product_id,
                "product_version": quote.product_version,
                "jurisdiction": quote.jurisdiction,
                "rating_result_hash": quote.rating_result_hash,
                "input_snapshot_hash": quote.input_snapshot_hash,
                "generated_at": quote.created_at.isoformat(),
                "expires_at": quote.expires_at.isoformat(),
            },
        }
        return report

    @staticmethod
    def explain_text(quote: Quote) -> str:
        """Generate a human-readable text explanation of the quote."""
        lines = [
            f"Quote: {quote.quote_id}",
            f"Product: {quote.product_id} v{quote.product_version}",
            f"Total Premium: ${quote.total_premium:.2f}/month",
            "",
        ]

        # Coverages
        if quote.coverages:
            lines.append("Coverages:")
            for name, premium in sorted(quote.coverages.items()):
                lines.append(f"  - {name}: ${premium:.2f}")
            lines.append("")

        # Surcharges
        if quote.surcharges_applied:
            lines.append("Surcharges Applied:")
            for s in quote.surcharges_applied:
                lines.append(f"  + {s}")
            lines.append("")

        # Discounts
        if quote.discounts_applied:
            lines.append("Discounts Applied:")
            for d in quote.discounts_applied:
                lines.append(f"  - {d}")
            lines.append("")

        # Bind eligibility
        lines.append(f"Bind Eligible: {'Yes' if quote.bind_eligible else 'No'}")

        # Referral info
        if quote.referral_flag != ReferralFlag.NONE:
            lines.append(f"Referral: {quote.referral_flag}")
            if quote.referral_reason:
                lines.append(f"Reason: {quote.referral_reason}")

        # Expiration
        lines.append(f"Expires: {quote.expires_at.strftime('%Y-%m-%d')}")

        return "\n".join(lines)

    @staticmethod
    def _build_summary(quote: Quote) -> dict[str, Any]:
        return {
            "total_premium": quote.total_premium,
            "num_coverages": len(quote.coverages),
            "num_surcharges": len(quote.surcharges_applied),
            "num_discounts": len(quote.discounts_applied),
            "bind_eligible": quote.bind_eligible,
        }

    @staticmethod
    def _build_premium_breakdown(quote: Quote) -> dict[str, Any]:
        return {
            "coverages": quote.coverages,
            "surcharges_applied": quote.surcharges_applied,
            "discounts_applied": quote.discounts_applied,
            "net_premium": quote.total_premium,
        }

    @staticmethod
    def _build_factor_analysis(quote: Quote) -> dict[str, Any]:
        factors = {}
        if quote.surcharges_applied:
            factors["surcharges"] = {
                "count": len(quote.surcharges_applied),
                "names": quote.surcharges_applied,
            }
        if quote.discounts_applied:
            factors["discounts"] = {
                "count": len(quote.discounts_applied),
                "names": quote.discounts_applied,
            }
        return factors

    @staticmethod
    def _build_eligibility_report(quote: Quote) -> dict[str, Any]:
        return {
            "eligible": quote.bind_eligible,
            "reason_codes": quote.reason_codes,
            "status": quote.status,
        }

    @staticmethod
    def _build_referral_report(quote: Quote) -> dict[str, Any]:
        if quote.referral_flag == ReferralFlag.NONE:
            return {"referral_required": False}
        return {
            "referral_required": True,
            "flag": quote.referral_flag,
            "reason": quote.referral_reason,
        }
