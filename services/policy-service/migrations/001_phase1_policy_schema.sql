-- Phase 1 policy service schema baseline.

CREATE TABLE IF NOT EXISTS bind_requests (
    bind_request_id VARCHAR(36) PRIMARY KEY,
    quote_id VARCHAR(36) NOT NULL,
    policy_id VARCHAR(36) NOT NULL,
    request_key VARCHAR(128),
    status VARCHAR(32) NOT NULL DEFAULT 'pending_approval',
    bind_method VARCHAR(64) NOT NULL DEFAULT 'human_approval',
    total_premium FLOAT NOT NULL DEFAULT 0,
    effective_date TIMESTAMP NOT NULL,
    expiration_date TIMESTAMP NOT NULL,
    quote_snapshot JSON NOT NULL,
    risk_assessment_snapshot JSON NOT NULL,
    created_by_actor_id VARCHAR(128) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_bind_requests_quote_id ON bind_requests (quote_id);
CREATE INDEX IF NOT EXISTS ix_bind_requests_policy_id ON bind_requests (policy_id);
CREATE INDEX IF NOT EXISTS ix_bind_requests_request_key ON bind_requests (request_key);
CREATE INDEX IF NOT EXISTS ix_bind_requests_status ON bind_requests (status);

CREATE TABLE IF NOT EXISTS bind_approvals (
    approval_id VARCHAR(36) PRIMARY KEY,
    bind_request_id VARCHAR(36) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    approver_actor_id VARCHAR(128),
    comments TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL,
    decided_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_bind_approvals_bind_request_id ON bind_approvals (bind_request_id);
CREATE INDEX IF NOT EXISTS ix_bind_approvals_status ON bind_approvals (status);

CREATE TABLE IF NOT EXISTS policies (
    policy_id VARCHAR(36) PRIMARY KEY,
    quote_id VARCHAR(36) NOT NULL,
    bind_request_id VARCHAR(36) NOT NULL,
    state VARCHAR(32) NOT NULL DEFAULT 'active',
    total_premium FLOAT NOT NULL DEFAULT 0,
    effective_date TIMESTAMP NOT NULL,
    expiration_date TIMESTAMP NOT NULL,
    bind_packet JSON NOT NULL,
    bound_by_actor_id VARCHAR(128) NOT NULL DEFAULT 'system',
    bound_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_policies_quote_id ON policies (quote_id);
CREATE INDEX IF NOT EXISTS ix_policies_bind_request_id ON policies (bind_request_id);
CREATE INDEX IF NOT EXISTS ix_policies_state ON policies (state);

CREATE TABLE IF NOT EXISTS policy_events (
    event_id VARCHAR(36) PRIMARY KEY,
    event_type VARCHAR(128) NOT NULL,
    aggregate_id VARCHAR(36) NOT NULL,
    actor_id VARCHAR(128) NOT NULL DEFAULT 'system',
    payload JSON NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_policy_events_event_type ON policy_events (event_type);
CREATE INDEX IF NOT EXISTS ix_policy_events_aggregate_id ON policy_events (aggregate_id);
