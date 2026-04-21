from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.postgres.base import UUIDBase
from src.postgres.types import str_1024, uuid_pk, created_at


class MessageOrm(UUIDBase):
    __tablename__ = "messages"

    channel_id: Mapped[UUID] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE")
    )
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content: Mapped[str_1024]
    created_at: Mapped[created_at]
