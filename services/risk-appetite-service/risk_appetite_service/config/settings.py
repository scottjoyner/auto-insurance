"""Risk appetite service configuration."""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings


class RiskAppetiteSettings(BaseSettings):
    """Settings for the Risk Appetite Service."""

    app_name: str = "risk-appetite-service"
    version: str = "0.1.0"
    debug: bool = False

    # API security defaults
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    allow_credentials: bool = False
    require_auth: bool = True
    enable_runtime_policy_update: bool = False

    # Risk appetite policy
    policy_path: str = "data/risk-appetite-policy.yml"

    # Portfolio state refresh
    portfolio_state_ttl: int = 300  # seconds
    portfolio_state_refresh_interval: int = 60  # seconds

    # Assessment defaults
    default_risk_score_weight_driver_age: float = 0.25
    default_risk_score_weight_claim_severity: float = 0.25
    default_risk_score_weight_vehicle_type: float = 0.15
    default_risk_score_weight_agency: float = 0.10
    default_risk_score_weight_geographic: float = 0.10
    default_risk_score_weight_lob: float = 0.15

    # Capital defaults (stub)
    default_available_capital: float = 10_000_000.0
    default_capital_ratio: float = 0.15

    # Reinsurance defaults (stub)
    default_retention_pct: float = 30.0
    default_total_capacity: float = 50_000_000.0
    default_current_utilization: float = 0.6

    # Logging
    log_level: str = "INFO"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    model_config = {"env_prefix": "RISK_APPETITE_"}


settings = RiskAppetiteSettings()
