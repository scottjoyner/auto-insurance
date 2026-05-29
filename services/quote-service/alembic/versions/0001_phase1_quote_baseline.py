"""phase1 quote baseline

Revision ID: 0001_quote_phase1
Revises:
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_quote_phase1"
down_revision = None
branch_labels = None
depends_on = None

json_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "quotes",
        sa.Column("quote_id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=True),
        sa.Column("customer_id", sa.String(length=128), nullable=True),
        sa.Column("product_id", sa.String(length=128), nullable=False),
        sa.Column("product_version", sa.String(length=64), nullable=False),
        sa.Column("jurisdiction", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("total_premium", sa.Float(), nullable=False, server_default="0"),
        sa.Column("coverages", json_type, nullable=False),
        sa.Column("reason_codes", json_type, nullable=False),
        sa.Column("surcharges_applied", json_type, nullable=False),
        sa.Column("discounts_applied", json_type, nullable=False),
        sa.Column("bind_eligible", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("referral_flag", sa.String(length=64), nullable=False, server_default="none"),
        sa.Column("referral_reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("rating_result_hash", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("input_snapshot_hash", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("ai_confidence_score", sa.Float(), nullable=True),
        sa.Column("applicant_data", json_type, nullable=False),
        sa.Column("created_by_actor_id", sa.String(length=128), nullable=False, server_default="system"),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_quotes_tenant_customer", "quotes", ["tenant_id", "customer_id"])
    op.create_index("ix_quotes_product_status", "quotes", ["product_id", "status"])

    op.create_table(
        "quote_versions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("quote_id", sa.String(length=36), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False, server_default="created"),
        sa.Column("quote_snapshot", json_type, nullable=False),
        sa.Column("input_snapshot_hash", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("rating_result_hash", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("created_by_actor_id", sa.String(length=128), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ux_quote_versions_quote_version", "quote_versions", ["quote_id", "version_number"], unique=True)

    op.create_table(
        "quote_status_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("quote_id", sa.String(length=36), nullable=False),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("actor_id", sa.String(length=128), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "quote_events",
        sa.Column("event_id", sa.String(length=64), primary_key=True),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("aggregate_id", sa.String(length=36), nullable=False),
        sa.Column("aggregate_type", sa.String(length=64), nullable=False, server_default="quote"),
        sa.Column("actor_id", sa.String(length=128), nullable=False, server_default="system"),
        sa.Column("payload", json_type, nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "quote_rating_traces",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("quote_id", sa.String(length=36), nullable=False),
        sa.Column("rating_result_hash", sa.String(length=128), nullable=False),
        sa.Column("input_snapshot_hash", sa.String(length=128), nullable=False),
        sa.Column("trace", json_type, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("quote_rating_traces")
    op.drop_table("quote_events")
    op.drop_table("quote_status_history")
    op.drop_index("ux_quote_versions_quote_version", table_name="quote_versions")
    op.drop_table("quote_versions")
    op.drop_index("ix_quotes_product_status", table_name="quotes")
    op.drop_index("ix_quotes_tenant_customer", table_name="quotes")
    op.drop_table("quotes")
