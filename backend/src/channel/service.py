from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.channel.enums import ChannelType
from src.channel.repository import ChannelRepository
from src.channel.schemas import ChannelCreateSchema, ChannelSchema
from src.core.services.base_service import BaseService


class ChannelService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        channel_repository: ChannelRepository,
    ) -> None:
        super().__init__(session)
        self.channel_repository = channel_repository

    async def create_channel(
        self,
        server_id: UUID,
        name: str,
        type: ChannelType = ChannelType.text,
        topic: str | None = None,
        is_private: bool = False,
        is_commit: bool = True,
    ) -> ChannelSchema:

        channel_data = ChannelCreateSchema(
            server_id=server_id,
            name=name,
            type=type,
            position=0,
            topic=topic,
            is_private=is_private,
        )

        channel = await self.channel_repository.create(channel_data)
        if is_commit:
            await self.session.commit()

        return channel
