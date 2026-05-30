-- Phase 1 customer service schema baseline.

CREATE TABLE IF NOT EXISTS tenants (
    tenant_id VARCHAR(128) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(64) NOT NULL DEFAULT 'active',
    metadata_json JSON NOT NULL,
    created_by_actor_id VARCHAR(128) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_tenants_status ON tenants (status);

CREATE TABLE IF NOT EXISTS accounts (
    account_id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(128) NOT NULL,
    name VARCHAR(255) NOT NULL,
    account_type VARCHAR(64) NOT NULL DEFAULT 'personal',
    status VARCHAR(64) NOT NULL DEFAULT 'active',
    created_by_actor_id VARCHAR(128) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_accounts_tenant_id ON accounts (tenant_id);
CREATE INDEX IF NOT EXISTS ix_accounts_status ON accounts (status);

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(128) NOT NULL,
    account_id VARCHAR(36) NOT NULL,
    first_name VARCHAR(128) NOT NULL DEFAULT '',
    last_name VARCHAR(128) NOT NULL DEFAULT '',
    display_name VARCHAR(255) NOT NULL,
    status VARCHAR(64) NOT NULL DEFAULT 'active',
    created_by_actor_id VARCHAR(128) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_customers_tenant_id ON customers (tenant_id);
CREATE INDEX IF NOT EXISTS ix_customers_account_id ON customers (account_id);
CREATE INDEX IF NOT EXISTS ix_customers_display_name ON customers (display_name);
CREATE INDEX IF NOT EXISTS ix_customers_status ON customers (status);

CREATE TABLE IF NOT EXISTS customer_contacts (
    contact_id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(128) NOT NULL,
    customer_id VARCHAR(36) NOT NULL,
    contact_type VARCHAR(64) NOT NULL,
    value VARCHAR(255) NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_customer_contacts_tenant_id ON customer_contacts (tenant_id);
CREATE INDEX IF NOT EXISTS ix_customer_contacts_customer_id ON customer_contacts (customer_id);

CREATE TABLE IF NOT EXISTS customer_addresses (
    address_id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(128) NOT NULL,
    customer_id VARCHAR(36) NOT NULL,
    address_type VARCHAR(64) NOT NULL DEFAULT 'mailing',
    line1 VARCHAR(255) NOT NULL,
    line2 VARCHAR(255) NOT NULL DEFAULT '',
    city VARCHAR(128) NOT NULL,
    state VARCHAR(64) NOT NULL,
    postal_code VARCHAR(32) NOT NULL,
    country VARCHAR(64) NOT NULL DEFAULT 'US',
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_customer_addresses_tenant_id ON customer_addresses (tenant_id);
CREATE INDEX IF NOT EXISTS ix_customer_addresses_customer_id ON customer_addresses (customer_id);

CREATE TABLE IF NOT EXISTS identity_links (
    identity_link_id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(128) NOT NULL,
    customer_id VARCHAR(36) NOT NULL,
    provider VARCHAR(128) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_identity_links_tenant_id ON identity_links (tenant_id);
CREATE INDEX IF NOT EXISTS ix_identity_links_customer_id ON identity_links (customer_id);
CREATE INDEX IF NOT EXISTS ix_identity_links_provider ON identity_links (provider);
CREATE INDEX IF NOT EXISTS ix_identity_links_subject ON identity_links (subject);

CREATE TABLE IF NOT EXISTS customer_events (
    event_id VARCHAR(36) PRIMARY KEY,
    event_type VARCHAR(128) NOT NULL,
    aggregate_id VARCHAR(128) NOT NULL,
    actor_id VARCHAR(128) NOT NULL DEFAULT 'system',
    payload JSON NOT NULL,
    published_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_customer_events_event_type ON customer_events (event_type);
CREATE INDEX IF NOT EXISTS ix_customer_events_aggregate_id ON customer_events (aggregate_id);
