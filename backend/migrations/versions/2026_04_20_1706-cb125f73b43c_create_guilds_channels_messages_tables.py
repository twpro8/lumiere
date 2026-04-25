"""create guilds, channels, messages tables

Revision ID: cb125f73b43c
Revises: 2ecc3fe6c712
Create Date: 2026-04-20 17:06:29.860228

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "cb125f73b43c"
down_revision: Union[str, Sequence[str], None] = "2ecc3fe6c712"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "guilds",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("icon_url", sa.String(length=128), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "channels",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("guild_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("type", sa.String(length=128), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["guild_id"], ["guilds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "messages",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("channel_id", sa.UUID(), nullable=False),
        sa.Column("author_id", sa.UUID(), nullable=False),
        sa.Column("content", sa.String(length=1024), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("messages")
    op.drop_table("channels")
    op.drop_table("guilds")
