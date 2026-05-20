from typing import Annotated

from fastapi import Depends


from src.core.dependencies import SessionDep
from src.server.server_member.repository import ServerMemberRepository
from src.server.server_member.service import ServerMemberService


def get_server_member_repository(
    session: SessionDep,
) -> ServerMemberRepository:
    return ServerMemberRepository(session=session)


def get_server_member_service(
    session: SessionDep,
    server_member_repository: ServerMemberRepositoryDep,
) -> ServerMemberService:
    return ServerMemberService(
        session=session,
        server_member_repository=server_member_repository,
    )


ServerMemberRepositoryDep = Annotated[
    ServerMemberRepository, Depends(get_server_member_repository)
]
ServerMemberServiceDep = Annotated[
    ServerMemberService, Depends(get_server_member_service)
]
