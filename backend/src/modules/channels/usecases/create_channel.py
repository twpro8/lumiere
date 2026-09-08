from dataclasses import asdict
from uuid import UUID

from src.core.logging import get_logger
from src.core.realtime import EventType, RealtimeNotifier
from src.core.realtime.rooms import server_room
from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelCreate, channel_to_dto
from src.modules.channels.domain.enums import ChannelType
from src.modules.channels.domain.exceptions import ChannelConflictError
from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.servers.public.facade import ServersFacade

logger = get_logger(__name__)


class CreateChannelUseCase:
    def __init__(
        self,
        channel_repository: ChannelRepository,
        realtime_notifier: RealtimeNotifier | None = None,
        servers_facade: ServersFacade | None = None,
    ) -> None:
        self._channels = channel_repository
        self._servers = servers_facade
        self._realtime = realtime_notifier

    async def __call__(
        self,
        *,
        server_id: UUID,
        name: str,
        user_id: UUID | None = None,
        channel_type: ChannelType = ChannelType.text,
        topic: str | None = None,
        is_private: bool = False,
    ) -> Channel:
        if self._servers is not None:
            if user_id is None:
                raise ValueError("user_id is required when servers_facade is provided")
            await self._servers.assert_is_server_owner(user_id, server_id)
        name = name.strip()
        existing = await self._channels.find_by_name(server_id, name)
        if existing is not None:
            raise ChannelConflictError
        max_pos = await self._channels.max_position_by_server(server_id)
        channel_data = ChannelCreate(
            server_id=server_id,
            name=name,
            type=channel_type,
            position=max_pos + 1,
            topic=topic,
            is_private=is_private,
        )
        channel = await self._channels.create(channel_data)
        await self._notify(server_id, channel)
        return channel

    async def _notify(self, server_id: UUID, channel: Channel) -> None:
        if self._realtime is not None:
            try:
                await self._realtime.publish_to_room(
                    room=server_room(server_id),
                    event_type=EventType.CHANNEL_CREATED,
                    payload=asdict(channel_to_dto(channel)),
                )
            except Exception:
                logger.exception("realtime.publish_failed", server_id=str(server_id))
