from insurance_observability.redaction import redact_mapping


def test_redact_mapping_masks_sensitive_nested_fields():
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "vehicle": {"vin": "1234567890", "year": 2023},
        "drivers": [{"driver_license": "A123", "age": 35}],
    }

    redacted = redact_mapping(payload)

    assert redacted["name"] == "Jane Doe"
    assert redacted["email"] == "[REDACTED]"
    assert redacted["vehicle"]["vin"] == "[REDACTED]"
    assert redacted["vehicle"]["year"] == 2023
    assert redacted["drivers"][0]["driver_license"] == "[REDACTED]"
