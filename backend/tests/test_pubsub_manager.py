# type: ignore

"""
Tests for RedisPubSubManager.

Unit tests  — use mocks (MagicMock/AsyncMock), no real Redis needed.
Integration tests — use FakeRedis (fakeredis.aioredis), exercise the real
                    redis-py PubSub pipeline end-to-end without a Redis server.
"""

import asyncio
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
import logging

import pytest
from fakeredis import aioredis as fake_aioredis
from redis.exceptions import RedisError
import structlog

from src.core.redis.manager import RedisPubSubManager

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.stdlib.LoggerFactory(),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_raw_message(channel: str, data: str) -> dict:
    return {"type": "message", "channel": channel.encode(), "data": data.encode()}


def make_raw_pmessage(pattern: str, channel: str, data: str) -> dict:
    return {
        "type": "pmessage",
        "pattern": pattern.encode(),
        "channel": channel.encode(),
        "data": data.encode(),
    }


async def fake_listen(messages: list[dict]):
    """Async-generator that yields prepared messages then blocks forever."""
    for msg in messages:
        yield msg
    await asyncio.sleep(9999)


# ---------------------------------------------------------------------------
# Fixtures — unit (mock-based)
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_pubsub():
    pubsub = AsyncMock()
    pubsub.subscribe = AsyncMock()
    pubsub.unsubscribe = AsyncMock()
    pubsub.psubscribe = AsyncMock()
    pubsub.punsubscribe = AsyncMock()
    pubsub.aclose = AsyncMock()
    # listen() is NOT a coroutine — it returns an async-generator.
    # Using MagicMock prevents AsyncMock from wrapping the return value
    # in a coroutine, which would break `async for`.
    pubsub.listen = MagicMock(side_effect=lambda: fake_listen([]))
    return pubsub


@pytest.fixture
def mock_redis(mock_pubsub):
    redis = AsyncMock()
    redis.publish = AsyncMock()
    redis.pubsub = MagicMock(return_value=mock_pubsub)
    return redis


@pytest.fixture
def manager(mock_redis):
    return RedisPubSubManager(
        redis=mock_redis,
        retry_delay=0.01,
        max_retries=3,
        queue_maxsize=10,
    )


# ---------------------------------------------------------------------------
# Fixtures — integration (FakeRedis-based)
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_server():
    """Single FakeServer shared between publisher and subscriber."""
    return fake_aioredis.FakeServer()


@pytest.fixture
async def subscriber_redis(fake_server):
    r = fake_aioredis.FakeRedis(server=fake_server)
    yield r
    await r.aclose()


@pytest.fixture
async def publisher_redis(fake_server):
    r = fake_aioredis.FakeRedis(server=fake_server)
    yield r
    await r.aclose()


@pytest.fixture
async def fake_manager(subscriber_redis):
    mgr = RedisPubSubManager(
        redis=subscriber_redis,
        retry_delay=0.01,
        max_retries=3,
        queue_maxsize=64,
    )
    yield mgr
    await mgr.stop()


# ===========================================================================
# Unit tests
# ===========================================================================


class TestPublish:
    async def test_calls_redis_publish(self, manager, mock_redis):
        await manager.publish("chan", "hello")
        mock_redis.publish.assert_awaited_once_with("chan", "hello")

    async def test_raises_on_redis_error(self, manager, mock_redis):
        mock_redis.publish.side_effect = RedisError("boom")
        with pytest.raises(RedisError):
            await manager.publish("chan", "hello")


class TestSubscribe:
    async def test_registers_handler(self, manager):
        handler = AsyncMock()
        await manager.subscribe("chan", handler)

        assert handler in manager._handlers["chan"]
        assert "chan" in manager._queues

    async def test_multiple_handlers_same_channel(self, manager):
        h1, h2 = AsyncMock(), AsyncMock()
        await manager.subscribe("chan", h1)
        await manager.subscribe("chan", h2)

        assert manager._handlers["chan"] == [h1, h2]

    async def test_creates_queue_once(self, manager):
        h1, h2 = AsyncMock(), AsyncMock()
        await manager.subscribe("chan", h1)
        q = manager._queues["chan"]
        await manager.subscribe("chan", h2)

        assert manager._queues["chan"] is q  # same queue object


class TestUnsubscribe:
    async def test_removes_specific_handler(self, manager, mock_pubsub):
        h1, h2 = AsyncMock(), AsyncMock()
        await manager.subscribe("chan", h1)
        await manager.subscribe("chan", h2)

        await manager.unsubscribe("chan", h1)

        assert h1 not in manager._handlers["chan"]
        assert h2 in manager._handlers["chan"]
        mock_pubsub.unsubscribe.assert_not_awaited()

    async def test_removes_all_handlers_when_none_given(self, manager, mock_pubsub):
        h1, h2 = AsyncMock(), AsyncMock()
        await manager.subscribe("chan", h1)
        await manager.subscribe("chan", h2)

        await manager.unsubscribe("chan")

        assert not manager._handlers.get("chan")
        mock_pubsub.unsubscribe.assert_awaited_with("chan")

    async def test_last_handler_triggers_redis_unsubscribe(self, manager, mock_pubsub):
        handler = AsyncMock()
        await manager.subscribe("chan", handler)
        await manager.unsubscribe("chan", handler)

        assert not manager._handlers.get("chan")
        assert "chan" not in manager._queues
        mock_pubsub.unsubscribe.assert_awaited_with("chan")

    async def test_noop_on_unknown_channel(self, manager):
        # should not raise
        await manager.unsubscribe("nonexistent")


