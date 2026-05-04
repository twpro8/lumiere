import pytest


@pytest.fixture(name="create_chat_data")
async def create_chat_data(ac_auth):

    return {
      "type": "group",
      "name": "string",
      "description": "string",
      "image_url": "string",
      "members": [
        "c08386e7-bbab-43b4-8427-d296390a3e1e",
    "1df5569d-c4bf-488e-9f0f-30946a7067c9"
]}


@pytest.fixture(name="create_chat")
async def create_chat(ac_auth, create_chat_data):
    response = await ac_auth.post("/chats", json=create_chat_data)
    assert response.status_code == 200
    return response.json()