from typing import Annotated, AsyncGenerator

from fastapi import Depends

from src.channel.dependencies import ChannelServiceDep
from src.core.dependencies import SessionDep
from src.server.repository import ServerRepository
from src.server.server_member.dependencies import ServerMemberServiceDep
from src.server.service import ServerService
from src.server.unit_of_work import ServerUnitOfWork


def get_server_repository(
    session: SessionDep,
) -> ServerRepository:
    return ServerRepository(session=session)


def get_server_service(
    session: SessionDep,
    server_unit_of_work: ServerUnitOfWorkDep,
    channel_service: ChannelServiceDep,
    server_member_service: ServerMemberServiceDep,
) -> ServerService:
    return ServerService(
        session=session,
        server_unit_of_work=server_unit_of_work,
        channel_service=channel_service,
        server_member_service=server_member_service,
    )


async def get_server_unit_of_work(
    session: SessionDep,
    server_repository: ServerRepositoryDep,
) -> AsyncGenerator[ServerUnitOfWork]:
    async with ServerUnitOfWork(session, server_repository) as server_unit_of_work:
        yield server_unit_of_work


ServerRepositoryDep = Annotated[ServerRepository, Depends(get_server_repository)]
ServerServiceDep = Annotated[ServerService, Depends(get_server_service)]
ServerUnitOfWorkDep = Annotated[ServerUnitOfWork, Depends(get_server_unit_of_work)]
