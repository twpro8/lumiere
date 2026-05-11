from datetime import datetime
from uuid import UUID

from pydantic import Field
from src.core.schemas import BaseSchema


class ServerSchema(BaseSchema):
    id: UUID
    name: str
    description: str | None
    icon_url: str | None
    owner_id: UUID
    member_count: int
    created_at: datetime
    updated_at: datetime


class ServerCreateRequestSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=300)
    icon_url: str | None


class ServerCreateSchema(ServerCreateRequestSchema):
    owner_id: UUID
