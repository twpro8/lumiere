from typing import Annotated

from fastapi import Depends
from src.core.dependencies import SessionDep
from src.channel.repository import ChannelRepository
from src.channel.service import ChannelService


def get_channel_repository(
    session: SessionDep,
) -> ChannelRepository:
    return ChannelRepository(session=session)


def get_channel_service(
    session: SessionDep,
    channel_repository: ChannelRepositoryDep,
) -> ChannelService:
    return ChannelService(
        session=session,
        channel_repository=channel_repository,
    )


ChannelRepositoryDep = Annotated[ChannelRepository, Depends(get_channel_repository)]
ChannelServiceDep = Annotated[ChannelService, Depends(get_channel_service)]
