"""Quote service configuration."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class QuoteServiceSettings(BaseSettings):
    """Settings for the Quote Service."""
    app_name: str = "quote-service"
    version: str = "0.1.0"
    debug: bool = False

    # Product configuration
    default_product_yaml: str = "data/sample-products/sample_personal_auto_v1.yml"

    # Quote defaults
    default_validity_days: int = 30
    max_validity_days: int = 365

    # Expiration
    quote_expiration_check_interval: int = 300  # seconds
    quote_expiration_batch_size: int = 100

    # AI confidence
    ai_confidence_threshold: float = 0.7
    ai_model_id: str = "default"

    # Logging
    log_level: str = "INFO"

    model_config = {"env_prefix": "QUOTE_SERVICE_"}


settings = QuoteServiceSettings()
