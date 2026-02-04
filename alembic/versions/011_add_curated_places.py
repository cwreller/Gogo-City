"""Add curated_places table for manually curated city places.

Revision ID: 011
Revises: 010
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "curated_places",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("city_id", UUID(as_uuid=True), nullable=False),
        
        # Place identification
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("lat", sa.Numeric(10, 7), nullable=False),
        sa.Column("lng", sa.Numeric(10, 7), nullable=False),
        
        # Optional Google Places link (for navigation, hours, etc.)
        sa.Column("google_place_id", sa.String(255), nullable=True),
        
        # Categorization for AI matching
        sa.Column("category", sa.String(50), nullable=False),  # restaurant, bar, coffee, activity, etc.
        sa.Column("vibe_tags", ARRAY(sa.String()), server_default="{}", nullable=False),  # chill, lively, romantic, etc.
        sa.Column("dietary_tags", ARRAY(sa.String()), server_default="{}", nullable=False),  # vegan, gluten-free, etc.
        sa.Column("price_level", sa.SmallInteger(), nullable=True),  # 1-4 (your own assessment)
        
        # Curated content
        sa.Column("description", sa.Text(), nullable=True),  # Your notes about the place
        sa.Column("best_for", sa.Text(), nullable=True),  # "great for groups", "date spot", etc.
        sa.Column("pro_tips", sa.Text(), nullable=True),  # "get the spicy chicken", "sit on the patio"
        sa.Column("photo_url", sa.Text(), nullable=True),
        
        # Time/availability hints
        sa.Column("best_times", ARRAY(sa.String()), server_default="{}", nullable=False),  # morning, afternoon, evening, late_night
        sa.Column("avg_duration_minutes", sa.Integer(), nullable=True),  # how long people typically spend
        
        # Admin
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"], name="fk_curated_places_city", ondelete="CASCADE"),
    )
    
    # Indexes
    op.create_index("idx_curated_places_city_id", "curated_places", ["city_id"])
    op.create_index("idx_curated_places_category", "curated_places", ["category"])
    op.create_index("idx_curated_places_active", "curated_places", ["city_id", "is_active"], postgresql_where=sa.text("is_active = true"))
    op.create_index("idx_curated_places_google_place_id", "curated_places", ["google_place_id"], postgresql_where=sa.text("google_place_id IS NOT NULL"))


def downgrade() -> None:
    op.drop_index("idx_curated_places_google_place_id", table_name="curated_places")
    op.drop_index("idx_curated_places_active", table_name="curated_places")
    op.drop_index("idx_curated_places_category", table_name="curated_places")
    op.drop_index("idx_curated_places_city_id", table_name="curated_places")
    op.drop_table("curated_places")
