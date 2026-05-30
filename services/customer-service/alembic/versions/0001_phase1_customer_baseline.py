"""phase1 customer baseline

Revision ID: 0001_customer_phase1
Revises:
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_customer_phase1"
down_revision = None
branch_labels = None
depends_on = None

json_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("tenant_id", sa.String(length=128), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="active"),
        sa.Column("metadata_json", json_type, nullable=False),
        sa.Column("created_by_actor_id", sa.String(length=128), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_tenants_status", "tenants", ["status"])

    op.create_table(
        "accounts",
        sa.Column("account_id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("account_type", sa.String(length=64), nullable=False, server_default="personal"),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="active"),
        sa.Column("created_by_actor_id", sa.String(length=128), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_accounts_tenant_id", "accounts", ["tenant_id"])
    op.create_index("ix_accounts_status", "accounts", ["status"])

    op.create_table(
        "customers",
        sa.Column("customer_id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("account_id", sa.String(length=36), nullable=False),
        sa.Column("first_name", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("last_name", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="active"),
        sa.Column("created_by_actor_id", sa.String(length=128), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_customers_tenant_id", "customers", ["tenant_id"])
    op.create_index("ix_customers_account_id", "customers", ["account_id"])
    op.create_index("ix_customers_display_name", "customers", ["display_name"])
    op.create_index("ix_customers_status", "customers", ["status"])

    op.create_table(
        "customer_contacts",
        sa.Column("contact_id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("contact_type", sa.String(length=64), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_customer_contacts_tenant_id", "customer_contacts", ["tenant_id"])
    op.create_index("ix_customer_contacts_customer_id", "customer_contacts", ["customer_id"])

    op.create_table(
        "customer_addresses",
        sa.Column("address_id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("address_type", sa.String(length=64), nullable=False, server_default="mailing"),
        sa.Column("line1", sa.String(length=255), nullable=False),
        sa.Column("line2", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("city", sa.String(length=128), nullable=False),
        sa.Column("state", sa.String(length=64), nullable=False),
        sa.Column("postal_code", sa.String(length=32), nullable=False),
        sa.Column("country", sa.String(length=64), nullable=False, server_default="US"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_customer_addresses_tenant_id", "customer_addresses", ["tenant_id"])
    op.create_index("ix_customer_addresses_customer_id", "customer_addresses", ["customer_id"])

    op.create_table(
        "identity_links",
        sa.Column("identity_link_id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=128), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_identity_links_tenant_id", "identity_links", ["tenant_id"])
    op.create_index("ix_identity_links_customer_id", "identity_links", ["customer_id"])
    op.create_index("ix_identity_links_provider", "identity_links", ["provider"])
    op.create_index("ix_identity_links_subject", "identity_links", ["subject"])

    op.create_table(
        "customer_events",
        sa.Column("event_id", sa.String(length=36), primary_key=True),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("aggregate_id", sa.String(length=128), nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=False, server_default="system"),
        sa.Column("payload", json_type, nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_customer_events_event_type", "customer_events", ["event_type"])
    op.create_index("ix_customer_events_aggregate_id", "customer_events", ["aggregate_id"])


def downgrade() -> None:
    op.drop_index("ix_customer_events_aggregate_id", table_name="customer_events")
    op.drop_index("ix_customer_events_event_type", table_name="customer_events")
    op.drop_table("customer_events")
    op.drop_index("ix_identity_links_subject", table_name="identity_links")
    op.drop_index("ix_identity_links_provider", table_name="identity_links")
    op.drop_index("ix_identity_links_customer_id", table_name="identity_links")
    op.drop_index("ix_identity_links_tenant_id", table_name="identity_links")
    op.drop_table("identity_links")
    op.drop_index("ix_customer_addresses_customer_id", table_name="customer_addresses")
    op.drop_index("ix_customer_addresses_tenant_id", table_name="customer_addresses")
    op.drop_table("customer_addresses")
    op.drop_index("ix_customer_contacts_customer_id", table_name="customer_contacts")
    op.drop_index("ix_customer_contacts_tenant_id", table_name="customer_contacts")
    op.drop_table("customer_contacts")
    op.drop_index("ix_customers_status", table_name="customers")
    op.drop_index("ix_customers_display_name", table_name="customers")
    op.drop_index("ix_customers_account_id", table_name="customers")
    op.drop_index("ix_customers_tenant_id", table_name="customers")
    op.drop_table("customers")
    op.drop_index("ix_accounts_status", table_name="accounts")
    op.drop_index("ix_accounts_tenant_id", table_name="accounts")
    op.drop_table("accounts")
    op.drop_index("ix_tenants_status", table_name="tenants")
    op.drop_table("tenants")
