from uuid import uuid4

import pytest

from src.core.realtime.envelope import EventType
from src.core.realtime.rooms import server_room
from src.modules.channels.domain.enums import ChannelType
from src.modules.channels.domain.exceptions import ChannelConflictError
from src.modules.channels.usecases.create_channel import CreateChannelUseCase
from src.modules.servers.domain.entities.dtos import ServerCreate, ServerMemberCreate
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import NotServerOwnerError
from tests.unit.channels.fakes import (
    FakeChannelRepository,
    FakeRealtimeNotifier,
)
from tests.unit.servers.fakes import (
    FakeServerMemberRepository,
    FakeServerRepository,
    FakeServersFacade,
)


async def test_creates_channel() -> None:
    use_case = CreateChannelUseCase(FakeChannelRepository())
    server_id = uuid4()

    channel = await use_case(server_id=server_id, name="general")

    assert channel.server_id == server_id
    assert channel.name == "general"
    assert channel.type == ChannelType.text
    assert channel.is_private is False


async def test_position_increments() -> None:
    channels = FakeChannelRepository()
    use_case = CreateChannelUseCase(channels)
    server_id = uuid4()

    first = await use_case(server_id=server_id, name="first")
    second = await use_case(server_id=server_id, name="second")

    assert first.position == 1
    assert second.position == 2


async def test_duplicate_name_raises_conflict() -> None:
    channels = FakeChannelRepository()
    use_case = CreateChannelUseCase(channels)
    server_id = uuid4()

    await use_case(server_id=server_id, name="general")

    with pytest.raises(ChannelConflictError):
        await use_case(server_id=server_id, name="general")


async def test_same_name_in_different_servers_allowed() -> None:
    channels = FakeChannelRepository()
    use_case = CreateChannelUseCase(channels)

    await use_case(server_id=uuid4(), name="general")
    second = await use_case(server_id=uuid4(), name="general")

    assert second.name == "general"


async def test_owner_can_create() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    servers_facade = FakeServersFacade(server_members, servers)
    use_case = CreateChannelUseCase(channels, servers_facade=servers_facade)
    owner_id = uuid4()
    server = await servers.create(ServerCreate(name="Server", owner_id=owner_id))
    await server_members.create(
        ServerMemberCreate(
            server_id=server.id,
            user_id=owner_id,
            role=ServerMemberRole.owner,
        )
    )

    channel = await use_case(server_id=server.id, name="chat", user_id=owner_id)

    assert channel.name == "chat"
    assert channel.server_id == server.id


async def test_non_owner_cannot_create() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    servers_facade = FakeServersFacade(server_members, servers)
    use_case = CreateChannelUseCase(channels, servers_facade=servers_facade)
    owner_id, member_id = uuid4(), uuid4()
    server = await servers.create(ServerCreate(name="Server", owner_id=owner_id))
    await server_members.create(
        ServerMemberCreate(
            server_id=server.id,
            user_id=owner_id,
            role=ServerMemberRole.owner,
        )
    )
    await server_members.create(
        ServerMemberCreate(
            server_id=server.id,
            user_id=member_id,
            role=ServerMemberRole.member,
        )
    )

    with pytest.raises(NotServerOwnerError):
        await use_case(server_id=server.id, name="chat", user_id=member_id)


async def test_user_id_required_with_facade() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    servers_facade = FakeServersFacade(server_members, servers)
    use_case = CreateChannelUseCase(channels, servers_facade=servers_facade)

    with pytest.raises(ValueError, match="user_id is required"):
        await use_case(server_id=uuid4(), name="chat")


async def test_publishes_channel_created_event() -> None:
    channels = FakeChannelRepository()
    realtime = FakeRealtimeNotifier()
    use_case = CreateChannelUseCase(channels, realtime_notifier=realtime)
    server_id = uuid4()

    channel = await use_case(server_id=server_id, name="announcements")

    assert len(realtime.room_published) == 1
    room, event_type, payload = realtime.room_published[0]
    assert room == server_room(server_id)
    assert event_type == EventType.CHANNEL_CREATED
    assert payload["id"] == channel.id
    assert payload["name"] == "announcements"
    assert payload["server_id"] == server_id


async def test_no_event_when_notifier_is_none() -> None:
    channels = FakeChannelRepository()
    use_case = CreateChannelUseCase(channels)
    server_id = uuid4()

    channel = await use_case(server_id=server_id, name="general")

    assert channel.name == "general"


async def test_publishes_event_with_servers_facade() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    servers_facade = FakeServersFacade(server_members, servers)
    realtime = FakeRealtimeNotifier()
    use_case = CreateChannelUseCase(
        channels, realtime_notifier=realtime, servers_facade=servers_facade
    )
    owner_id = uuid4()
    server = await servers.create(ServerCreate(name="Server", owner_id=owner_id))
    await server_members.create(
        ServerMemberCreate(
            server_id=server.id,
            user_id=owner_id,
            role=ServerMemberRole.owner,
        )
    )

    channel = await use_case(server_id=server.id, name="chat", user_id=owner_id)

    assert len(realtime.room_published) == 1
    room, event_type, payload = realtime.room_published[0]
    assert room == server_room(server.id)
    assert event_type == EventType.CHANNEL_CREATED
    assert payload["id"] == channel.id
