"""Live WebSocket tour. Run with:  SIFTING_API_KEY=sft_… python examples/websocket.py

Shows both the async-native client and (commented) the blocking client.
"""

import asyncio
import os

from siftingio import AsyncSiftingClient


async def main() -> None:
    client = AsyncSiftingClient(api_key=os.environ.get("SIFTING_API_KEY"))
    socket = client.ws()

    socket.on("open", lambda _: print("connected"))
    socket.on("reconnect", lambda info: print("reconnecting, attempt", info["attempt"]))
    socket.on("error", lambda e: print("server error:", e.get("code"), e.get("message")))
    socket.on("tick", lambda t: print(f"[{t.get('class', 'tick')}] {t['s']} {t.get('p') or t.get('b')}"))
    socket.on("tvl", lambda v: print(f"[tvl] {v['s']} ${v['usd']}"))

    await socket.connect()
    await socket.subscribe("cex", ["BTCUSD", "ETHUSD"])
    await socket.subscribe("tvl", ["eth:WETH-USDC"])

    # Stream for 30 seconds, then close.
    await asyncio.sleep(30)
    await socket.close()
    await client.aclose()
    print("done")


# Blocking equivalent:
#
#     from siftingio import SiftingClient
#     client = SiftingClient(api_key=os.environ["SIFTING_API_KEY"])
#     socket = client.ws()
#     socket.on("tick", lambda t: print(t["s"], t.get("p")))
#     socket.connect()
#     socket.subscribe("cex", ["BTCUSD"])
#     for frame in socket.stream():
#         ...
#     socket.close()


if __name__ == "__main__":
    asyncio.run(main())
