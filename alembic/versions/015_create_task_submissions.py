"""Create task_submissions table for user-submitted tasks.

Revision ID: 015
Revises: fc4f0cf18fb4
Create Date: 2026-03-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID

revision: str = "015"
down_revision: Union[str, None] = "fc4f0cf18fb4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "task_submissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("submitted_by", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("city_id", UUID(as_uuid=True), sa.ForeignKey("cities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("address", sa.Text),
        sa.Column("lat", sa.Numeric(10, 7)),
        sa.Column("lng", sa.Numeric(10, 7)),
        sa.Column("task_description", sa.Text),
        sa.Column("verification_hint", sa.Text),
        sa.Column("verification_type", sa.String(20), nullable=False, server_default="photo"),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("vibe_tags", ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("price_level", sa.SmallInteger),
        sa.Column("avg_duration_minutes", sa.Integer),
        sa.Column("pro_tips", sa.Text),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reviewed_by", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("rejection_reason", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="chk_task_submissions_status"),
        sa.CheckConstraint("verification_type IN ('gps', 'photo', 'both')", name="chk_task_submissions_verification_type"),
    )
    op.create_index("ix_task_submissions_status", "task_submissions", ["status"])
    op.create_index("ix_task_submissions_submitted_by", "task_submissions", ["submitted_by"])


def downgrade() -> None:
    op.drop_index("ix_task_submissions_submitted_by")
    op.drop_index("ix_task_submissions_status")
    op.drop_table("task_submissions")
