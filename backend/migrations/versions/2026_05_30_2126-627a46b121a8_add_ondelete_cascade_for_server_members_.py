"""add ondelete cascade for server_members table

Revision ID: 627a46b121a8
Revises: 55756ee31fac
Create Date: 2026-05-30 21:26:26.337448

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "627a46b121a8"
down_revision: Union[str, Sequence[str], None] = "55756ee31fac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        op.f("server_members_user_id_fkey"),
        "server_members",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("server_members_server_id_fkey"),
        "server_members",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_server_members_server_id_servers",
        "server_members",
        "servers",
        ["server_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_server_members_user_id_users",
        "server_members",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_server_members_user_id_users", "server_members", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_server_members_server_id_servers",
        "server_members",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("server_members_server_id_fkey"),
        "server_members",
        "servers",
        ["server_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("server_members_user_id_fkey"),
        "server_members",
        "users",
        ["user_id"],
        ["id"],
    )
