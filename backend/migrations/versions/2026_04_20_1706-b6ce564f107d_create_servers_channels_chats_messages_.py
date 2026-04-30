"""create servers, channels, chats, messages and association tables

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
        "chats",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("type", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=True),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("owner_id", sa.UUID(), nullable=True),
        sa.Column("image_url", sa.String(length=512), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chats_owner_id"), "chats", ["owner_id"], unique=False)
    op.create_table(
        "servers",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("icon_url", sa.String(length=512), nullable=True),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("member_count", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_servers_owner_id"), "servers", ["owner_id"], unique=False)
    op.create_table(
        "channels",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("server_id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("topic", sa.String(length=1024), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("is_private", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["server_id"], ["servers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("server_id", "name", name="uq_channels_server_name"),
    )
    op.create_index("ix_channels_server_id", "channels", ["server_id"], unique=False)
    op.create_table(
        "chat_members",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("chat_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(length=128), nullable=False),
        sa.Column("last_read_seq", sa.Integer(), nullable=False),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["chat_id"],
            ["chats.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chat_id", "user_id", name="uq_chat_members_chat_user"),
    )
    op.create_index(
        "ix_chat_members_chat_id", "chat_members", ["chat_id"], unique=False
    )
    op.create_index(
        "ix_chat_members_user_id", "chat_members", ["user_id"], unique=False
    )
    op.create_table(
        "server_invites",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("server_id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("max_uses", sa.Integer(), nullable=True),
        sa.Column("use_count", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["server_id"],
            ["servers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(
        op.f("ix_server_invites_server_id"),
        "server_invites",
        ["server_id"],
        unique=False,
    )
    op.create_table(
        "server_members",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("server_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(length=128), nullable=False),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["server_id"],
            ["servers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "server_id", "user_id", name="uq_server_members_server_user"
        ),
    )
    op.create_index(
        "ix_server_members_server_id",
        "server_members",
        ["server_id"],
        unique=False,
    )
    op.create_index(
        "ix_server_members_user_id",
        "server_members",
        ["user_id"],
        unique=False,
    )
    op.create_table(
        "messages",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("chat_id", sa.UUID(), nullable=True),
        sa.Column("channel_id", sa.UUID(), nullable=True),
        sa.Column("sender_id", sa.UUID(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.UUID(), nullable=True),
        sa.Column("is_edited", sa.Boolean(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(chat_id IS NULL) != (channel_id IS NULL)",
            name="ck_messages_single_context",
        ),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chat_id"], ["chats.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["messages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_messages_channel_id"),
        "messages",
        ["channel_id"],
        unique=False,
    )
    op.create_index(op.f("ix_messages_chat_id"), "messages", ["chat_id"], unique=False)
    op.create_index(
        op.f("ix_messages_sender_id"), "messages", ["sender_id"], unique=False
    )
    op.create_index(
        "uq_messages_channel_sequence",
        "messages",
        ["channel_id", "sequence"],
        unique=True,
        postgresql_where="channel_id IS NOT NULL",
    )
    op.create_index(
        "uq_messages_chat_sequence",
        "messages",
        ["chat_id", "sequence"],
        unique=True,
        postgresql_where="chat_id IS NOT NULL",
    )
    op.execute(sa.text("""
        CREATE TRIGGER update_servers_updated_at
        BEFORE UPDATE ON servers
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """))
    op.execute(sa.text("""
        CREATE TRIGGER update_channels_updated_at
        BEFORE UPDATE ON channels
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """))
    op.execute(sa.text("""
        CREATE TRIGGER update_chats_updated_at
        BEFORE UPDATE ON chats
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """))
    op.execute(sa.text("""
        CREATE TRIGGER update_messages_updated_at
        BEFORE UPDATE ON messages
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS update_messages_updated_at ON messages;")
    op.execute("DROP TRIGGER IF EXISTS update_chats_updated_at ON chats;")
    op.execute("DROP TRIGGER IF EXISTS update_channels_updated_at ON channels;")
    op.execute("DROP TRIGGER IF EXISTS update_servers_updated_at ON servers;")
    op.drop_index(
        "uq_messages_chat_sequence",
        table_name="messages",
        postgresql_where="chat_id IS NOT NULL",
    )
    op.drop_index(
        "uq_messages_channel_sequence",
        table_name="messages",
        postgresql_where="channel_id IS NOT NULL",
    )
    op.drop_index(op.f("ix_messages_sender_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_chat_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_channel_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index("ix_server_members_user_id", table_name="server_members")
    op.drop_index("ix_server_members_server_id", table_name="server_members")
    op.drop_table("server_members")
    op.drop_index(op.f("ix_server_invites_server_id"), table_name="server_invites")
    op.drop_table("server_invites")
    op.drop_index("ix_chat_members_user_id", table_name="chat_members")
    op.drop_index("ix_chat_members_chat_id", table_name="chat_members")
    op.drop_table("chat_members")
    op.drop_index("ix_channels_server_id", table_name="channels")
    op.drop_table("channels")
    op.drop_index(op.f("ix_servers_owner_id"), table_name="servers")
    op.drop_table("servers")
    op.drop_index(op.f("ix_chats_owner_id"), table_name="chats")
    op.drop_table("chats")
