# siftingio

Official Python SDK for the [SiftingIO](https://sifting.io) market data API — **sync and async** REST clients plus a live WebSocket, fully type-hinted.

- **Sync *and* async.** `SiftingClient` for scripts, notebooks, and pandas; `AsyncSiftingClient` for asyncio services. Same method names, same shapes.
- **Typed.** Every endpoint, parameter, and response is annotated (`py.typed`); responses are plain dicts with `TypedDict` shapes for editor autocomplete.
- **Resource-mapped.** Methods mirror the [API docs](https://sifting.io/docs) 1:1.
- **Batteries included.** Auto-retry on 429/5xx, gzip negotiation, cursor auto-pagination, and an auto-reconnecting WebSocket client.

## Install

```bash
pip install siftingio
```

Requires Python 3.9+. Depends only on `httpx` and `websockets`.

## Quick start (sync)

```python
from siftingio import SiftingClient

client = SiftingClient(api_key="sft_...")  # or env-driven; see below

# Live price
trade = client.last.trade("crypto", "BTCUSD")
print(trade["p"], trade["t"])

# Company fundamentals
profile = client.stocks.profile("AAPL")
ratios = client.stocks.ratios("AAPL")

# Historical bars (gzip handled for you)
bars = client.crypto.bars("BTCUSD", start="2024-01-01", interval="1h")
print(len(bars["data"]), "bars")

client.close()  # or use `with SiftingClient(...) as client:`
```

## Quick start (async)

```python
import asyncio
from siftingio import AsyncSiftingClient

async def main():
    async with AsyncSiftingClient(api_key="sft_...") as client:
        quote = await client.last.quote("crypto", "ETHUSD")
        print(quote["b"], quote["a"])

asyncio.run(main())
```

## Authentication

Get an API key from your [SiftingIO dashboard](https://sifting.io). It's sent as the `X-API-Key` header. You can also supply it dynamically (e.g. from a secrets manager or a rotating token):

```python
client = SiftingClient(get_api_key=lambda: read_secret("SIFTING_API_KEY"))

# Async: the hook may be sync or async
async_client = AsyncSiftingClient(get_api_key=fetch_token_async)
```

## Configuration

```python
SiftingClient(
    api_key="sft_...",       # X-API-Key header
    get_api_key=callable,    # dynamic alternative to api_key
    base_url="https://api.sifting.io",      # override for proxies/staging
    ws_url="wss://stream.sifting.io/ws/v1", # WebSocket endpoint
    timeout=30.0,            # per-request timeout (seconds)
    max_retries=2,           # automatic retries for 429 / 5xx
    headers={"X-Trace": "…"},# extra headers on every request
    http_client=httpx.Client(...),  # bring your own httpx client
)
```

`AsyncSiftingClient` takes the same arguments (with `httpx.AsyncClient`).

## Resources

| Namespace | Endpoints | Highlights |
|---|---|---|
| `client.last` | `/v1/last/*` | `trade`, `quote`, `tvl` — live snapshots |
| `client.stocks` | `/v1/fnd/stocks/*`, `/v1/hist/stocks/*` | `search`, `profile`, `filings`, `financials`, `ratios`, `insiders`, `events`, `screener`, `bars`, … |
| `client.filers` | `/v1/fnd/filers/*` | `holdings` — 13F positions |
| `client.markets` | `/v1/fnd/markets/*` | `list`, `status`, `hours`, `calendar` |
| `client.forex` | `/v1/hist/forex/*` | `bars` |
| `client.crypto` | `/v1/hist/crypto/*` | `bars` |
| `client.dex` | `/v1/fnd/dex/*` | `wallet` portfolios |
| `client.economic_calendar` | `/v1/fnd/economic-calendar` | `list` |

> Python keyword params that collide with reserved words use a trailing underscore: pass `from_=...` (sent to the API as `from`).

## Pagination

List endpoints return `{"data": [...], "meta": {...}}` with an opaque `meta["next_cursor"]`. Stream every page with `auto_paginate` (sync) or `aauto_paginate` (async):

```python
from siftingio import auto_paginate, collect_all

for filing in auto_paginate(lambda cursor: client.stocks.filings("AAPL", cursor=cursor, form="10-K")):
    print(filing["accession"], filing["filed_at"])

insiders = collect_all(lambda cursor: client.stocks.insiders("TSLA", cursor=cursor), max_items=100)
```

```python
from siftingio import aauto_paginate

async for filing in aauto_paginate(lambda cursor: client.stocks.filings("AAPL", cursor=cursor)):
    ...
```

## Live WebSocket

**Async:**

```python
async with client.ws() as socket:   # client = AsyncSiftingClient(...)
    socket.on("tick", lambda t: print(t["s"], t.get("p")))
    socket.on("error", lambda e: print("server error:", e["code"], e["message"]))
    await socket.subscribe("cex", ["BTCUSD", "ETHUSD"])  # products: cex|dex|fx|us|tvl
    async for frame in socket:       # or rely purely on handlers
        ...
```

**Sync:**

```python
socket = client.ws()                 # client = SiftingClient(...)
socket.on("tick", lambda t: print(t["s"], t.get("p")))
socket.connect()
socket.subscribe("cex", ["BTCUSD"])
for frame in socket.stream():
    ...
socket.close()
```

Subscriptions are tracked and **replayed automatically on reconnect**, so you subscribe once and keep receiving data across drops. In the sync client, handlers run on a background thread.

## Error handling

```python
from siftingio import SiftingAPIError, SiftingConnectionError

try:
    client.stocks.profile("NOPE")
except SiftingAPIError as err:
    err.status       # 404
    err.code         # "unknown_ticker"
    err.retry_after  # seconds, on 429
    err.request_id   # X-Request-Id — quote this in support tickets
    err.body         # full parsed error body
except SiftingConnectionError as err:
    err.timeout      # True if it was a client-side timeout
```

The client automatically retries `429` and `5xx` up to `max_retries`, honoring `Retry-After`.

## License

MIT
