import uuid
from uuid import UUID

import pytest
from sqlalchemy import select

from src.chat.models import ChatOrm, ChatMemberOrm
from src.chat.enums import ChatMemberRole


async def test_chat_has_fields(ac_auth, session, create_chat, create_chat_data):
    """Check that the fields are working as expected."""

    query = await session.execute(select(ChatOrm).where(ChatOrm.id == create_chat["id"]))
    chat = query.scalar_one()

    assert chat.name == create_chat_data["name"]
    assert chat.description == create_chat_data["description"]
    assert chat.owner_id is not None


async def test_chat_has_members(ac_auth, session, create_chat):
    """Chek that the members are created correctly."""

    chat_id = UUID(create_chat["id"])

    query = await session.execute(select(ChatMemberOrm).where(ChatMemberOrm.chat_id == chat_id))
    members = query.scalars().all()

    assert all(m.chat_id == chat_id for m in members)
    assert len(members) == 3


async def test_chat_has_owner(ac_auth, session, create_chat):
    """Chek that the owner is created correctly."""

    chat_id = UUID(create_chat["id"])

    data = await ac_auth.get("/users/me")
    assert data.status_code == 200
    user_id = UUID(data.json().get("id"))

    query = await session.execute(select(ChatMemberOrm).where(ChatMemberOrm.user_id == user_id, ChatMemberOrm.chat_id == chat_id))
    owner = query.scalar_one_or_none()

    assert owner.role == ChatMemberRole.owner


async def test_empty_json_returns_422(ac_auth, create_chat_data):
    """Check that we can't create chat with empty JSON."""

    response = await ac_auth.post("/chats", json={})
    assert response.status_code == 422


@pytest.mark.parametrize("members_count", [1, 10])
async def test_members_validation(ac_auth, create_chat_data, members_count):
    payload = {**create_chat_data, "members": [str(uuid.uuid4()) for _ in range(members_count)]}
    response = await ac_auth.post("/chats", json=payload)
    assert response.status_code == 422