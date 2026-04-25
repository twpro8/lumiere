"""
Aggregates all ORM models into a single module.

This module ensures that all model classes are imported and registered
in SQLAlchemy's metadata. It is primarily used by Alembic during
autogeneration, so that all tables are discovered correctly.

Do not remove or bypass these imports unless you update Alembic's
model discovery logic accordingly.
"""

from src.user.model import UserOrm
from src.guild.model import GuildOrm
from src.channel.model import ChannelOrm
from src.message.model import MessageOrm

__all__ = [
    "UserOrm",
    "GuildOrm",
    "ChannelOrm",
    "MessageOrm",
]
