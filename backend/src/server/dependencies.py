from typing import Annotated

from fastapi import Depends

from src.channel.dependencies import ChannelServiceDep
from src.core.dependencies import SessionDep
from src.server.repository import ServerRepository
from src.server.server_member.dependencies import ServerMemberServiceDep
from src.server.service import ServerService


def get_server_repository(
    session: SessionDep,
) -> ServerRepository:
    return ServerRepository(session=session)


def get_server_service(
    session: SessionDep,
    server_repository: ServerRepositoryDep,
    channel_service: ChannelServiceDep,
    server_member_service: ServerMemberServiceDep,
) -> ServerService:
    return ServerService(
        session=session,
        server_repository=server_repository,
        channel_service=channel_service,
        server_member_service=server_member_service,
    )


ServerRepositoryDep = Annotated[ServerRepository, Depends(get_server_repository)]
ServerServiceDep = Annotated[ServerService, Depends(get_server_service)]
