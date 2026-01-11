"""remove_unnecessary_fields

Revision ID: 9f0d7140b47a
Revises: 030e3ac5aa78
Create Date: 2026-01-09 21:36:36.104580

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f0d7140b47a'
down_revision: Union[str, Sequence[str], None] = '030e3ac5aa78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove unnecessary fields from models."""
    # Remove is_active from prompts table
    op.drop_column('prompts', 'is_active')

    # Remove is_default from settings table
    op.drop_column('settings', 'is_default')

    # Remove status from tools table
    op.drop_column('tools', 'status')


def downgrade() -> None:
    """Add back unnecessary fields."""
    # Add back is_active to prompts table
    op.add_column('prompts', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))
    op.create_index('ix_prompts_is_active', 'prompts', ['is_active'])

    # Add back is_default to settings table
    op.add_column('settings', sa.Column('is_default', sa.Boolean(), nullable=False, server_default='0'))
    op.create_index('ix_settings_is_default', 'settings', ['is_default'])

    # Add back status to tools table
    op.add_column('tools', sa.Column('status', sa.String(), nullable=False, server_default='active'))
