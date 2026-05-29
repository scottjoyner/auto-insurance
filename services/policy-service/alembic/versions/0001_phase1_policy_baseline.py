"""phase1 policy baseline

Revision ID: 0001_policy_phase1
Revises:
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_policy_phase1"
down_revision = None
branch_labels = None
depends_on = None

json_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "bind_requests",
        sa.Column("bind_request_id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=True),
        sa.Column("customer_id", sa.String(length=128), nullable=True),
        sa.Column("quote_id", sa.String(length=36), nullable=False),
        sa.Column("policy_id", sa.String(length=36), nullable=False),
        sa.Column("request_key", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending_approval"),
        sa.Column("bind_method", sa.String(length=64), nullable=False, server_default="human_approval"),
        sa.Column("total_premium", sa.Float(), nullable=False, server_default="0"),
        sa.Column("effective_date", sa.DateTime(), nullable=False),
        sa.Column("expiration_date", sa.DateTime(), nullable=False),
        sa.Column("quote_snapshot", json_type, nullable=False),
        sa.Column("risk_assessment_snapshot", json_type, nullable=False),
        sa.Column("created_by_actor_id", sa.String(length=128), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_bind_requests_quote_id", "bind_requests", ["quote_id"])
    op.create_index("ix_bind_requests_policy_id", "bind_requests", ["policy_id"])
    op.create_index("ix_bind_requests_request_key", "bind_requests", ["request_key"])
    op.create_index("ix_bind_requests_status", "bind_requests", ["status"])
    op.create_index("ix_bind_requests_tenant_customer", "bind_requests", ["tenant_id", "customer_id"])

    op.create_table(
        "bind_approvals",
        sa.Column("approval_id", sa.String(length=36), primary_key=True),
        sa.Column("bind_request_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("approver_actor_id", sa.String(length=128), nullable=True),
        sa.Column("comments", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("decided_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_bind_approvals_bind_request_id", "bind_approvals", ["bind_request_id"])
    op.create_index("ix_bind_approvals_status", "bind_approvals", ["status"])

    op.create_table(
        "policies",
        sa.Column("policy_id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=True),
        sa.Column("customer_id", sa.String(length=128), nullable=True),
        sa.Column("quote_id", sa.String(length=36), nullable=False),
        sa.Column("bind_request_id", sa.String(length=36), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("total_premium", sa.Float(), nullable=False, server_default="0"),
        sa.Column("effective_date", sa.DateTime(), nullable=False),
        sa.Column("expiration_date", sa.DateTime(), nullable=False),
        sa.Column("bind_packet", json_type, nullable=False),
        sa.Column("bound_by_actor_id", sa.String(length=128), nullable=False, server_default="system"),
        sa.Column("bound_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_policies_quote_id", "policies", ["quote_id"])
    op.create_index("ix_policies_bind_request_id", "policies", ["bind_request_id"])
    op.create_index("ix_policies_state", "policies", ["state"])
    op.create_index("ix_policies_tenant_customer", "policies", ["tenant_id", "customer_id"])

    op.create_table(
        "policy_events",
        sa.Column("event_id", sa.String(length=36), primary_key=True),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("aggregate_id", sa.String(length=36), nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=False, server_default="system"),
        sa.Column("payload", json_type, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_policy_events_event_type", "policy_events", ["event_type"])
    op.create_index("ix_policy_events_aggregate_id", "policy_events", ["aggregate_id"])


def downgrade() -> None:
    op.drop_index("ix_policy_events_aggregate_id", table_name="policy_events")
    op.drop_index("ix_policy_events_event_type", table_name="policy_events")
    op.drop_table("policy_events")
    op.drop_index("ix_policies_tenant_customer", table_name="policies")
    op.drop_index("ix_policies_state", table_name="policies")
    op.drop_index("ix_policies_bind_request_id", table_name="policies")
    op.drop_index("ix_policies_quote_id", table_name="policies")
    op.drop_table("policies")
    op.drop_index("ix_bind_approvals_status", table_name="bind_approvals")
    op.drop_index("ix_bind_approvals_bind_request_id", table_name="bind_approvals")
    op.drop_table("bind_approvals")
    op.drop_index("ix_bind_requests_tenant_customer", table_name="bind_requests")
    op.drop_index("ix_bind_requests_status", table_name="bind_requests")
    op.drop_index("ix_bind_requests_request_key", table_name="bind_requests")
    op.drop_index("ix_bind_requests_policy_id", table_name="bind_requests")
    op.drop_index("ix_bind_requests_quote_id", table_name="bind_requests")
    op.drop_table("bind_requests")
