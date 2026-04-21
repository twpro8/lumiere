from sqlalchemy.orm import DeclarativeBase

from src.postgres.mixins import UUIDMixin


class Base(DeclarativeBase):
    pass


class UUIDBase(UUIDMixin, Base):
    __abstract__ = True
