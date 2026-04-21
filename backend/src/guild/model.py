from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.postgres.base import UUIDBase
from src.postgres.types import str_128, created_at


class GuildOrm(UUIDBase):
    __tablename__ = "guilds"

    name: Mapped[str_128]
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    icon_url: Mapped[str_128 | None]
    created_at: Mapped[created_at]
