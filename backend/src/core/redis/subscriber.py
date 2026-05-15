import asyncio
from collections import defaultdict
from typing import Callable, Coroutine, Any
from functools import partial
from enum import Enum, auto

from redis import RedisError
from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from src.core.logging import get_logger

logger = get_logger(__name__)
MessageHandler = Callable[[str, str], Coroutine[Any, Any, None]]
_RETRYABLE_ERRORS = (
    RedisError,
    OSError,
    ConnectionError,
    TimeoutError,
    asyncio.TimeoutError,
)


class _State(Enum):
    INITIAL = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()


class RedisSubscriber:
    def __init__(
        self,
        redis: Redis,
        retry_delay: float = 1.0,
        max_retries: int = 10,
        queue_maxsize: int = 20,
        max_concurrency: int = 100,
    ):
        self._retry_delay = retry_delay
        self._max_retries = max_retries
        self._redis = redis
        self._queue_maxsize = queue_maxsize
        self._max_concurrency = max_concurrency
        self._pubsub_instance: PubSub | None = None
        self._handlers: dict[str, list[MessageHandler]] = defaultdict(list)
        self._tasks: set[asyncio.Task] = set()
        self._drain_tasks: set[asyncio.Task] = set()
        self._queues: dict[str, asyncio.Queue] = {}
        self._closing_queues: dict[str, asyncio.Queue] = {}
        self._dispatch_event = asyncio.Event()
        self._dispatch_offset = 0
        self._listener_task: asyncio.Task[None] | None = None
        self._dispatcher_task: asyncio.Task[None] | None = None
        self._lifecycle_lock = asyncio.Lock()
        self._subscription_lock = asyncio.Lock()
        self._state = _State.INITIAL

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"state={self._state.name}, "
            f"channels={len(self._handlers)}, "
            f"tasks={len(self._tasks)}"
            f")"
        )

    def __str__(self) -> str:
        return f"RedisSubscriber<{self._state.name}>"

    def __contains__(self, channel: str) -> bool:
        return channel in self._handlers

    def __len__(self) -> int:
        return len(self._handlers)

    def __bool__(self) -> bool:
        return self._state is _State.RUNNING

    async def start(self):
        async with self._lifecycle_lock:
            if self._state in (_State.STARTING, _State.RUNNING):
                return
            self._state = _State.STARTING
            try:
                self._pubsub_instance = self._redis.pubsub()
                await self._subscribe("__subscriber_keepalive__")
                self._dispatch_event.set()
                self._listener_task = asyncio.create_task(self._listener_loop())
                self._dispatcher_task = asyncio.create_task(self._dispatcher_loop())
                self._state = _State.RUNNING
            except Exception:
                self._state = _State.STOPPED
                raise

    async def stop(self, timeout: float = 30.0):
        async with self._lifecycle_lock:
            if self._state in (_State.STOPPING, _State.STOPPED):
                return
            self._state = _State.STOPPING
            try:
                if self._listener_task:
                    self._listener_task.cancel()
                    try:
                        await self._listener_task
                    except asyncio.CancelledError:
                        pass
                try:
                    async with asyncio.timeout(timeout):
                        all_queues = [
                            *self._queues.values(),
                            *self._closing_queues.values(),
                        ]
                        if all_queues:
                            await asyncio.gather(*(q.join() for q in all_queues))
                        if self._tasks:
                            await asyncio.gather(*self._tasks, return_exceptions=True)
                except TimeoutError:
                    logger.warning("stop_timeout", remaining_tasks=len(self._tasks))
                    for task in list(self._tasks):
                        task.cancel()
                    await asyncio.gather(*self._tasks, return_exceptions=True)
                if self._dispatcher_task:
                    self._dispatcher_task.cancel()
                    try:
                        await self._dispatcher_task
                    except asyncio.CancelledError:
                        pass
                for task in list(self._drain_tasks):
                    task.cancel()
                await asyncio.gather(*list(self._drain_tasks), return_exceptions=True)
                async with self._subscription_lock:
                    await self._unsubscribe()
                    await self._close()
            finally:
                self._state = _State.STOPPED

    async def subscribe(self, channel: str, handler: MessageHandler):
        async with self._subscription_lock:
            self._ensure_running()
            self._handlers[channel].append(handler)
            if len(self._handlers[channel]) == 1:
                self._queues[channel] = asyncio.Queue(maxsize=self._queue_maxsize)
                try:
                    await self._subscribe(channel)
                except Exception:
                    # on error rollback
                    self._handlers[channel].remove(handler)
                    if not self._handlers[channel]:
                        self._handlers.pop(channel, None)
                        self._queues.pop(channel, None)
                    raise

    async def unsubscribe(self, channel: str, handler: MessageHandler | None = None):
        async with self._subscription_lock:
            self._ensure_running()
            if handler is None:
                self._handlers.pop(channel, None)
            else:
                self._handlers[channel] = [
                    h for h in self._handlers[channel] if h is not handler
                ]
                if not self._handlers[channel]:
                    self._handlers.pop(channel, None)
            if not self._handlers.get(channel):
                await self._unsubscribe(channel)
                queue = self._queues.pop(channel, None)
                if queue is not None:
                    self._closing_queues[channel] = queue
                    task = asyncio.create_task(self._drain_and_remove(channel, queue))
                    self._drain_tasks.add(task)
                    task.add_done_callback(self._drain_tasks.discard)

    async def _subscribe(self, *channels: str, timeout: int = 10) -> None:
        async with asyncio.timeout(timeout):
            await self._pubsub.subscribe(*channels)

    async def _unsubscribe(self, *channels: str, timeout: int = 10) -> None:
        async with asyncio.timeout(timeout):
            await self._pubsub.unsubscribe(*channels)

    async def _close(self, timeout: int = 10) -> None:
        async with asyncio.timeout(timeout):
            await self._pubsub.close()

    async def _recreate_pubsub(self, channels: list[str]) -> None:
        try:
            await self._unsubscribe()
            await self._close()
        except Exception:  # noqa
            pass

        self._pubsub_instance = self._redis.pubsub()
        await self._subscribe(*channels)

    async def _drain_and_remove(self, channel: str, queue: asyncio.Queue):
        try:
            await queue.join()
        except asyncio.CancelledError:
            pass
        finally:
            self._closing_queues.pop(channel, None)
            logger.info("channel_drained", channel=channel)

    def _try_submit(
        self,
        channel: str,
        data: str,
        handler: MessageHandler,
        queue: asyncio.Queue,
    ) -> None:
        coro = None
        task = None
        try:
            coro = handler(channel, data)
            task = asyncio.create_task(coro)
            self._tasks.add(task)
            task.add_done_callback(partial(self._on_task_done, queue=queue))
        except Exception:
            if coro is not None:
                coro.close()
            if task is None:
                queue.task_done()
            raise

    def _on_task_done(self, task: asyncio.Task, queue: asyncio.Queue):
        self._tasks.discard(task)
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("handler_error", error=str(e))
        queue.task_done()
        self._dispatch_event.set()

    async def _listener_loop(self):
        retries = 0
        while self._state is _State.RUNNING:
            try:
                async for raw in self._pubsub.listen():
                    retries = 0
                    if raw["type"] != "message":
                        continue
                    channel: str = raw["channel"]
                    if isinstance(channel, bytes):
                        channel = channel.decode()
                    data: str = raw["data"]
                    if isinstance(data, bytes):
                        data = data.decode()
                    handlers = self._handlers.get(channel)
                    if not handlers:
                        continue
                    await self._enqueue(channel, data, handlers)
                logger.warning("pubsub_listen_ended")
                raise RedisError("PubSub listen unexpectedly ended")
            except asyncio.CancelledError:
                return
            except _RETRYABLE_ERRORS as e:
                if self._state is not _State.RUNNING:
                    return
                retries += 1
                if retries > self._max_retries:
                    logger.error("listener_max_retries_reached")
                    return
                wait = min(self._retry_delay * (2 ** (retries - 1)), 60.0)
                logger.warning(
                    "listener_redis_error",
                    attempt=retries,
                    max_retries=self._max_retries,
                    error=str(e),
                    retry_in=wait,
                )
                await asyncio.sleep(wait)
                if self._state is not _State.RUNNING:
                    return
                await self._reconnect()
                self._dispatch_event.set()
            except Exception:
                logger.exception("listener_unexpected_error")
                raise

    async def _dispatcher_loop(self):
        while self._state is _State.RUNNING:
            await self._dispatch_event.wait()
            self._dispatch_event.clear()
            items = [
                *self._queues.items(),
                *self._closing_queues.items(),
            ]
            if not items:
                continue

            # Round-robin to prevent starvation (not completely)
            n = len(items)
            rotated = items[self._dispatch_offset :] + items[: self._dispatch_offset]

            for channel, queue in rotated:
                while not queue.empty() and len(self._tasks) < self._max_concurrency:
                    data, handler = queue.get_nowait()
                    self._try_submit(channel, data, handler, queue)

            self._dispatch_offset = (self._dispatch_offset + 1) % n

    async def _enqueue(
        self,
        channel: str,
        data: str,
        handlers: list[MessageHandler],
    ) -> None:
        queue = self._queues.get(channel)
        if queue is None:
            return
        needed = len(handlers)
        available = queue.maxsize - queue.qsize()
        if available < needed:
            logger.warning(
                "queue_full_drop",
                channel=channel,
                dropped_handlers=needed,
            )
            return
        for handler in handlers:
            try:
                queue.put_nowait((data, handler))
            except asyncio.QueueFull:
                logger.warning("queue_full_race_drop", channel=channel)
                return
        self._dispatch_event.set()

    async def _reconnect(self):
        async with self._lifecycle_lock:
            if self._state is not _State.RUNNING:
                return
            async with self._subscription_lock:
                # IMPORTANT:
                # state may change while waiting for locks
                if self._state is not _State.RUNNING:
                    return
                channels = ["__subscriber_keepalive__", *self._handlers.keys()]
                await self._recreate_pubsub(channels)
                logger.info("pubsub_reconnected", channels=channels)

    def _ensure_running(self):
        if self._state is not _State.RUNNING:
            raise RuntimeError(f"RedisSubscriber is not running: {self._state}")

    @property
    def _pubsub(self) -> PubSub:
        if self._pubsub_instance is None:
            raise RuntimeError("RedisSubscriber is not started")

        return self._pubsub_instance
