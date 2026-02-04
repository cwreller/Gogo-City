"""Create route_instances table.

Revision ID: 006
Revises: 005
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "route_instances",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("source_template_id", UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_route_instances_user", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_template_id"], ["route_templates.id"], name="fk_route_instances_template", ondelete="SET NULL"),
        sa.CheckConstraint("status IN ('active', 'completed', 'archived')", name="chk_route_instances_status"),
    )
    
    # Indexes
    op.create_index("idx_route_instances_user_id_status", "route_instances", ["user_id", "status"])
    op.create_index(
        "idx_route_instances_source_template_id", 
        "route_instances", 
        ["source_template_id"],
        postgresql_where=sa.text("source_template_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("idx_route_instances_source_template_id", table_name="route_instances")
    op.drop_index("idx_route_instances_user_id_status", table_name="route_instances")
    op.drop_table("route_instances")
