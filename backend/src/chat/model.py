from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, Enum as SAEnum, String

from src.postgres.base import UUIDBase
from src.postgres.types import created_at
from src.user.model import UserOrm

from uuid import UUID
import enum

class ChatType(enum.Enum):
    DIRECT = "direct"
    GROUP = "group"

class ChatMemberOrm(UUIDBase):
    """Many to many relationship"""
    __tablename__ = 'chats_members'
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)

    created_at: Mapped[created_at]



    __table_args__ = (
        UniqueConstraint('chat_id', 'user_id', name = "uq_chat_member"),
    )

class ChatOrm(UUIDBase):
    """Chats Table"""
    __tablename__ = 'chats'
    
    
    name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(nullable=True)

    owner_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    type: Mapped[ChatType] = mapped_column(SAEnum(ChatType), nullable=False)

    created_at: Mapped[created_at]

    members: Mapped[list["UserOrm"]] = relationship( back_populates="chats", secondary="chats_members")

class ChatMessageOrm(UUIDBase):
    """Chats messages"""
    __tablename__ = 'chats_messages'

    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    content: Mapped[str] = mapped_column(String(1000))

    created_at: Mapped[created_at]

