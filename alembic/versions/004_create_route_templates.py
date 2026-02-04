"""Create route_templates table.

Revision ID: 004
Revises: 003
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "route_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("author_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("share_code", sa.String(20), nullable=True),
        sa.Column("is_public", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("estimated_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("estimated_budget_cents", sa.Integer(), nullable=True),
        sa.Column("vibe_tags", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], name="fk_route_templates_author", ondelete="CASCADE"),
        sa.UniqueConstraint("share_code", name="uq_route_templates_share_code"),
    )
    
    # Indexes
    op.create_index("idx_route_templates_author_id", "route_templates", ["author_id"])
    op.create_index(
        "idx_route_templates_public", 
        "route_templates", 
        ["city", "created_at"],
        postgresql_where=sa.text("is_public = true"),
    )


def downgrade() -> None:
    op.drop_index("idx_route_templates_public", table_name="route_templates")
    op.drop_index("idx_route_templates_author_id", table_name="route_templates")
    op.drop_table("route_templates")
