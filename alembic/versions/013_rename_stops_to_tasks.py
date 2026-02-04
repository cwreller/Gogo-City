"""Rename template_stops to template_tasks, instance_stops to instance_tasks.

Revision ID: 013
Revises: 012
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename template_stops -> template_tasks
    op.rename_table("template_stops", "template_tasks")
    
    # Rename the index
    op.drop_index("idx_template_stops_template_id", table_name="template_tasks")
    op.drop_index("idx_template_stops_place_id", table_name="template_tasks")
    op.create_index("idx_template_tasks_template_id", "template_tasks", ["template_id"])
    
    # Rename the foreign key constraint
    op.drop_constraint("fk_template_stops_template", "template_tasks", type_="foreignkey")
    op.create_foreign_key(
        "fk_template_tasks_template",
        "template_tasks",
        "route_templates",
        ["template_id"],
        ["id"],
        ondelete="CASCADE"
    )
    
    # Add new columns to template_tasks for task support
    op.add_column("template_tasks", sa.Column("task_description", sa.Text(), nullable=True))
    op.add_column("template_tasks", sa.Column("verification_hint", sa.Text(), nullable=True))
    op.add_column("template_tasks", sa.Column(
        "verification_type", 
        sa.String(20), 
        nullable=False, 
        server_default="gps"
    ))
    
    # Make lat/lng nullable (for locationless tasks)
    op.alter_column("template_tasks", "lat", nullable=True)
    op.alter_column("template_tasks", "lng", nullable=True)
    
    # Rename instance_stops -> instance_tasks
    op.rename_table("instance_stops", "instance_tasks")
    
    # Rename the index
    op.drop_index("idx_instance_stops_instance_id", table_name="instance_tasks")
    op.create_index("idx_instance_tasks_instance_id", "instance_tasks", ["instance_id"])
    
    # Rename the foreign key constraint
    op.drop_constraint("fk_instance_stops_instance", "instance_tasks", type_="foreignkey")
    op.create_foreign_key(
        "fk_instance_tasks_instance",
        "instance_tasks",
        "route_instances",
        ["instance_id"],
        ["id"],
        ondelete="CASCADE"
    )
    
    # Add new columns to instance_tasks for task support
    op.add_column("instance_tasks", sa.Column("task_description", sa.Text(), nullable=True))
    op.add_column("instance_tasks", sa.Column("verification_hint", sa.Text(), nullable=True))
    op.add_column("instance_tasks", sa.Column(
        "verification_type", 
        sa.String(20), 
        nullable=False, 
        server_default="gps"
    ))
    
    # Make lat/lng nullable (for locationless tasks)
    op.alter_column("instance_tasks", "lat", nullable=True)
    op.alter_column("instance_tasks", "lng", nullable=True)
    
    # Update check_ins: rename column and constraint
    op.alter_column("check_ins", "instance_stop_id", new_column_name="instance_task_id")
    op.drop_constraint("uq_check_ins_instance_stop", "check_ins", type_="unique")
    op.create_unique_constraint("uq_check_ins_instance_task", "check_ins", ["instance_task_id"])
    op.drop_constraint("fk_check_ins_instance_stop", "check_ins", type_="foreignkey")
    op.create_foreign_key(
        "fk_check_ins_instance_task",
        "check_ins",
        "instance_tasks",
        ["instance_task_id"],
        ["id"],
        ondelete="CASCADE"
    )
    
    # Add verified_by column to check_ins
    op.add_column("check_ins", sa.Column(
        "verified_by",
        sa.String(20),
        nullable=True  # null means not yet verified, or verification not required
    ))


def downgrade() -> None:
    # Remove verified_by from check_ins
    op.drop_column("check_ins", "verified_by")
    
    # Revert check_ins column rename
    op.drop_constraint("fk_check_ins_instance_task", "check_ins", type_="foreignkey")
    op.drop_constraint("uq_check_ins_instance_task", "check_ins", type_="unique")
    op.alter_column("check_ins", "instance_task_id", new_column_name="instance_stop_id")
    op.create_unique_constraint("uq_check_ins_instance_stop", "check_ins", ["instance_stop_id"])
    op.create_foreign_key(
        "fk_check_ins_instance_stop",
        "check_ins",
        "instance_tasks",  # table is still renamed at this point
        ["instance_stop_id"],
        ["id"],
        ondelete="CASCADE"
    )
    
    # Remove new columns from instance_tasks
    op.alter_column("instance_tasks", "lat", nullable=False)
    op.alter_column("instance_tasks", "lng", nullable=False)
    op.drop_column("instance_tasks", "verification_type")
    op.drop_column("instance_tasks", "verification_hint")
    op.drop_column("instance_tasks", "task_description")
    
    # Rename instance_tasks -> instance_stops
    op.drop_constraint("fk_instance_tasks_instance", "instance_tasks", type_="foreignkey")
    op.drop_index("idx_instance_tasks_instance_id", table_name="instance_tasks")
    op.rename_table("instance_tasks", "instance_stops")
    op.create_index("idx_instance_stops_instance_id", "instance_stops", ["instance_id"])
    op.create_foreign_key(
        "fk_instance_stops_instance",
        "instance_stops",
        "route_instances",
        ["instance_id"],
        ["id"],
        ondelete="CASCADE"
    )
    
    # Remove new columns from template_tasks
    op.alter_column("template_tasks", "lat", nullable=False)
    op.alter_column("template_tasks", "lng", nullable=False)
    op.drop_column("template_tasks", "verification_type")
    op.drop_column("template_tasks", "verification_hint")
    op.drop_column("template_tasks", "task_description")
    
    # Rename template_tasks -> template_stops
    op.drop_constraint("fk_template_tasks_template", "template_tasks", type_="foreignkey")
    op.drop_index("idx_template_tasks_template_id", table_name="template_tasks")
    op.rename_table("template_tasks", "template_stops")
    op.create_index("idx_template_stops_template_id", "template_stops", ["template_id"])
    op.create_index("idx_template_stops_place_id", "template_stops", ["place_id"])
    op.create_foreign_key(
        "fk_template_stops_template",
        "template_stops",
        "route_templates",
        ["template_id"],
        ["id"],
        ondelete="CASCADE"
    )
    
    # Fix check_ins FK to point to instance_stops
    op.drop_constraint("fk_check_ins_instance_stop", "check_ins", type_="foreignkey")
    op.create_foreign_key(
        "fk_check_ins_instance_stop",
        "check_ins",
        "instance_stops",
        ["instance_stop_id"],
        ["id"],
        ondelete="CASCADE"
    )
