from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services import BaseService
from src.server.enums import ServerMemberRole
from src.server.server_member.schemas import (
    ServerMemberCreateSchema,
    ServerMemberSchema,
)
from src.server.server_member.unit_of_work import ServerMemberUnitOfWork


class ServerMemberService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        server_member_unit_of_work: ServerMemberUnitOfWork,
    ) -> None:
        super().__init__(session)
        self.uow = server_member_unit_of_work

    async def create_member(
        self,
        user_id: UUID,
        server_id: UUID,
        role: ServerMemberRole = ServerMemberRole.member,
        is_commit: bool = True,
    ) -> ServerMemberSchema:
        member_data = ServerMemberCreateSchema(
            server_id=server_id,
            user_id=user_id,
            role=role,
        )

        member = await self.uow.server_members.create(member_data)
        if is_commit:
            await self.uow.commit()

        return member