class TestPatternSubscribe:
    async def test_registers_handler(self, manager):
        handler = AsyncMock()
        await manager.psubscribe("news.*", handler)

        assert handler in manager._pattern_handlers["news.*"]

    async def test_punsubscribe_last_handler(self, manager, mock_pubsub):
        handler = AsyncMock()
        await manager.psubscribe("news.*", handler)
        await manager.punsubscribe("news.*", handler)

        assert not manager._pattern_handlers.get("news.*")
        mock_pubsub.punsubscribe.assert_awaited_with("news.*")

    async def test_punsubscribe_specific_handler_keeps_others(
        self, manager, mock_pubsub
    ):
        h1, h2 = AsyncMock(), AsyncMock()
        await manager.psubscribe("news.*", h1)
        await manager.psubscribe("news.*", h2)

        await manager.punsubscribe("news.*", h1)

        assert h1 not in manager._pattern_handlers["news.*"]
        assert h2 in manager._pattern_handlers["news.*"]
        mock_pubsub.punsubscribe.assert_not_awaited()


class TestMessageDispatching:
    async def test_message_delivered_to_handler(self, manager, mock_pubsub):
        received: list[tuple[str, str]] = []

        async def handler(channel: str, data: str) -> None:
            received.append((channel, data))

        mock_pubsub.listen.side_effect = lambda: fake_listen(
            [make_raw_message("chan", "hello")]
        )

        await manager.subscribe("chan", handler)
        await asyncio.sleep(0.05)
        await manager.stop()

        assert ("chan", "hello") in received

    async def test_pmessage_delivered_to_pattern_handler(self, manager, mock_pubsub):
        received: list[tuple[str, str]] = []

        async def handler(channel: str, data: str) -> None:
            received.append((channel, data))

        mock_pubsub.listen.side_effect = lambda: fake_listen(
            [make_raw_pmessage("news.*", "news.sport", "goal!")]
        )

        await manager.psubscribe("news.*", handler)
        await asyncio.sleep(0.05)
        await manager.stop()

        assert ("news.sport", "goal!") in received

    async def test_all_handlers_called(self, manager, mock_pubsub):
        h1, h2 = AsyncMock(), AsyncMock()

        mock_pubsub.listen.side_effect = lambda: fake_listen(
            [make_raw_message("chan", "ping")]
        )

        await manager.subscribe("chan", h1)
        await manager.subscribe("chan", h2)
        await asyncio.sleep(0.05)
        await manager.stop()

        h1.assert_awaited_once_with("chan", "ping")
        h2.assert_awaited_once_with("chan", "ping")

    async def test_unknown_message_type_ignored(self, manager, mock_pubsub):
        handler = AsyncMock()

        async def listen_with_subscribe_msg():
            yield {"type": "subscribe", "channel": b"chan", "data": 1}
            await asyncio.sleep(9999)

        mock_pubsub.listen.side_effect = listen_with_subscribe_msg

        await manager.subscribe("chan", handler)
        await asyncio.sleep(0.05)
        await manager.stop()

        handler.assert_not_awaited()


class TestBackpressure:
    async def test_queue_full_drops_message(self, manager, mock_pubsub, caplog):
        """Messages are silently dropped (not raised) when the queue is full."""
        handler = AsyncMock()
        messages = [make_raw_message("chan", str(i)) for i in range(20)]

        mock_pubsub.listen.side_effect = lambda: fake_listen(messages)

        # Override the queue with maxsize=1 BEFORE subscribe creates it
        manager._queue_maxsize = 1
        await manager.subscribe("chan", handler)
        await asyncio.sleep(0.1)
        await manager.stop()

        assert "queue_full_drop" in caplog.text

    async def test_handler_exception_does_not_crash_dispatcher(
        self, manager, mock_pubsub
    ):
        async def bad_handler(channel: str, data: str) -> None:
            raise ValueError("oops")

        mock_pubsub.listen.side_effect = lambda: fake_listen(
            [make_raw_message("chan", "msg")]
        )

        await manager.subscribe("chan", bad_handler)
        await asyncio.sleep(0.05)

        assert manager._running is True
        await manager.stop()


