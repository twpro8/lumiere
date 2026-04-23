from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.postgres import UUIDBase
from src.core.postgres import str_128, created_at


class UserOrm(UUIDBase):
    __tablename__ = "users"

    name: Mapped[str_128]
    username: Mapped[str_128] = mapped_column(unique=True)
    email: Mapped[str_128] = mapped_column(unique=True)
    password_hash: Mapped[str_128]
    avatar_url: Mapped[str_128 | None]
    created_at: Mapped[created_at]

    chats: Mapped[list["ChatOrm"]] = relationship(back_populates="members", secondary="chats_members")