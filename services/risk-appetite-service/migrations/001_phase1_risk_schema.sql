-- Phase 1 risk appetite service schema baseline.

CREATE TABLE IF NOT EXISTS risk_policy_versions (
    id INTEGER PRIMARY KEY,
    version VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    effective_date VARCHAR(32) NOT NULL DEFAULT '',
    policy_data JSON NOT NULL,
    submitted_by_actor_id VARCHAR(128),
    approved_by_actor_id VARCHAR(128),
    activated_by_actor_id VARCHAR(128),
    created_at TIMESTAMP NOT NULL,
    submitted_at TIMESTAMP,
    approved_at TIMESTAMP,
    activated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_risk_policy_versions_status ON risk_policy_versions (status);
CREATE INDEX IF NOT EXISTS ix_risk_policy_versions_version ON risk_policy_versions (version);

CREATE TABLE IF NOT EXISTS risk_policy_approvals (
    id INTEGER PRIMARY KEY,
    policy_version_id INTEGER NOT NULL,
    action VARCHAR(64) NOT NULL,
    actor_id VARCHAR(128) NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_risk_policy_approvals_policy_version_id ON risk_policy_approvals (policy_version_id);

CREATE TABLE IF NOT EXISTS risk_assessments (
    assessment_id VARCHAR(36) PRIMARY KEY,
    quote_id VARCHAR(36) NOT NULL,
    policy_version VARCHAR(64) NOT NULL,
    decision VARCHAR(64) NOT NULL,
    risk_score FLOAT NOT NULL DEFAULT 0,
    risk_level VARCHAR(32) NOT NULL DEFAULT 'LOW',
    quote_data JSON NOT NULL,
    portfolio_state JSON NOT NULL,
    assessment_payload JSON NOT NULL,
    actor_id VARCHAR(128) NOT NULL DEFAULT 'system',
    assessed_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_risk_assessments_quote_id ON risk_assessments (quote_id);
CREATE INDEX IF NOT EXISTS ix_risk_assessments_policy_version ON risk_assessments (policy_version);
CREATE INDEX IF NOT EXISTS ix_risk_assessments_decision ON risk_assessments (decision);
