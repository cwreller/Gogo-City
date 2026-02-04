"""Create instance_stops table.

Revision ID: 007
Revises: 006
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "instance_stops",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("instance_id", UUID(as_uuid=True), nullable=False),
        sa.Column("source_template_stop_id", UUID(as_uuid=True), nullable=True),
        sa.Column("place_id", sa.String(255), nullable=False),
        sa.Column("provider", sa.String(50), server_default="google", nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("lat", sa.Numeric(10, 7), nullable=False),
        sa.Column("lng", sa.Numeric(10, 7), nullable=False),
        sa.Column("place_types", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["instance_id"], ["route_instances.id"], name="fk_instance_stops_instance", ondelete="CASCADE"),
    )
    
    # Indexes
    op.create_index("idx_instance_stops_instance_id", "instance_stops", ["instance_id"])


def downgrade() -> None:
    op.drop_index("idx_instance_stops_instance_id", table_name="instance_stops")
    op.drop_table("instance_stops")
