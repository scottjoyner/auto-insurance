"""PII redaction helpers for logs and traces."""

from __future__ import annotations

from typing import Any

SENSITIVE_KEYS = {
    "ssn",
    "social_security_number",
    "dob",
    "date_of_birth",
    "driver_license",
    "drivers_license",
    "email",
    "phone",
    "address",
    "vin",
    "payment_method",
    "card_number",
    "bank_account",
}


def redact_mapping(value: Any) -> Any:
    """Recursively redact sensitive fields in dictionaries/lists."""
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact_mapping(item)
        return redacted
    if isinstance(value, list):
        return [redact_mapping(item) for item in value]
    return value
