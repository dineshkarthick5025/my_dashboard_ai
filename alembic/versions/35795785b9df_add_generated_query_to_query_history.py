"""Add generated_query and rename config to llm_config in query_history

Revision ID: 35795785b9df
Revises: ea05d55b0153
Create Date: 2025-06-24 23:24:17.877669

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35795785b9df'
down_revision: Union[str, Sequence[str], None] = 'ea05d55b0153'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('query_history', sa.Column('generated_query', sa.Text(), nullable=True))
    op.alter_column('query_history', 'config', new_column_name='llm_config')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('query_history', 'llm_config', new_column_name='config')
    op.drop_column('query_history', 'generated_query')

