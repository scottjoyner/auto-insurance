"""phase1 risk baseline

Revision ID: 0001_risk_phase1
Revises:
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_risk_phase1"
down_revision = None
branch_labels = None
depends_on = None

json_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "risk_policy_versions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("effective_date", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("policy_data", json_type, nullable=False),
        sa.Column("submitted_by_actor_id", sa.String(length=128), nullable=True),
        sa.Column("approved_by_actor_id", sa.String(length=128), nullable=True),
        sa.Column("activated_by_actor_id", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("activated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_risk_policy_versions_status", "risk_policy_versions", ["status"])
    op.create_index("ix_risk_policy_versions_version", "risk_policy_versions", ["version"])

    op.create_table(
        "risk_policy_approvals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("policy_version_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_risk_policy_approvals_policy_version_id", "risk_policy_approvals", ["policy_version_id"])

    op.create_table(
        "risk_assessments",
        sa.Column("assessment_id", sa.String(length=36), primary_key=True),
        sa.Column("quote_id", sa.String(length=36), nullable=False),
        sa.Column("policy_version", sa.String(length=64), nullable=False),
        sa.Column("decision", sa.String(length=64), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("risk_level", sa.String(length=32), nullable=False, server_default="LOW"),
        sa.Column("quote_data", json_type, nullable=False),
        sa.Column("portfolio_state", json_type, nullable=False),
        sa.Column("assessment_payload", json_type, nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=False, server_default="system"),
        sa.Column("assessed_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_risk_assessments_quote_id", "risk_assessments", ["quote_id"])
    op.create_index("ix_risk_assessments_policy_version", "risk_assessments", ["policy_version"])
    op.create_index("ix_risk_assessments_decision", "risk_assessments", ["decision"])


def downgrade() -> None:
    op.drop_index("ix_risk_assessments_decision", table_name="risk_assessments")
    op.drop_index("ix_risk_assessments_policy_version", table_name="risk_assessments")
    op.drop_index("ix_risk_assessments_quote_id", table_name="risk_assessments")
    op.drop_table("risk_assessments")
    op.drop_index("ix_risk_policy_approvals_policy_version_id", table_name="risk_policy_approvals")
    op.drop_table("risk_policy_approvals")
    op.drop_index("ix_risk_policy_versions_version", table_name="risk_policy_versions")
    op.drop_index("ix_risk_policy_versions_status", table_name="risk_policy_versions")
    op.drop_table("risk_policy_versions")
