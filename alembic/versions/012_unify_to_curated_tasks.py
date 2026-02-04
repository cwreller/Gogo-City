"""Unify curated_places into curated_tasks with location + task fields.

Revision ID: 012
Revises: 011
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old curated_places table
    op.drop_index("idx_curated_places_google_place_id", table_name="curated_places")
    op.drop_index("idx_curated_places_active", table_name="curated_places")
    op.drop_index("idx_curated_places_category", table_name="curated_places")
    op.drop_index("idx_curated_places_city_id", table_name="curated_places")
    op.drop_table("curated_places")
    
    # Create unified curated_tasks table
    op.create_table(
        "curated_tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("city_id", UUID(as_uuid=True), nullable=False),
        
        # Task identity
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        
        # Location fields (nullable - if null, task is locationless)
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("google_place_id", sa.String(255), nullable=True),
        
        # Task action fields (nullable - if null, just "visit the place")
        sa.Column("task_description", sa.Text(), nullable=True),  # "Eat hot chicken"
        sa.Column("verification_hint", sa.Text(), nullable=True),  # "Photo of you eating"
        
        # Verification type: gps, photo, both
        sa.Column("verification_type", sa.String(20), nullable=False, server_default="gps"),
        
        # Categorization for AI matching
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("vibe_tags", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("dietary_tags", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("price_level", sa.SmallInteger(), nullable=True),
        
        # Curated content
        sa.Column("best_for", sa.Text(), nullable=True),
        sa.Column("pro_tips", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        
        # Time/availability
        sa.Column("best_times", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("avg_duration_minutes", sa.Integer(), nullable=True),
        
        # Admin
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"], name="fk_curated_tasks_city", ondelete="CASCADE"),
        sa.CheckConstraint(
            "verification_type IN ('gps', 'photo', 'both')",
            name="chk_curated_tasks_verification_type"
        ),
    )
    
    # Indexes for curated_tasks
    op.create_index("idx_curated_tasks_city_id", "curated_tasks", ["city_id"])
    op.create_index("idx_curated_tasks_category", "curated_tasks", ["category"])
    op.create_index("idx_curated_tasks_verification_type", "curated_tasks", ["verification_type"])
    op.create_index(
        "idx_curated_tasks_active", 
        "curated_tasks", 
        ["city_id", "is_active"], 
        postgresql_where=sa.text("is_active = true")
    )


def downgrade() -> None:
    # Drop curated_tasks
    op.drop_index("idx_curated_tasks_active", table_name="curated_tasks")
    op.drop_index("idx_curated_tasks_verification_type", table_name="curated_tasks")
    op.drop_index("idx_curated_tasks_category", table_name="curated_tasks")
    op.drop_index("idx_curated_tasks_city_id", table_name="curated_tasks")
    op.drop_table("curated_tasks")
    
    # Recreate curated_places (simplified version for rollback)
    op.create_table(
        "curated_places",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("city_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("lat", sa.Numeric(10, 7), nullable=False),
        sa.Column("lng", sa.Numeric(10, 7), nullable=False),
        sa.Column("google_place_id", sa.String(255), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("vibe_tags", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("dietary_tags", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("price_level", sa.SmallInteger(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("best_for", sa.Text(), nullable=True),
        sa.Column("pro_tips", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("best_times", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("avg_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"], name="fk_curated_places_city", ondelete="CASCADE"),
    )
    op.create_index("idx_curated_places_city_id", "curated_places", ["city_id"])
    op.create_index("idx_curated_places_category", "curated_places", ["category"])
    op.create_index(
        "idx_curated_places_active", 
        "curated_places", 
        ["city_id", "is_active"], 
        postgresql_where=sa.text("is_active = true")
    )
    op.create_index(
        "idx_curated_places_google_place_id", 
        "curated_places", 
        ["google_place_id"], 
        postgresql_where=sa.text("google_place_id IS NOT NULL")
    )
