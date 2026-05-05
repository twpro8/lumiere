"""
Redis Pub/Sub Manager - Production-ready async implementation.
"""

import asyncio
from collections import defaultdict
from typing import Callable, Awaitable

from redis.asyncio import Redis
from redis.asyncio.client import PubSub
from redis.exceptions import RedisError

from src.core.logging import get_logger

logger = get_logger(__name__)


MessageHandler = Callable[[str, str], Awaitable[None]]


class RedisPubSubManager:
    """
    Async Redis Pub/Sub manager with support for multiple channels,
    pattern subscriptions, graceful shutdown, reconnection, and backpressure.
    """

    def __init__(
        self,
        redis: Redis,
        retry_delay: float = 2.0,
        max_retries: int = 10,
        queue_maxsize: int = 256,
    ) -> None:
        """
        Initialize the manager.

        Args:
            redis: An active redis.asyncio.Redis instance.
            retry_delay: Seconds to wait between reconnection attempts.
            max_retries: Maximum reconnection attempts before giving up.
            queue_maxsize: Max messages buffered per channel before backpressure kicks in.
        """
        self._redis = redis
        self._retry_delay = retry_delay
        self._max_retries = max_retries
        self._queue_maxsize = queue_maxsize

        self._handlers: dict[str, list[MessageHandler]] = defaultdict(list)
        self._pattern_handlers: dict[str, list[MessageHandler]] = defaultdict(list)

        self._pubsub: PubSub | None = None
        self._listener_task: asyncio.Task[None] | None = None
        self._dispatcher_task: asyncio.Task[None] | None = None

        # Channel -> asyncio.Queue for backpressure
        self._queues: dict[str, asyncio.Queue[tuple[str, str]]] = {}

        self._running = False
        self._lock = asyncio.Lock()

    async def publish(self, channel: str, message: str) -> None:
        """
        Publish a message to a Redis channel.

        Args:
            channel: Target channel name.
            message: UTF-8 string payload.
        """
        try:
            await self._redis.publish(channel, message)
            logger.debug("published", channel=channel, message=message)
        except RedisError as exc:
            logger.error(
                "publish_failed",
                channel=channel,
                error=str(exc),
                exc_info=True,
            )
            raise

    async def subscribe(self, channel: str, handler: MessageHandler) -> None:
        """
        Register an async handler for a channel and start listening.

        Multiple handlers can be registered for the same channel.

        Args:
            channel: Channel name to subscribe to.
            handler: Async callable(channel, message) invoked on each message.
        """
        async with self._lock:
            self._handlers[channel].append(handler)
            if channel not in self._queues:
                self._queues[channel] = asyncio.Queue(maxsize=self._queue_maxsize)

            if self._pubsub is not None:
                await self._pubsub.subscribe(channel)
                logger.info("subscribed", channel=channel)

            await self._ensure_running()

    async def psubscribe(self, pattern: str, handler: MessageHandler) -> None:
        """
        Register an async handler for a glob-style channel pattern (PSUBSCRIBE).

        Args:
            pattern: Redis glob pattern, e.g. ``news.*``.
            handler: Async callable(channel, message) invoked on matching messages.
        """
        async with self._lock:
            self._pattern_handlers[pattern].append(handler)
            if pattern not in self._queues:
                self._queues[pattern] = asyncio.Queue(maxsize=self._queue_maxsize)

            if self._pubsub is not None:
                await self._pubsub.psubscribe(pattern)
                logger.info("pattern_subscribed", pattern=pattern)

            await self._ensure_running()

    async def unsubscribe(
        self,
        channel: str,
        handler: MessageHandler | None = None,
    ) -> None:
        """
        Remove a handler (or all handlers) from a channel.

        If no handlers remain the channel is unsubscribed from Redis.

        Args:
            channel: Channel name.
            handler: Specific handler to remove; removes all if ``None``.
        """
        async with self._lock:
            if handler is None:
                self._handlers.pop(channel, None)
            else:
                handlers = self._handlers.get(channel, [])
                self._handlers[channel] = [h for h in handlers if h is not handler]

            if not self._handlers.get(channel) and self._pubsub is not None:
                await self._pubsub.unsubscribe(channel)
                self._queues.pop(channel, None)
                logger.info("unsubscribed", channel=channel)

    async def punsubscribe(
        self,
        pattern: str,
        handler: MessageHandler | None = None,
    ) -> None:
        """
        Remove a handler (or all handlers) from a pattern subscription.

        Args:
            pattern: The glob pattern previously registered.
            handler: Specific handler to remove; removes all if ``None``.
        """
        async with self._lock:
            if handler is None:
                self._pattern_handlers.pop(pattern, None)
            else:
                handlers = self._pattern_handlers.get(pattern, [])
                self._pattern_handlers[pattern] = [
                    h for h in handlers if h is not handler
                ]

            if not self._pattern_handlers.get(pattern) and self._pubsub is not None:
                await self._pubsub.punsubscribe(pattern)
                self._queues.pop(pattern, None)
                logger.info("pattern_unsubscribed", pattern=pattern)

    async def stop(self) -> None:
        """
        Gracefully stop all background tasks and release Redis resources.
        """
        async with self._lock:
            self._running = False

        for task in (self._listener_task, self._dispatcher_task):
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        if self._pubsub is not None:
            try:
                await self._pubsub.unsubscribe()
                await self._pubsub.punsubscribe()
                await self._pubsub.aclose()  # type: ignore[no-untyped-call]
            except RedisError as exc:
                logger.warning("pubsub_close_error", error=str(exc), exc_info=True)
            self._pubsub = None

        logger.info("pubsub_stopped")

    async def _ensure_running(self) -> None:
        """Create pubsub + background tasks if not already running (call under lock)."""
        if self._running:
            return

        self._running = True
        self._pubsub = self._redis.pubsub()

        # (Re-)subscribe to all known channels/patterns
        if self._handlers:
            await self._pubsub.subscribe(*self._handlers.keys())
        if self._pattern_handlers:
            await self._pubsub.psubscribe(*self._pattern_handlers.keys())

        self._listener_task = asyncio.create_task(
            self._listener_loop(),
            name="pubsub-listener",
        )
        self._dispatcher_task = asyncio.create_task(
            self._dispatcher_loop(),
            name="pubsub-dispatcher",
        )

    async def _listener_loop(self) -> None:
        """Read messages from Redis and enqueue them for dispatching."""
        retries = 0

        while self._running:
            try:
                assert self._pubsub is not None
                async for raw in self._pubsub.listen():
                    if not self._running:
                        return

                    msg_type = raw.get("type")
                    if msg_type not in ("message", "pmessage"):
                        continue

                    if msg_type == "message":
                        channel: str = raw["channel"]
                        if isinstance(channel, bytes):
                            channel = channel.decode()
                        data: str = raw["data"]
                        if isinstance(data, bytes):
                            data = data.decode()
                        await self._enqueue(channel, channel, data)

                    elif msg_type == "pmessage":
                        pattern: str = raw["pattern"]
                        if isinstance(pattern, bytes):
                            pattern = pattern.decode()
                        channel = raw["channel"]
                        if isinstance(channel, bytes):
                            channel = channel.decode()
                        data = raw["data"]
                        if isinstance(data, bytes):
                            data = data.decode()
                        await self._enqueue(pattern, channel, data)

                retries = 0  # clean exit from listen() loop

            except asyncio.CancelledError:
                return
            except RedisError as exc:
                if not self._running:
                    return
                retries += 1
                if retries > self._max_retries:
                    logger.error("listener_max_retries_reached")
                    self._running = False
                    return
                wait = self._retry_delay * retries
                logger.warning(
                    "listener_redis_error",
                    attempt=retries,
                    max_retries=self._max_retries,
                    error=str(exc),
                    retry_in=wait,
                )
                await asyncio.sleep(wait)
                await self._reconnect()

    async def _reconnect(self) -> None:
        """Re-create the PubSub object and re-subscribe to all channels."""
        try:
            if self._pubsub is not None:
                await self._pubsub.aclose()  # type: ignore[no-untyped-call]
        except Exception:
            pass

        self._pubsub = self._redis.pubsub()
        async with self._lock:
            if self._handlers:
                await self._pubsub.subscribe(*self._handlers.keys())
            if self._pattern_handlers:
                await self._pubsub.psubscribe(*self._pattern_handlers.keys())
        logger.info("reconnected")

    async def _enqueue(self, key: str, channel: str, data: str) -> None:
        """Put a (channel, data) tuple onto the appropriate queue (backpressure aware)."""
        queue = self._queues.get(key)
        if queue is None:
            return
        try:
            queue.put_nowait((channel, data))
        except asyncio.QueueFull:
            logger.warning("queue_full_drop", key=key)

    async def _dispatcher_loop(self) -> None:
        """Drain all queues and invoke registered handlers concurrently."""
        while self._running:
            dispatched = False

            for key, queue in list(self._queues.items()):
                while not queue.empty():
                    channel, data = queue.get_nowait()
                    handlers = self._handlers.get(
                        key, []
                    ) or self._pattern_handlers.get(key, [])
                    for handler in handlers:
                        asyncio.create_task(
                            self._safe_call(handler, channel, data),
                            name=f"handler-{key}",
                        )
                    dispatched = True

            if not dispatched:
                await asyncio.sleep(0.01)

    @staticmethod
    async def _safe_call(handler: MessageHandler, channel: str, data: str) -> None:
        """Invoke a handler, catching and logging any exception."""
        try:
            await handler(channel, data)
        except Exception:
            logger.exception("handler_exception", channel=channel)
