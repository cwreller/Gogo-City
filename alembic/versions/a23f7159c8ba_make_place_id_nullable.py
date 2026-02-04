"""make_place_id_nullable

Revision ID: a23f7159c8ba
Revises: 013_rename_stops_to_tasks
Create Date: 2026-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a23f7159c8ba'
down_revision: Union[str, None] = '013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make place_id nullable in template_tasks and instance_tasks
    op.alter_column('template_tasks', 'place_id',
                    existing_type=sa.String(255),
                    nullable=True)
    op.alter_column('instance_tasks', 'place_id',
                    existing_type=sa.String(255),
                    nullable=True)


def downgrade() -> None:
    op.alter_column('template_tasks', 'place_id',
                    existing_type=sa.String(255),
                    nullable=False)
    op.alter_column('instance_tasks', 'place_id',
                    existing_type=sa.String(255),
                    nullable=False)
