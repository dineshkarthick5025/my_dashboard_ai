"""Add dashboards table

Revision ID: fd7ba0c5b57d
Revises: 3581cd380d25
Create Date: 2025-06-24 14:24:23.609412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd7ba0c5b57d'
down_revision: Union[str, Sequence[str], None] = '3581cd380d25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'dashboards',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('data', sa.Text(), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('dashboards')

