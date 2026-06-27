# SiftingIO Python SDK

Official Python SDK for the [SiftingIO Market Data API](https://sifting.io).

SiftingIO provides real-time and historical market data APIs for stocks, FX, crypto, commodities, DEX datasets, fundamentals, market news, and market hours through REST and WebSocket.

This SDK is built for Python developers integrating market data into financial applications, trading tools, dashboards, research workflows, backtesting systems, data pipelines, notebooks, and enterprise data workflows.

## Highlights

* **Sync and async clients** with `SiftingClient` for scripts, notebooks, and data workflows, and `AsyncSiftingClient` for asyncio services.
* **REST and WebSocket support** in one package.
* **Fully type-hinted** endpoint parameters and response shapes with `py.typed`.
* **Resource-mapped API design** with method names that mirror the [SiftingIO API documentation](https://sifting.io/docs).
* **Production-oriented defaults** including retry handling for `429` and `5xx`, gzip negotiation, cursor auto-pagination, and an auto-reconnecting WebSocket client.
* **Lightweight dependencies** using only `httpx` and `websockets`.

## Resources

* [Website](https://sifting.io)
* [API Documentation](https://sifting.io/docs)
* [Symbol Catalog](https://sifting.io/symbols)
* [Market Hours](https://sifting.io/market-hours)
* [Integrations](https://sifting.io/integrations)
* [Postman Collection](https://www.postman.com/siftingio)
* [Pricing](https://sifting.io/pricing)
* [System Status](https://siftingio.instatus.com)

## Explore coverage

Before integrating, you can browse supported symbols, asset classes, and symbol-level REST/WebSocket examples in the public catalog:

* [Symbol Catalog](https://sifting.io/symbols)
* [Market Hours](https://sifting.io/market-hours)

## Install

```bash
pip install siftingio
```

Requires Python 3.9+.

## Quick start: sync client

```python
from siftingio import SiftingClient

client = SiftingClient(api_key="sft_...")

# Live price snapshot
trade = client.last.trade("crypto", "BTCUSD")
print(trade["p"], trade["t"])

# Company fundamentals
profile = client.stocks.profile("AAPL")
ratios = client.stocks.ratios("AAPL")

# Historical bars
bars = client.crypto.bars("BTCUSD", start="2024-01-01", interval="1h")
print(len(bars["data"]), "bars")

client.close()
```

You can also use the sync client as a context manager:

```python
from siftingio import SiftingClient

with SiftingClient(api_key="sft_...") as client:
    quote = client.last.quote("crypto", "ETHUSD")
    print(quote["b"], quote["a"])
```

## Quick start: async client

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

Create an API key from the [SiftingIO dashboard](https://sifting.io). The SDK sends it as the `X-API-Key` header.

```python
from siftingio import SiftingClient

client = SiftingClient(api_key="sft_...")
```

You can also provide the API key dynamically, for example from a secrets manager or token rotation workflow:

```python
client = SiftingClient(get_api_key=lambda: read_secret("SIFTING_API_KEY"))
```

For async clients, the hook may be sync or async:

```python
async_client = AsyncSiftingClient(get_api_key=fetch_token_async)
```

## Configuration

```python
from siftingio import SiftingClient

client = SiftingClient(
    api_key="sft_...",                         # X-API-Key header
    get_api_key=None,                          # dynamic alternative to api_key
    base_url="https://api.sifting.io",         # override for proxies or staging
    ws_url="wss://stream.sifting.io/ws/v1",    # WebSocket endpoint
    timeout=30.0,                              # per-request timeout in seconds
    max_retries=2,                             # automatic retries for 429 and 5xx
    headers={"X-Trace": "..."},                # extra headers on every request
)
```

`AsyncSiftingClient` accepts the same configuration options and can use an `httpx.AsyncClient`.

## API resources

| Namespace                  | Endpoints                               | Highlights                                                                                                 |
| -------------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `client.last`              | `/v1/last/*`                            | `trade`, `quote`, `tvl` live snapshots                                                                     |
| `client.stocks`            | `/v1/fnd/stocks/*`, `/v1/hist/stocks/*` | `search`, `profile`, `filings`, `financials`, `ratios`, `insiders`, `events`, `screener`, `bars`, and more |
| `client.filers`            | `/v1/fnd/filers/*`                      | `holdings` for 13F positions                                                                               |
| `client.markets`           | `/v1/fnd/markets/*`                     | `list`, `status`, `hours`, `calendar`                                                                      |
| `client.forex`             | `/v1/hist/forex/*`                      | Historical FX bars                                                                                         |
| `client.crypto`            | `/v1/hist/crypto/*`                     | Historical crypto bars                                                                                     |
| `client.dex`               | `/v1/fnd/dex/*`                         | Wallet and DEX-related data                                                                                |
| `client.economic_calendar` | `/v1/fnd/economic-calendar`             | Economic calendar events                                                                                   |

Python keyword parameters that conflict with reserved words use a trailing underscore. For example, pass `from_=...` and the SDK sends it to the API as `from`.

## Pagination

List endpoints return:

```python
{
    "data": [...],
    "meta": {
        "next_cursor": "..."
    }
}
```

Use `auto_paginate` for sync workflows:

```python
from siftingio import auto_paginate, collect_all

for filing in auto_paginate(
    lambda cursor: client.stocks.filings("AAPL", cursor=cursor, form="10-K")
):
    print(filing["accession"], filing["filed_at"])

insiders = collect_all(
    lambda cursor: client.stocks.insiders("TSLA", cursor=cursor),
    max_items=100,
)
```

Use `aauto_paginate` for async workflows:

```python
from siftingio import aauto_paginate

async for filing in aauto_paginate(
    lambda cursor: client.stocks.filings("AAPL", cursor=cursor)
):
    print(filing["accession"], filing["filed_at"])
```

## Live WebSocket

### Async WebSocket

```python
async with client.ws() as socket:  # client = AsyncSiftingClient(...)
    socket.on("tick", lambda t: print(t["s"], t.get("p")))
    socket.on("error", lambda e: print("server error:", e["code"], e["message"]))

    await socket.subscribe("cex", ["BTCUSD", "ETHUSD"])  # cex, dex, fx, us, tvl

    async for frame in socket:
        ...
```

### Sync WebSocket

```python
socket = client.ws()  # client = SiftingClient(...)

socket.on("tick", lambda t: print(t["s"], t.get("p")))
socket.connect()
socket.subscribe("cex", ["BTCUSD"])

for frame in socket.stream():
    ...

socket.close()
```

Subscriptions are tracked and replayed automatically after reconnects.

In the sync client, handlers run on a background thread. Keep handlers fast, or hand work to your own queues, channels, or worker threads.

## Error handling

```python
from siftingio import SiftingAPIError, SiftingConnectionError

try:
    client.stocks.profile("NOPE")
except SiftingAPIError as err:
    err.status       # HTTP status code
    err.code         # API error code
    err.retry_after  # retry delay in seconds, when available
    err.request_id   # X-Request-Id for support
    err.body         # parsed error body
except SiftingConnectionError as err:
    err.timeout      # True for client-side timeout
```

The client automatically retries `429` and `5xx` responses up to `max_retries`, honoring `Retry-After` when available.

## License

MIT
