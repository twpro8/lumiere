from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.postgres.base import UUIDBase
from src.postgres.types import str_128, uuid_pk


class ChannelOrm(UUIDBase):
    __tablename__ = "channels"

    guild_id: Mapped[UUID] = mapped_column(ForeignKey("guilds.id", ondelete="CASCADE"))
    name: Mapped[str_128]
    type: Mapped[str_128]
    position: Mapped[int]
