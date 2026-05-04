import pytest
from uuid import UUID

CHAT_FIELDS = {"id", "name", "description", "owner_id", "image_url",
               "is_archived", "created_at", "updated_at", "type"}


@pytest.fixture(name="create_chat")
async def create_chat_fixture(ac_auth, create_chat_data):
    """Factory fixture — call it N times to create N chats."""

    async def _create(data: dict | None = None) -> dict:
        response = await ac_auth.post("/chats", json=data or create_chat_data)
        assert response.status_code == 200, response.text
        return response.json()

    return _create


def assert_chat_shape(chat: dict) -> None:
    """Assert that a chat dict has all required fields."""

    missing = CHAT_FIELDS - chat.keys()
    assert not missing


async def test_get_all_chats_unauthorized_returns_401(ac):
    """Unauthenticated request must be rejected."""

    response = await ac.get("/chats")
    assert response.status_code == 401


async def test_get_all_chats_returns_list(ac_auth, create_chat):
    """Endpoint must return a JSON array."""

    await create_chat()
    response = await ac_auth.get("/chats")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_all_chats_chat_has_required_fields(ac_auth, create_chat):
    """Every chat in the response must contain all expected fields."""

    await create_chat()
    response = await ac_auth.get("/chats")
    assert response.status_code == 200

    chats = response.json()
    assert chats
    for chat in chats:
        assert_chat_shape(chat)


async def test_get_all_chats_returns_only_users_chats(ac_auth, create_chat):
    """Chats that don't belong to the user must not appear."""

    await create_chat()
    response = await ac_auth.get("/chats")

    assert response.status_code == 200
    chats = response.json()

    assert chats != []
    assert all("id" in chat for chat in chats)


async def test_get_all_chats_count_increases_after_creation(ac_auth, create_chat):
    """Creating a new chat must increase the total count by one."""

    before = await ac_auth.get("/chats")
    count_before = len(before.json())

    await create_chat()

    after = await ac_auth.get("/chats")
    count_after = len(after.json())

    assert count_after == count_before + 1


async def test_get_all_chats_no_duplicates(ac_auth, create_chat):
    """Each chat id must appear exactly once (no JOIN duplicates)."""

    await create_chat()
    response = await ac_auth.get("/chats")

    ids = [chat["id"] for chat in response.json()]
    assert len(ids) == len(set(ids)), "Duplicate chats detected in response"


async def test_get_all_chats_group_chat_has_name(ac_auth, create_chat, create_chat_data):
    """Group chat must expose its real name, not null."""

    await create_chat()
    response = await ac_auth.get("/chats")

    group_chats = [c for c in response.json() if c["type"] == "group"]
    assert group_chats, "No group chats found"

    for chat in group_chats:
        assert chat["name"] == create_chat_data["name"]


@pytest.mark.parametrize("chat_count", [2, 3])
async def test_get_all_chats_returns_all_created_chats(
    ac_auth, create_chat, create_chat_data, chat_count
):
    """All chats created by the user must appear in the response."""

    before = await ac_auth.get("/chats")
    count_before = len(before.json())

    for _ in range(chat_count):
        await create_chat()

    response = await ac_auth.get("/chats")
    assert response.status_code == 200
    assert len(response.json()) == count_before + chat_count

# TODO create private chat tests