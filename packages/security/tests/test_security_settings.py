import pytest

from insurance_security.settings import SecuritySettings, SecuritySettingsError, validate_security_settings


def test_dev_mode_allows_missing_jwt_settings():
    settings = validate_security_settings(SecuritySettings(auth_mode="dev"))
    assert settings.auth_mode == "dev"


def test_rejects_unknown_auth_mode():
    with pytest.raises(SecuritySettingsError):
        validate_security_settings(SecuritySettings(auth_mode="unknown"))


def test_jwt_mode_requires_issuer():
    with pytest.raises(SecuritySettingsError, match="INSURANCE_JWT_ISSUER"):
        validate_security_settings(
            SecuritySettings(
                auth_mode="jwt",
                jwt_audience="auto-insurance-api",
                jwt_algorithm="HS256",
                jwt_hs256_secret="secret",
            )
        )


def test_jwt_mode_requires_audience():
    with pytest.raises(SecuritySettingsError, match="INSURANCE_JWT_AUDIENCE"):
        validate_security_settings(
            SecuritySettings(
                auth_mode="jwt",
                jwt_issuer="https://idp.example.test/",
                jwt_algorithm="HS256",
                jwt_hs256_secret="secret",
            )
        )


def test_hs256_requires_secret():
    with pytest.raises(SecuritySettingsError, match="INSURANCE_JWT_HS256_SECRET"):
        validate_security_settings(
            SecuritySettings(
                auth_mode="jwt",
                jwt_issuer="https://idp.example.test/",
                jwt_audience="auto-insurance-api",
                jwt_algorithm="HS256",
            )
        )


def test_rs256_requires_jwks_url():
    with pytest.raises(SecuritySettingsError, match="INSURANCE_JWT_JWKS_URL"):
        validate_security_settings(
            SecuritySettings(
                auth_mode="jwt",
                jwt_issuer="https://idp.example.test/",
                jwt_audience="auto-insurance-api",
                jwt_algorithm="RS256",
            )
        )


def test_valid_hs256_settings_pass():
    settings = validate_security_settings(
        SecuritySettings(
            auth_mode="jwt",
            jwt_issuer="https://idp.example.test/",
            jwt_audience="auto-insurance-api",
            jwt_algorithm="HS256",
            jwt_hs256_secret="secret",
        )
    )
    assert settings.jwt_algorithm == "HS256"


def test_valid_rs256_settings_pass():
    settings = validate_security_settings(
        SecuritySettings(
            auth_mode="jwt",
            jwt_issuer="https://idp.example.test/",
            jwt_audience="auto-insurance-api",
            jwt_algorithm="RS256",
            jwt_jwks_url="https://idp.example.test/.well-known/jwks.json",
        )
    )
    assert settings.jwt_algorithm == "RS256"
