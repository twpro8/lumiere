from sqlalchemy.ext.asyncio import AsyncSession

from src.core.unit_of_work.base_unit_of_work import BaseUnitOfWork
from src.server.server_member.repository import ServerMemberRepository


class ServerMemberUnitOfWork(BaseUnitOfWork):
    server_members: ServerMemberRepository

    def __init__(
        self,
        session: AsyncSession,
        server_member_repository: ServerMemberRepository,
    ) -> None:
        super().__init__(session)
        self.server_members = server_member_repository

    def _uow_marker(self) -> None: ...
