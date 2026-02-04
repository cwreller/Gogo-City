"""Create places_cache table.

Revision ID: 003
Revises: 002
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "places_cache",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("place_id", sa.String(255), nullable=False),
        sa.Column("provider", sa.String(50), server_default="google", nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("lat", sa.Numeric(10, 7), nullable=False),
        sa.Column("lng", sa.Numeric(10, 7), nullable=False),
        sa.Column("place_types", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("price_level", sa.SmallInteger(), nullable=True),
        sa.Column("rating", sa.Numeric(2, 1), nullable=True),
        sa.Column("rating_count", sa.Integer(), nullable=True),
        sa.Column("photo_references", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("raw_data", JSONB(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), server_default=sa.text("now() + interval '30 days'"), nullable=False),
        sa.UniqueConstraint("place_id", "provider", name="uq_places_cache_place_provider"),
    )
    
    # Indexes
    op.create_index("idx_places_cache_place_id", "places_cache", ["place_id"])
    op.create_index("idx_places_cache_expires_at", "places_cache", ["expires_at"])


def downgrade() -> None:
    op.drop_index("idx_places_cache_expires_at", table_name="places_cache")
    op.drop_index("idx_places_cache_place_id", table_name="places_cache")
    op.drop_table("places_cache")
