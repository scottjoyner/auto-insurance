# Shared Types Package

## Purpose

Core data types shared across all services. These define the canonical entities for the insurance operating system.

## File Structure

```
packages/shared-types/
  README.md
  pyproject.toml
  src/
    shared_types/
      __init__.py
      party.py
      customer.py
      product.py
      quote.py
      risk.py
      policy.py
      claim.py
      payment.py
      event.py
      audit.py
      compliance.py
  tests/
    test_party.py
    test_product.py
    test_quote.py
    test_event.py
```

## Core Types

### Party

```python
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from uuid import UUID, uuid4

class PartyType(StrEnum):
    CUSTOMER = "customer"
    AGENT = "agent"
    UNDERWRITER = "underwriter"
    CLAIMS_ADJUSTER = "claims_adjuster"
    TREASURY_ANALYST = "treasury_analyst"
    COMPLIANCE_REVIEWER = "compliance_reviewer"
    SMART_CONTRACT_SIGNER = "smart_contract_signer"
    AI_AGENT = "ai_agent"

@dataclass(frozen=True)
class Party:
    party_id: UUID
    party_type: PartyType
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    date_of_birth: date | None = None
    created_at: date = None
    updated_at: date = None
```

### Product

```python
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Optional

class ProductStatus(StrEnum):
    DRAFT = "draft"
    ARCHITECTURE_SAMPLE_ONLY = "architecture_sample_only"
    INTERNAL_REVIEW = "internal_review"
    COMPLIANCE_REVIEW = "compliance_review"
    APPROVED_FOR_TESTING = "approved_for_testing"
    APPROVED_FOR_PRODUCTION = "approved_for_production"
    SUSPENDED = "suspended"
    RETIRED = "retired"

@dataclass
class CoverageOption:
    id: str
    name: str
    base_rate: float
    required_for_bind: bool
    limit_options: list[dict] | None = None
    deductible_options: list[int] | None = None

@dataclass
class Product:
    product_id: str
    product_name: str
    product_version: str
    status: ProductStatus
    jurisdiction: str
    coverages: list[CoverageOption]
    rating_variables: list[dict]
    effective_date: date
    expiration_date: Optional[date]
    approval: dict  # {product_approved: bool, rate_approved: bool, form_approved: bool}
```

### Quote

```python
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional

class QuoteStatus(StrEnum):
    DRAFT_QUOTE = "DRAFT_QUOTE"
    QUOTED = "QUOTED"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    WITHDRAWN = "WITHDRAWN"

@dataclass
class QuoteRatingResult:
    base_rate: float
    variable_factors: dict[str, float]
    discount_applications: list[dict]
    surcharge_applications: list[dict]
    coverage_rates: dict[str, float]
    final_premium: float
    reason_codes: list[str]

@dataclass
class Quote:
    quote_id: str
    product_id: str
    product_version: str
    jurisdiction: str
    status: QuoteStatus
    rating_result: QuoteRatingResult
    input_snapshot_hash: str
    expires_at: datetime
    created_at: datetime
    accepted_at: Optional[datetime] = None
    bind_eligible: bool = False
    risk_appetite_result: Optional[dict] = None
```

### Risk Appetite Decision

```python
from dataclasses import dataclass
from enum import StrEnum

class RiskDecision(StrEnum):
    ACCEPT = "ACCEPT"
    ACCEPT_WITH_LIMITS = "ACCEPT_WITH_LIMITS"
    ACCEPT_WITH_REINSURANCE = "ACCEPT_WITH_REINSURANCE"
    REFER_TO_UNDERWRITER = "REFER_TO_UNDERWRITER"
    DECLINE = "DECLINE"
    REQUEST_MORE_INFO = "REQUEST_MORE_INFO"
    WAITLIST = "WAITLIST"

@dataclass
class RiskAppetiteDecision:
    decision: RiskDecision
    reason_codes: list[str]
    required_approvals: list[str]
    capital_impact_estimate: Optional[float] = None
    reserve_impact_estimate: Optional[float] = None
    portfolio_concentration_impact: Optional[dict] = None
    audit_reference: str = ""
```

### Policy

```python
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional

class PolicyStatus(StrEnum):
    DRAFT_QUOTE = "DRAFT_QUOTE"
    QUOTED = "QUOTED"
    ACCEPTED = "ACCEPTED"
    BIND_REQUESTED = "BIND_REQUESTED"
    BOUND = "BOUND"
    ISSUED = "ISSUED"
    ACTIVE = "ACTIVE"
    ENDORSED = "ENDORSED"
    RENEWAL_PENDING = "RENEWAL_PENDING"
    RENEWED = "RENEWED"
    CANCEL_PENDING = "CANCEL_PENDING"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    REINSTATED = "REINSTATED"
    CLAIM_LOCKED = "CLAIM_LOCKED"

@dataclass
class Policy:
    policy_id: str
    quote_id: str
    product_id: str
    product_version: str
    policy_version: str
    status: PolicyStatus
    coverage_details: dict
    premium: float
    effective_date: datetime
    expiration_date: datetime
    blockchain_commitment_hash: Optional[str] = None
    bind_approved_by: Optional[str] = None
    bind_approved_at: Optional[datetime] = None
```

### Claim

```python
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional

class ClaimStatus(StrEnum):
    FNOL_RECEIVED = "FNOL_RECEIVED"
    EVIDENCE_PENDING = "EVIDENCE_PENDING"
    COVERAGE_REVIEW = "COVERAGE_REVIEW"
    FRAUD_REVIEW = "FRAUD_REVIEW"
    ADJUSTER_REVIEW = "ADJUSTER_REVIEW"
    RESERVE_SET = "RESERVE_SET"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAID = "PAID"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"

@dataclass
class Claim:
    claim_id: str
    policy_id: str
    policy_version: str
    status: ClaimStatus
    claim_type: str
    loss_date: datetime
    reserve_amount: Optional[float] = None
    payout_amount: Optional[float] = None
    decision_reason_codes: list[str] = None
    coverage_verified: bool = False
    fraud_flag: bool = False
    blockchain_commitment_hash: Optional[str] = None
```

### Domain Event

```python
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

class ActorType(StrEnum):
    CUSTOMER = "customer"
    AI_AGENT = "ai_agent"
    SERVICE = "service"
    HUMAN = "human"
    SMART_CONTRACT = "smart_contract"
    ORACLE = "oracle"

@dataclass
class Actor:
    actor_type: ActorType
    actor_id: str

@dataclass
class DomainEvent:
    event_id: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    occurred_at: datetime
    actor: Actor
    correlation_id: str
    causation_id: str | None = None
    payload: dict[str, Any] = None
    schema_version: str = "1.0.0"
```

### Compliance Control

```python
from dataclasses import dataclass
from enum import StrEnum

class ControlFamily(StrEnum):
    PRODUCT_GOVERNANCE = "product_governance"
    QUOTE_REPRODUCIBILITY = "quote_reproducibility"
    RISK_APPETITE = "risk_appetite"
    POLICY_AUTHORITY = "policy_authority"
    CLAIMS_AUTHORITY = "claims_authority"
    AI_GOVERNANCE = "ai_governance"
    TREASURY_GOVERNANCE = "treasury_governance"
    BLOCKCHAIN_PRIVACY = "blockchain_privacy"
    AUDITABILITY = "auditability"
    SECURITY_ACCESS = "security_access"

@dataclass
class ComplianceResult:
    control_family: ControlFamily
    passed: bool
    reason: str
    details: dict = None
```
