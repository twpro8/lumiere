from sqlalchemy.orm import Mapped, mapped_column

from src.postgres.base import Base
from src.postgres.types import uuid_pk, str_128, created_at


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    name: Mapped[str_128]
    username: Mapped[str_128] = mapped_column(unique=True)
    email: Mapped[str_128] = mapped_column(unique=True)
    password_hash: Mapped[str_128]
    avatar_url: Mapped[str_128 | None]
    created_at: Mapped[created_at]
