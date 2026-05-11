from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services import BaseService
from src.server.enums import ServerMemberRole
from src.server.server_member.repository import ServerMemberRepository
from src.server.server_member.schemas import (
    ServerMemberCreateSchema,
    ServerMemberSchema,
)


class ServerMemberService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        server_member_repository: ServerMemberRepository,
    ) -> None:
        super().__init__(session)
        self.server_member_repository = server_member_repository

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

        member = await self.server_member_repository.create(member_data)

        if is_commit:
            await self.session.commit()

        return member
