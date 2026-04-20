from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.postgres.base import Base
from src.postgres.types import str_128, uuid_pk, created_at


class GuildOrm(Base):
    __tablename__ = "guilds"

    id: Mapped[uuid_pk]
    name: Mapped[str_128]
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    icon_url: Mapped[str_128 | None]
    created_at: Mapped[created_at]
