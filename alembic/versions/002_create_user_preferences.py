"""Create user_preferences table.

Revision ID: 002
Revises: 001
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_preferences",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("budget_min_cents", sa.Integer(), nullable=True),
        sa.Column("budget_max_cents", sa.Integer(), nullable=True),
        sa.Column("max_distance_km", sa.Numeric(5, 2), nullable=True),
        sa.Column("preferred_start_time", sa.Time(), nullable=True),
        sa.Column("preferred_end_time", sa.Time(), nullable=True),
        sa.Column("vibe_tags", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("dietary_tags", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_preferences_user", ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_user_preferences_user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_preferences")
