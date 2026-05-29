-- Phase 1 claims service schema baseline.

CREATE TABLE IF NOT EXISTS claims (
    claim_id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(128),
    customer_id VARCHAR(128),
    policy_id VARCHAR(36) NOT NULL,
    status VARCHAR(64) NOT NULL DEFAULT 'open',
    severity VARCHAR(32) NOT NULL DEFAULT 'low',
    queue VARCHAR(64) NOT NULL DEFAULT 'New FNOL',
    loss_type VARCHAR(64) NOT NULL,
    loss_date TIMESTAMP NOT NULL,
    loss_location TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    police_report_indicator BOOLEAN NOT NULL DEFAULT FALSE,
    injuries_indicator BOOLEAN NOT NULL DEFAULT FALSE,
    preferred_contact_method VARCHAR(64) NOT NULL DEFAULT 'email',
    fnol_payload JSON NOT NULL,
    created_by_actor_id VARCHAR(128) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_claims_tenant_customer ON claims (tenant_id, customer_id);
CREATE INDEX IF NOT EXISTS ix_claims_policy_id ON claims (policy_id);
CREATE INDEX IF NOT EXISTS ix_claims_status ON claims (status);
CREATE INDEX IF NOT EXISTS ix_claims_queue ON claims (queue);
CREATE INDEX IF NOT EXISTS ix_claims_severity ON claims (severity);

CREATE TABLE IF NOT EXISTS claim_evidence (
    evidence_id VARCHAR(36) PRIMARY KEY,
    claim_id VARCHAR(36) NOT NULL,
    evidence_type VARCHAR(64) NOT NULL,
    source VARCHAR(128) NOT NULL DEFAULT 'customer',
    uri TEXT NOT NULL DEFAULT '',
    checksum VARCHAR(128) NOT NULL DEFAULT '',
    visibility VARCHAR(64) NOT NULL DEFAULT 'internal',
    uploaded_by_actor_id VARCHAR(128) NOT NULL,
    uploaded_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_claim_evidence_claim_id ON claim_evidence (claim_id);

CREATE TABLE IF NOT EXISTS claim_notes (
    note_id VARCHAR(36) PRIMARY KEY,
    claim_id VARCHAR(36) NOT NULL,
    note_type VARCHAR(64) NOT NULL DEFAULT 'adjuster',
    body TEXT NOT NULL,
    created_by_actor_id VARCHAR(128) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_claim_notes_claim_id ON claim_notes (claim_id);

CREATE TABLE IF NOT EXISTS claim_status_history (
    id INTEGER PRIMARY KEY,
    claim_id VARCHAR(36) NOT NULL,
    from_status VARCHAR(64),
    to_status VARCHAR(64) NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    actor_id VARCHAR(128) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_claim_status_history_claim_id ON claim_status_history (claim_id);

CREATE TABLE IF NOT EXISTS claim_reserve_history (
    id INTEGER PRIMARY KEY,
    claim_id VARCHAR(36) NOT NULL,
    amount FLOAT NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    recommended_by_actor_id VARCHAR(128) NOT NULL,
    approved_by_actor_id VARCHAR(128),
    status VARCHAR(64) NOT NULL DEFAULT 'pending_approval',
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_claim_reserve_history_claim_id ON claim_reserve_history (claim_id);

CREATE TABLE IF NOT EXISTS claim_events (
    event_id VARCHAR(36) PRIMARY KEY,
    event_type VARCHAR(128) NOT NULL,
    aggregate_id VARCHAR(36) NOT NULL,
    actor_id VARCHAR(128) NOT NULL,
    payload JSON NOT NULL,
    published_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_claim_events_event_type ON claim_events (event_type);
CREATE INDEX IF NOT EXISTS ix_claim_events_aggregate_id ON claim_events (aggregate_id);
