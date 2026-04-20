from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings

# TODO: configure pool size and max_overflow
engine = create_async_engine(str(settings.DATABASE_URL))
