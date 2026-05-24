"""Live WebSocket clients: an asyncio-native :class:`AsyncSiftingSocket` and a
thread-backed sync :class:`SiftingSocket` wrapper.

Both track subscriptions and replay them on reconnect, so callers subscribe once
and keep receiving data across drops. Obtain one via ``client.ws()`` /
``async_client.ws()``.
"""

from __future__ import annotations

import asyncio
import json
import queue
import threading
from collections.abc import AsyncIterator, Iterator
from typing import Any, Callable

from .._transport import _AsyncTransport, _SyncTransport
from .types import WsProduct

# Prefer the modern asyncio client; fall back to the top-level connect on
# websockets < 13. Both support `async with` and async-iterator reconnect.
try:  # pragma: no cover - import shim
    from websockets.asyncio.client import connect as _ws_connect
except ImportError:  # pragma: no cover
    from websockets import connect as _ws_connect
from websockets.exceptions import ConnectionClosed

Handler = Callable[[Any], Any]
_STREAM_DONE = object()


class AsyncSiftingSocket:
    """Asyncio WebSocket client with auto-reconnect and subscription replay.

    ::

        socket = async_client.ws()
        socket.on("tick", lambda t: print(t["s"], t.get("p")))
        await socket.connect()
        await socket.subscribe("cex", ["BTCUSDT", "ETHUSDT"])
        async for frame in socket:   # or rely purely on handlers
            ...
    """

    def __init__(
        self,
        transport: _AsyncTransport,
        *,
        auto_reconnect: bool = True,
        heartbeat_interval: float = 0.0,
        open_timeout: float = 10.0,
    ) -> None:
        self._t = transport
        self.auto_reconnect = auto_reconnect
        self.heartbeat_interval = heartbeat_interval
        self.open_timeout = open_timeout

        self._handlers: dict[str, list[Handler]] = {}
        self._subs: dict[str, set[str]] = {}
        self._conn: Any = None
        self._task: asyncio.Task[None] | None = None
        self._closed = False
        self._open_event = asyncio.Event()
        self._stream_q: asyncio.Queue[Any] = asyncio.Queue()

    # ── Handlers ──────────────────────────────────────────────────────────────

    def on(self, event: str, handler: Handler) -> Callable[[], None]:
        """Register a handler (sync or async). Returns an unregister callable.

        Events: ``open``, ``close``, ``reconnect``, ``message`` (every frame),
        ``tick``, ``tvl``, ``ack``, ``pong``, ``error``.
        """
        self._handlers.setdefault(event, []).append(handler)
        return lambda: self._handlers.get(event, []).remove(handler)

    async def _dispatch(self, event: str, payload: Any) -> None:
        for handler in list(self._handlers.get(event, [])):
            try:
                result = handler(payload)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:  # noqa: BLE001 - a bad handler must not kill the loop
                pass

    # ── Lifecycle ───────────────────────────────────────────────────────────────

    async def connect(self) -> None:
        """Open the connection and wait until it is established."""
        self._closed = False
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run())
        try:
            await asyncio.wait_for(self._open_event.wait(), timeout=self.open_timeout)
        except asyncio.TimeoutError:
            # Connection is still being attempted in the background; let the
            # caller proceed (handlers/reconnect continue to run).
            pass

    async def close(self) -> None:
        """Close the connection and stop reconnecting."""
        self._closed = True
        if self._conn is not None:
            try:
                await self._conn.close()
            except Exception:  # noqa: BLE001
                pass
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
        await self._stream_q.put(_STREAM_DONE)

    @property
    def connected(self) -> bool:
        return self._conn is not None and not self._closed

    async def __aenter__(self) -> AsyncSiftingSocket:
        await self.connect()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def __aiter__(self) -> AsyncIterator[Any]:
        """Async-iterate every decoded server frame until the socket closes."""
        while True:
            frame = await self._stream_q.get()
            if frame is _STREAM_DONE:
                return
            yield frame

    # ── Operations ──────────────────────────────────────────────────────────────

    async def subscribe(self, product: WsProduct, symbols: list[str]) -> None:
        """Subscribe to symbols on a product channel (tracked + replayed on reconnect)."""
        bucket = self._subs.setdefault(product, set())
        bucket.update(symbols)
        if self.connected:
            await self._send({"op": "subscribe", "product": product, "symbols": symbols})

    async def unsubscribe(self, product: WsProduct, symbols: list[str]) -> None:
        bucket = self._subs.get(product)
        if bucket:
            bucket.difference_update(symbols)
            if not bucket:
                del self._subs[product]
        if self.connected:
            await self._send({"op": "unsubscribe", "product": product, "symbols": symbols})

    async def ping(self) -> None:
        if self.connected:
            await self._send({"op": "ping"})

    # ── Internals ─────────────────────────────────────────────────────────────────

    async def _send(self, payload: dict[str, Any]) -> None:
        if self._conn is not None:
            await self._conn.send(json.dumps(payload))

    async def _run(self) -> None:
        url = await self._t.ws_connect_url_resolved()
        attempt = 0
        while not self._closed:
            try:
                async with _ws_connect(url) as conn:
                    self._conn = conn
                    attempt = 0
                    self._open_event.set()
                    await self._flush_subscriptions()
                    await self._dispatch("open", None)
                    hb = (
                        asyncio.create_task(self._heartbeat())
                        if self.heartbeat_interval > 0
                        else None
                    )
                    try:
                        async for raw in conn:
                            await self._handle(raw)
                    finally:
                        if hb is not None:
                            hb.cancel()
            except (ConnectionClosed, OSError):
                pass
            except Exception:  # noqa: BLE001
                pass
            finally:
                self._conn = None
                self._open_event.clear()
                await self._dispatch("close", None)

            if self._closed or not self.auto_reconnect:
                break
            attempt += 1
            await self._dispatch("reconnect", {"attempt": attempt})
            await asyncio.sleep(min(30.0, 0.5 * 2 ** (attempt - 1)))

        await self._stream_q.put(_STREAM_DONE)

    async def _flush_subscriptions(self) -> None:
        for product, symbols in self._subs.items():
            if symbols:
                await self._send({"op": "subscribe", "product": product, "symbols": list(symbols)})

    async def _handle(self, raw: Any) -> None:
        try:
            frame = json.loads(raw if isinstance(raw, str) else raw.decode())
        except (ValueError, AttributeError):
            return
        await self._stream_q.put(frame)
        await self._dispatch("message", frame)
        kind = frame.get("f")
        if kind in ("tick", "tvl", "ack", "pong", "error"):
            await self._dispatch(kind, frame)

    async def _heartbeat(self) -> None:
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            await self.ping()


