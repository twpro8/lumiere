from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas.base_schema import BaseSchema
from src.chat.models import ChatMemberOrm, ChatOrm
from src.chat.enums import ChatMemberRole
from src.core.postgres import UUIDBase
from src.chat.schemas import ChatSchema, MemberSchema, CreateChatSchema

class BaseRepository[schemaT: BaseSchema, modelT: UUIDBase]:
    schema: type[schemaT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _validate(self, obj: modelT) -> schemaT:
        return self.schema.model_validate(obj)

    def _validate_many(self, objs: list[modelT]) -> list[schemaT]:
        return [self.schema.model_validate(obj) for obj in objs]


class ChatRepository(BaseRepository[ChatSchema, ChatOrm]):
    schema = ChatSchema

    async def create_group_chat(self, data: CreateChatSchema, owner_id: UUID) -> ChatSchema:
        """Creates a new group chat in the database"""

        chat = ChatOrm(**data.model_dump(exclude={"members"}), owner_id=owner_id)
        self.session.add(chat)
        await self.session.flush()

        return self._validate(chat)


class MemberRepository(BaseRepository[MemberSchema, ChatMemberOrm]):
    schema = MemberSchema

    async def add_member(self, user_id: UUID, chat_id: UUID, role: ChatMemberRole) -> MemberSchema:
        """Creates a new member with the given user_id and chat_id"""

        member = ChatMemberOrm(user_id=user_id, chat_id=chat_id, role=role)
        self.session.add(member)
        await self.session.flush()

        return self._validate(member)

    async def add_members(self, members: list[UUID], chat_id: UUID, owner_id: UUID) -> None:
        """Create list of new members with the given user_id and chat_id"""

        orm_members = [ChatMemberOrm(user_id=user_id, chat_id=chat_id, role=ChatMemberRole.member)
                   for user_id in members]
        orm_members.append(ChatMemberOrm(user_id=owner_id, chat_id=chat_id, role=ChatMemberRole.owner))

        self.session.add_all(orm_members)
        await self.session.flush()
