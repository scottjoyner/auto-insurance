-- Phase 1 quote service schema baseline.
-- This mirrors the SQLAlchemy models and is intended as the starting point for
-- replacing prototype auto_create_schema with a real migration runner.

CREATE TABLE IF NOT EXISTS quotes (
    quote_id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(128),
    customer_id VARCHAR(128),
    product_id VARCHAR(128) NOT NULL,
    product_version VARCHAR(64) NOT NULL,
    jurisdiction VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    total_premium FLOAT NOT NULL DEFAULT 0,
    coverages JSON NOT NULL,
    reason_codes JSON NOT NULL,
    surcharges_applied JSON NOT NULL,
    discounts_applied JSON NOT NULL,
    bind_eligible BOOLEAN NOT NULL DEFAULT FALSE,
    referral_flag VARCHAR(64) NOT NULL DEFAULT 'none',
    referral_reason TEXT NOT NULL DEFAULT '',
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL,
    accepted_at TIMESTAMP,
    rating_result_hash VARCHAR(128) NOT NULL DEFAULT '',
    input_snapshot_hash VARCHAR(128) NOT NULL DEFAULT '',
    ai_confidence_score FLOAT,
    applicant_data JSON NOT NULL,
    created_by_actor_id VARCHAR(128) NOT NULL DEFAULT 'system',
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_quotes_tenant_customer ON quotes (tenant_id, customer_id);
CREATE INDEX IF NOT EXISTS ix_quotes_product_status ON quotes (product_id, status);

CREATE TABLE IF NOT EXISTS quote_versions (
    id INTEGER PRIMARY KEY,
    quote_id VARCHAR(36) NOT NULL,
    version_number INTEGER NOT NULL,
    reason TEXT NOT NULL DEFAULT 'created',
    quote_snapshot JSON NOT NULL,
    input_snapshot_hash VARCHAR(128) NOT NULL DEFAULT '',
    rating_result_hash VARCHAR(128) NOT NULL DEFAULT '',
    created_by_actor_id VARCHAR(128) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_quote_versions_quote_version ON quote_versions (quote_id, version_number);

CREATE TABLE IF NOT EXISTS quote_status_history (
    id INTEGER PRIMARY KEY,
    quote_id VARCHAR(36) NOT NULL,
    from_status VARCHAR(32),
    to_status VARCHAR(32) NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    actor_id VARCHAR(128) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS quote_events (
    event_id VARCHAR(64) PRIMARY KEY,
    event_type VARCHAR(128) NOT NULL,
    aggregate_id VARCHAR(36) NOT NULL,
    aggregate_type VARCHAR(64) NOT NULL DEFAULT 'quote',
    actor_id VARCHAR(128) NOT NULL DEFAULT 'system',
    payload JSON NOT NULL,
    published_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS quote_rating_traces (
    id INTEGER PRIMARY KEY,
    quote_id VARCHAR(36) NOT NULL,
    rating_result_hash VARCHAR(128) NOT NULL,
    input_snapshot_hash VARCHAR(128) NOT NULL,
    trace JSON NOT NULL,
    created_at TIMESTAMP NOT NULL
);
