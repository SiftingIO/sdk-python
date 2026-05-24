"""WebSocket integration tests against a local echo/tick server."""

from __future__ import annotations

import asyncio
import json

import pytest

from siftingio import AsyncSiftingClient

try:
    from websockets.asyncio.server import serve
except ImportError:  # websockets < 13
    from websockets import serve  # type: ignore[no-redef]


async def _server_handler(ws, *_args):
    """Reply to subscribe with an ack + one tick per symbol; pong on ping."""
    async for raw in ws:
        msg = json.loads(raw)
        op = msg.get("op")
        if op == "subscribe":
            await ws.send(json.dumps({"f": "ack"}))
            for sym in msg["symbols"]:
                await ws.send(json.dumps({"f": "tick", "s": sym, "p": "100", "t": 1}))
        elif op == "ping":
            await ws.send(json.dumps({"f": "pong"}))


@pytest.mark.asyncio
async def test_async_ws_subscribe_and_receive():
    async with serve(_server_handler, "localhost", 0) as server:
        port = server.sockets[0].getsockname()[1]
        client = AsyncSiftingClient(api_key="k", ws_url=f"ws://localhost:{port}")
        socket = client.ws(auto_reconnect=False)

        ticks: list[dict] = []
        acks: list[dict] = []
        socket.on("tick", lambda t: ticks.append(t))
        socket.on("ack", lambda a: acks.append(a))

        await socket.connect()
        assert socket.connected
        await socket.subscribe("cex", ["BTCUSD", "ETHUSD"])

        # Wait until both ticks land (handlers run on this loop).
        for _ in range(50):
            if len(ticks) >= 2:
                break
            await asyncio.sleep(0.02)

        assert acks, "expected an ack frame"
        symbols = sorted(t["s"] for t in ticks)
        assert symbols == ["BTCUSD", "ETHUSD"]

        await socket.close()
        await client.aclose()


@pytest.mark.asyncio
async def test_async_ws_async_iteration():
    async with serve(_server_handler, "localhost", 0) as server:
        port = server.sockets[0].getsockname()[1]
        client = AsyncSiftingClient(api_key="k", ws_url=f"ws://localhost:{port}")
        socket = client.ws(auto_reconnect=False)

        await socket.connect()
        await socket.subscribe("cex", ["BTCUSD"])

        got_tick = None
        async def consume():
            nonlocal got_tick
            async for frame in socket:
                if frame.get("f") == "tick":
                    got_tick = frame
                    return

        await asyncio.wait_for(consume(), timeout=2.0)
        assert got_tick is not None
        assert got_tick["s"] == "BTCUSD"

        await socket.close()
        await client.aclose()
