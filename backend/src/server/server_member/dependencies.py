from typing import Annotated, AsyncGenerator

from fastapi import Depends


from src.core.dependencies import SessionDep
from src.server.server_member.repository import ServerMemberRepository
from src.server.server_member.service import ServerMemberService
from src.server.server_member.unit_of_work import ServerMemberUnitOfWork


def get_server_member_repository(
    session: SessionDep,
) -> ServerMemberRepository:
    return ServerMemberRepository(session=session)


def get_server_member_service(
    session: SessionDep,
    server_member_unit_of_work: ServerMemberUnitOfWorkDep,
) -> ServerMemberService:
    return ServerMemberService(
        session=session,
        server_member_unit_of_work=server_member_unit_of_work,
    )


async def get_server_member_unit_of_work(
    session: SessionDep,
    server_member_repository: ServerMemberRepositoryDep,
) -> AsyncGenerator[ServerMemberUnitOfWork]:
    async with ServerMemberUnitOfWork(
        session, server_member_repository
    ) as server_member_unit_of_work:
        yield server_member_unit_of_work


ServerMemberRepositoryDep = Annotated[
    ServerMemberRepository, Depends(get_server_member_repository)
]
ServerMemberServiceDep = Annotated[
    ServerMemberService, Depends(get_server_member_service)
]
ServerMemberUnitOfWorkDep = Annotated[
    ServerMemberUnitOfWork, Depends(get_server_member_unit_of_work)
]
