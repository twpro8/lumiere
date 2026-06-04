from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services import BaseService
from src.server.enums import ServerMemberRole
from src.server.schemas import (
    ServerCreateRequestSchema,
    ServerCreateSchema,
    ServerSchema,
    ServerUpdateRequestSchema,
    ServerUpdateSchema,
)
from src.channel.service import ChannelService
from src.server.server_member.service import ServerMemberService
from src.server.exceptions import (
    ServerNotFoundError,
    ServerNotEmptyError,
)
from src.server.unit_of_work import ServerUnitOfWork


class ServerService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        server_unit_of_work: ServerUnitOfWork,
        channel_service: ChannelService,
        server_member_service: ServerMemberService,
    ) -> None:
        super().__init__(session)
        self.uow = server_unit_of_work
        self.channel_service = channel_service
        self.server_member_service = server_member_service

    async def create_server(
        self,
        server_data: ServerCreateRequestSchema,
        owner_id: UUID,
    ) -> ServerSchema:
        # Creating server
        _server_data = ServerCreateSchema(**server_data.model_dump(), owner_id=owner_id)
        server = await self.uow.servers.create(_server_data)

        # Adding owner to server members
        await self.server_member_service.create_member(
            user_id=owner_id,
            server_id=server.id,
            role=ServerMemberRole.owner,
            is_commit=False,
        )

        # Creating general channel for server
        await self.channel_service.create_channel(
            server.id,
            name="general",
            is_commit=False,
        )

        await self.uow.commit()
        return server

    async def update_server(
        self,
        update_data: ServerUpdateRequestSchema,
        server_id: UUID,
        owner_id: UUID,
    ) -> ServerSchema:
        server = await self.uow.servers.get_one(id=server_id, owner_id=owner_id)
        if not server:
            raise ServerNotFoundError

        _update_data = ServerUpdateSchema(
            **update_data.model_dump(),
            id=server.id,
            owner_id=owner_id,
        )
        updated_server = await self.uow.servers.update(server.id, _update_data)

        await self.uow.commit()
        return updated_server

    async def delete_server(
        self,
        server_id: UUID,
        owner_id: UUID,
    ) -> None:
        server = await self.uow.servers.get_one(id=server_id, owner_id=owner_id)
        if not server:
            raise ServerNotFoundError

        if server.member_count > 1:
            raise ServerNotEmptyError

        await self.uow.servers.delete(server.id)
        await self.uow.commit()
