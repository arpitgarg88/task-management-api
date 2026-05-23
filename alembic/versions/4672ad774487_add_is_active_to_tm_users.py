"""add is_active to tm_users

Revision ID: 4672ad774487
Revises: 9d65b189db27
Create Date: 2026-05-23 12:22:04.178023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4672ad774487'
down_revision: Union[str, Sequence[str], None] = '9d65b189db27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # tm_tasks.status -> NOT NULL
    op.alter_column(
        'tm_tasks',
        'status',
        existing_type=postgresql.ENUM(
            'PENDING',
            'IN_PROGRESS',
            'COMPLETED',
            'CANCELLED',
            name='taskstatus'
        ),
        nullable=False
    )

    # Add is_active safely for existing rows
    op.add_column(
        'tm_users',
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        )
    )

    # tm_users.role -> NOT NULL
    op.alter_column(
        'tm_users',
        'role',
        existing_type=postgresql.ENUM(
            'ADMIN',
            'USER',
            'MANAGER',
            name='userrole'
        ),
        nullable=False
    )

    # Optional: remove DB default after migration
    op.alter_column('tm_users', 'is_active', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        'tm_users',
        'role',
        existing_type=postgresql.ENUM(
            'ADMIN',
            'USER',
            'MANAGER',
            name='userrole'
        ),
        nullable=True
    )

    op.drop_column('tm_users', 'is_active')

    op.alter_column(
        'tm_tasks',
        'status',
        existing_type=postgresql.ENUM(
            'PENDING',
            'IN_PROGRESS',
            'COMPLETED',
            'CANCELLED',
            name='taskstatus'
        ),
        nullable=True
    )