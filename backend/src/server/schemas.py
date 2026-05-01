from datetime import datetime
from uuid import UUID

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
