import uuid
from typing import TYPE_CHECKING, List
from datetime import datetime

from sqlalchemy import ForeignKey, UUID, UniqueConstraint, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.postgres import UUIDBase, str_128, str_512, timestamp
from src.server.enums import ServerMemberRole

if TYPE_CHECKING:
    from src.user.models import UserOrm


class ServerOrm(UUIDBase):
    __tablename__ = "servers"

    name: Mapped[str_128]
    description: Mapped[str_512 | None]
    icon_url: Mapped[str_512 | None]
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    member_count: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[timestamp]
    # Make sure you have added the trigger to the migration.
    updated_at: Mapped[timestamp]
    owner: Mapped["UserOrm"] = relationship("UserOrm", back_populates="owned_servers")
    members: Mapped[List["ServerMemberOrm"]] = relationship(
        "ServerMemberOrm", back_populates="server"
    )


class ServerMemberOrm(UUIDBase):
    __tablename__ = "server_members"
    __table_args__ = (
        UniqueConstraint("server_id", "user_id", name="uq_server_members_server_user"),
        Index("ix_server_members_server_id", "server_id"),
        Index("ix_server_members_user_id", "user_id"),
    )

    server_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("servers.id", ondelete="CASCADE"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    role: Mapped[str_128] = mapped_column(default=ServerMemberRole.member)
    joined_at: Mapped[timestamp]
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    server: Mapped["ServerOrm"] = relationship("ServerOrm", back_populates="members")
    user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="joined_servers")


class ServerInviteOrm(UUIDBase):
    __tablename__ = "server_invites"

    server_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("servers.id"),
        index=True,
    )
    code: Mapped[str_128] = mapped_column(unique=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    max_uses: Mapped[int | None]
    use_count: Mapped[int] = mapped_column(default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[timestamp]
