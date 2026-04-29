"""add trigger function for updated_at column

Revision ID: e58d7bcecb23
Revises: cb125f73b43c
Create Date: 2026-04-29 14:58:23.497113

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e58d7bcecb23"
down_revision: Union[str, Sequence[str], None] = "cb125f73b43c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
      NEW.updated_at = NOW() AT TIME ZONE 'UTC';
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