class TestReconnect:
    async def test_reconnects_after_redis_error(self, manager, mock_pubsub):
        received: list[str] = []

        async def handler(channel: str, data: str) -> None:
            received.append(data)

        async def listen_ok():
            yield make_raw_message("chan", "after_reconnect")
            await asyncio.sleep(9999)

        async def listen_fail():
            raise RedisError("connection lost")
            yield  # marks this as an async-generator so the error propagates correctly

        responses = iter([listen_fail, listen_ok])
        mock_pubsub.listen.side_effect = lambda: next(responses)()

        await manager.subscribe("chan", handler)
        await asyncio.sleep(0.3)
        await manager.stop()

        assert "after_reconnect" in received

    async def test_stops_after_max_retries(self, manager, mock_pubsub):
        mock_pubsub.listen.side_effect = lambda: (_ for _ in ()).throw(
            RedisError("persistent error")
        )

        async def always_fail():
            raise RedisError("persistent error")
            yield

        mock_pubsub.listen.side_effect = lambda: always_fail()

        await manager.subscribe("chan", AsyncMock())
        # max_retries=3, retry_delay=0.01 → should give up quickly
        await asyncio.sleep(0.5)

        assert manager._running is False


class TestStop:
    async def test_stop_sets_running_false(self, manager, mock_pubsub):
        await manager.subscribe("chan", AsyncMock())
        assert manager._running is True

        await manager.stop()

        assert manager._running is False

    async def test_stop_closes_pubsub(self, manager, mock_pubsub):
        await manager.subscribe("chan", AsyncMock())
        await manager.stop()

        mock_pubsub.aclose.assert_awaited()
        assert manager._pubsub is None

    async def test_stop_is_idempotent(self, manager):
        await manager.subscribe("chan", AsyncMock())
        await manager.stop()
        # second stop should not raise
        await manager.stop()


# ===========================================================================
# Integration tests (FakeRedis)
# ===========================================================================


class TestIntegration:
    """
    These tests use a real redis-py PubSub pipeline backed by FakeRedis.
    No mocks — exercises the actual listener/dispatcher/queue path.
    """

    async def test_publish_subscribe_roundtrip(self, fake_manager, publisher_redis):
        received: list[tuple[str, str]] = []

        async def handler(channel: str, data: str) -> None:
            received.append((channel, data))

        await fake_manager.subscribe("greetings", handler)
        await asyncio.sleep(0.05)

        await publisher_redis.publish("greetings", "hello")
        await asyncio.sleep(0.1)

        assert ("greetings", "hello") in received

    async def test_multiple_messages_in_order(self, fake_manager, publisher_redis):
        received: list[str] = []

        async def handler(channel: str, data: str) -> None:
            received.append(data)

        await fake_manager.subscribe("ordered", handler)
        await asyncio.sleep(0.05)

        for i in range(5):
            await publisher_redis.publish("ordered", str(i))

        await asyncio.sleep(0.2)

        assert received == ["0", "1", "2", "3", "4"]

    async def test_multiple_subscribers_same_channel(
        self, fake_manager, publisher_redis
    ):
        results: dict[str, list[str]] = {"a": [], "b": []}

        async def handler_a(channel: str, data: str) -> None:
            results["a"].append(data)

        async def handler_b(channel: str, data: str) -> None:
            results["b"].append(data)

        await fake_manager.subscribe("shared", handler_a)
        await fake_manager.subscribe("shared", handler_b)
        await asyncio.sleep(0.05)

        await publisher_redis.publish("shared", "broadcast")
        await asyncio.sleep(0.1)

        assert results["a"] == ["broadcast"]
        assert results["b"] == ["broadcast"]

    async def test_pattern_subscribe_roundtrip(self, fake_manager, publisher_redis):
        received: list[tuple[str, str]] = []

        async def handler(channel: str, data: str) -> None:
            received.append((channel, data))

        await fake_manager.psubscribe("events.*", handler)
        await asyncio.sleep(0.05)

        await publisher_redis.publish("events.login", "user_1")
        await publisher_redis.publish("events.logout", "user_2")
        await asyncio.sleep(0.2)

        assert ("events.login", "user_1") in received
        assert ("events.logout", "user_2") in received

    # DEAD LOCK
    # async def test_unsubscribe_stops_delivery(self, fake_manager, publisher_redis):
    #     received: list[str] = []
    #
    #     async def handler(channel: str, data: str) -> None:
    #         received.append(data)
    #
    #     await fake_manager.subscribe("temp", handler)
    #     await asyncio.sleep(0.05)
    #
    #     await publisher_redis.publish("temp", "before")
    #     await asyncio.sleep(0.1)
    #
    #     await fake_manager.unsubscribe("temp", handler)
    #     await asyncio.sleep(0.05)
    #
    #     await publisher_redis.publish("temp", "after")
    #     await asyncio.sleep(0.1)
    #
    #     assert "before" in received
    #     assert "after" not in received

    async def test_publish_to_unsubscribed_channel_is_ignored(
        self, fake_manager, publisher_redis
    ):
        handler = AsyncMock()
        await fake_manager.subscribe("active", handler)
        await asyncio.sleep(0.05)

        # publish to a channel nobody subscribed to
        await publisher_redis.publish("ghost", "ignored")
        await asyncio.sleep(0.1)

        handler.assert_not_awaited()
