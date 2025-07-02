"""Add Query History table

Revision ID: ea05d55b0153
Revises: fd7ba0c5b57d
Create Date: 2025-06-24 23:08:46.144093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea05d55b0153'
down_revision: Union[str, Sequence[str], None] = 'fd7ba0c5b57d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'query_history',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),  # e.g., 'success' or 'failed'
        sa.Column('config', sa.JSON(), nullable=True),     # store LLM config if success
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('query_history')
