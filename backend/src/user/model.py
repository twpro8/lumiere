from sqlalchemy.orm import Mapped, mapped_column
from src.postgres.base import UUIDBase
from src.postgres.types import str_128, created_at


class UserOrm(UUIDBase):
    __tablename__ = "users"

    name: Mapped[str_128]
    username: Mapped[str_128] = mapped_column(unique=True)
    email: Mapped[str_128] = mapped_column(unique=True)
    password_hash: Mapped[str_128]
    avatar_url: Mapped[str_128 | None]
    created_at: Mapped[created_at]
