"""add_xp_columns

Revision ID: fc4f0cf18fb4
Revises: 91953ef80d80
Create Date: 2026-02-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'fc4f0cf18fb4'
down_revision: Union[str, None] = '91953ef80d80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('curated_tasks', sa.Column('xp', sa.Integer(), server_default='0', nullable=False))
    op.add_column('template_tasks', sa.Column('xp', sa.Integer(), server_default='0', nullable=False))
    op.add_column('instance_tasks', sa.Column('xp', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('total_xp', sa.Integer(), server_default='0', nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'total_xp')
    op.drop_column('instance_tasks', 'xp')
    op.drop_column('template_tasks', 'xp')
    op.drop_column('curated_tasks', 'xp')
