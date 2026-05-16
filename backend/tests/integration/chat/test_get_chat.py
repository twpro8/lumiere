async def test_get_chat_unauthorized_returns_401(ac, create_chat):
    response = await ac.get(f"/chats/{create_chat['id']}")
    assert response.status_code == 401
