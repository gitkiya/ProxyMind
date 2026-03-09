"""add a content col

Revision ID: 2c780ba5d14d
Revises: 4d0e77409b7a
Create Date: 2026-03-04 21:26:40.478850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c780ba5d14d'
down_revision: Union[str, Sequence[str], None] = '4d0e77409b7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