class SiftingSocket:
    """Blocking WebSocket client.

    Runs an :class:`AsyncSiftingSocket` on a dedicated background thread and
    bridges calls to it. Registered handlers run on that background thread.

    ::

        socket = client.ws()
        socket.on("tick", lambda t: print(t["s"], t.get("p")))
        socket.connect()
        socket.subscribe("cex", ["BTCUSDT"])
        for frame in socket.stream():
            ...
        socket.close()
    """

    def __init__(self, transport: _SyncTransport, **options: Any) -> None:
        # The sync transport shares config with an async transport built here;
        # the async socket only needs URL + key resolution, both sync-derivable.
        self._async_transport = _AsyncTransport(
            api_key=transport._api_key,
            base_url=transport.base_url,
            ws_url=transport.ws_url,
            timeout=transport.timeout,
            max_retries=transport.max_retries,
            headers=transport._extra_headers,
            get_api_key=transport._get_api_key,
        )
        self._options = options
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()
        self._socket = AsyncSiftingSocket(self._async_transport, **options)

    def _run(self, coro: Any) -> Any:
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()

    def on(self, event: str, handler: Handler) -> Callable[[], None]:
        return self._socket.on(event, handler)

    def connect(self) -> None:
        self._run(self._socket.connect())

    def subscribe(self, product: WsProduct, symbols: list[str]) -> None:
        self._run(self._socket.subscribe(product, symbols))

    def unsubscribe(self, product: WsProduct, symbols: list[str]) -> None:
        self._run(self._socket.unsubscribe(product, symbols))

    def ping(self) -> None:
        self._run(self._socket.ping())

    @property
    def connected(self) -> bool:
        return self._socket.connected

    def stream(self) -> Iterator[Any]:
        """Yield decoded server frames (blocking generator) until the socket closes."""
        q: queue.Queue[Any] = queue.Queue()
        off = self._socket.on("message", lambda frame: q.put(frame))
        stop = self._socket.on("close", lambda _: q.put(_STREAM_DONE))
        try:
            while True:
                frame = q.get()
                if frame is _STREAM_DONE:
                    return
                yield frame
        finally:
            off()
            stop()

    def close(self) -> None:
        try:
            self._run(self._socket.close())
        finally:
            self._loop.call_soon_threadsafe(self._loop.stop)

    def __enter__(self) -> SiftingSocket:
        self.connect()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
