from datetime import datetime
from uuid import UUID

from pydantic import Field, model_validator

from src.chat.enums import ChatMemberRole, ChatType
from src.core.schemas.base_schema import BaseSchema


class ChatSchema(BaseSchema):
    id: UUID
    type: ChatType
    name: str | None
    description: str | None
    owner_id: UUID | None
    image_url: str | None
    is_archived: bool
    created_at: datetime
    updated_at: datetime


class ChatMemberSchema(BaseSchema):
    chat_id: UUID
    user_id: UUID
    role: ChatMemberRole
    last_read_seq: int
    joined_at: datetime
    left_at: datetime | None


class MemberCreateSchema(BaseSchema):
    user_id: UUID
    chat_id: UUID
    role: ChatMemberRole | None = ChatMemberRole.member


class ChatCreateSchema(BaseSchema):
    owner_id: UUID | None = None
    type: ChatType
    name: str | None = None
    description: str | None = None


class ChatCreateRequestSchema(BaseSchema):
    type: ChatType
    target_user_id: UUID | None = None
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=300)
    member_ids: list[UUID] | None = None

    @model_validator(mode="after")
    def validate_conditional_fields(self) -> ChatCreateRequestSchema:
        if self.type == ChatType.private:
            if self.target_user_id is None:
                raise ValueError("'target_user_id' is required when type is 'private'.")
            if self.name is not None:
                raise ValueError("'name' is only allowed for group chats.")
            if self.description is not None:
                raise ValueError("'description' is only allowed for group chats.")
            if self.member_ids is not None:
                raise ValueError("'member_ids' is only allowed for group chats.")

        elif self.type == ChatType.group:
            if self.name is None:
                raise ValueError("'name' is required when type is 'group'.")
            if self.target_user_id is not None:
                raise ValueError("'target_user_id' is only allowed for private chats.")

        return self
