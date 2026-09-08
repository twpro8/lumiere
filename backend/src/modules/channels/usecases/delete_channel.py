from dataclasses import asdict
from uuid import UUID

from src.core.logging import get_logger
from src.core.realtime import EventType, RealtimeNotifier
from src.core.realtime.rooms import server_room
from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import channel_to_dto
from src.modules.channels.domain.exceptions import (
    ChannelNotFoundError,
    OnlyChannelDeletionError,
)
from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.servers.public.facade import ServersFacade

logger = get_logger(__name__)


class DeleteChannelUseCase:
    def __init__(
        self,
        channel_repository: ChannelRepository,
        servers_facade: ServersFacade,
        realtime_notifier: RealtimeNotifier,
    ) -> None:
        self._channels = channel_repository
        self._servers_facade = servers_facade
        self._realtime = realtime_notifier

    async def __call__(
        self, *, channel_id: UUID, user_id: UUID, server_id: UUID
    ) -> None:
        channel = await self._channels.get_by_id(channel_id)
        if channel is None:
            raise ChannelNotFoundError
        if channel.server_id != server_id:
            raise ChannelNotFoundError

        await self._servers_facade.assert_is_server_owner(user_id, channel.server_id)

        if await self._channels.count_by_server(channel.server_id) <= 1:
            raise OnlyChannelDeletionError

        await self._channels.delete(channel.id)
        await self._notify(server_id, channel)

    async def _notify(self, server_id: UUID, channel: Channel) -> None:
        try:
            await self._realtime.publish_to_room(
                room=server_room(server_id),
                event_type=EventType.CHANNEL_DELETED,
                payload=asdict(channel_to_dto(channel)),
            )
        except Exception:
            logger.exception("realtime.publish_failed", server_id=str(server_id))
