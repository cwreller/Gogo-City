"""Add cities table and link to route_templates.

Revision ID: 009
Revises: 008
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create cities table
    op.create_table(
        "cities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("country", sa.String(100), nullable=False, server_default="USA"),
        sa.Column("lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    
    # Add unique constraint on name + state + country
    op.create_unique_constraint("uq_cities_name_state_country", "cities", ["name", "state", "country"])
    
    # Add index for lookups
    op.create_index("idx_cities_name", "cities", ["name"])
    
    # Add city_id column to route_templates
    op.add_column("route_templates", sa.Column("city_id", UUID(as_uuid=True), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        "fk_route_templates_city",
        "route_templates",
        "cities",
        ["city_id"],
        ["id"],
        ondelete="SET NULL",
    )
    
    # Add index on city_id
    op.create_index("idx_route_templates_city_id", "route_templates", ["city_id"])
    
    # Drop old city varchar column
    op.drop_column("route_templates", "city")
    
    # Also drop city column from route_instances (it was a snapshot, but we can reference via template)
    op.drop_column("route_instances", "city")


def downgrade() -> None:
    # Add back city column to route_instances
    op.add_column("route_instances", sa.Column("city", sa.String(100), nullable=True))
    
    # Add back city column to route_templates
    op.add_column("route_templates", sa.Column("city", sa.String(100), nullable=True))
    
    # Drop index and foreign key
    op.drop_index("idx_route_templates_city_id", table_name="route_templates")
    op.drop_constraint("fk_route_templates_city", "route_templates", type_="foreignkey")
    
    # Drop city_id column
    op.drop_column("route_templates", "city_id")
    
    # Drop cities table
    op.drop_index("idx_cities_name", table_name="cities")
    op.drop_constraint("uq_cities_name_state_country", "cities", type_="unique")
    op.drop_table("cities")
