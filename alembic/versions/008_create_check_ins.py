"""Create check_ins table.

Revision ID: 008
Revises: 007
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "check_ins",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("instance_stop_id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("checked_in_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("rating", sa.SmallInteger(), nullable=True),
        sa.ForeignKeyConstraint(["instance_stop_id"], ["instance_stops.id"], name="fk_check_ins_instance_stop", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_check_ins_user", ondelete="CASCADE"),
        sa.UniqueConstraint("instance_stop_id", name="uq_check_ins_instance_stop"),
        sa.CheckConstraint("rating IS NULL OR (rating >= 1 AND rating <= 5)", name="chk_check_ins_rating"),
    )
    
    # Indexes for leaderboard and feed queries
    op.create_index("idx_check_ins_user_checked_in_at", "check_ins", ["user_id", sa.text("checked_in_at DESC")])
    op.create_index("idx_check_ins_checked_in_at", "check_ins", [sa.text("checked_in_at DESC")])


def downgrade() -> None:
    op.drop_index("idx_check_ins_checked_in_at", table_name="check_ins")
    op.drop_index("idx_check_ins_user_checked_in_at", table_name="check_ins")
    op.drop_table("check_ins")
