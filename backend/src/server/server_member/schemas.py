from uuid import UUID

from src.core.schemas.base_schema import BaseSchema
from src.server.enums import ServerMemberRole


class ServerMemberSchema(BaseSchema):
    server_id: UUID
    user_id: UUID
    role: ServerMemberRole


class ServerMemberCreateSchema(BaseSchema):
    server_id: UUID
    user_id: UUID
    role: ServerMemberRole = ServerMemberRole.member
