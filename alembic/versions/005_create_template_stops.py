"""Create template_stops table.

Revision ID: 005
Revises: 004
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "template_stops",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("template_id", UUID(as_uuid=True), nullable=False),
        sa.Column("place_id", sa.String(255), nullable=False),
        sa.Column("provider", sa.String(50), server_default="google", nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("lat", sa.Numeric(10, 7), nullable=False),
        sa.Column("lng", sa.Numeric(10, 7), nullable=False),
        sa.Column("place_types", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["template_id"], ["route_templates.id"], name="fk_template_stops_template", ondelete="CASCADE"),
    )
    
    # Indexes
    op.create_index("idx_template_stops_template_id", "template_stops", ["template_id"])
    op.create_index("idx_template_stops_place_id", "template_stops", ["place_id"])


def downgrade() -> None:
    op.drop_index("idx_template_stops_place_id", table_name="template_stops")
    op.drop_index("idx_template_stops_template_id", table_name="template_stops")
    op.drop_table("template_stops")
