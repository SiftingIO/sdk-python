"""Tests for both sync and async clients, using httpx's MockTransport."""

from __future__ import annotations

import httpx
import pytest

from siftingio import (
    AsyncSiftingClient,
    SiftingAPIError,
    SiftingClient,
    aauto_paginate,
    auto_paginate,
)


def mock_client(handler) -> SiftingClient:
    return SiftingClient(api_key="sft_test", http_client=httpx.Client(transport=httpx.MockTransport(handler)))


def async_mock_client(handler) -> AsyncSiftingClient:
    return AsyncSiftingClient(
        api_key="sft_test",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )


def test_request_url_params_and_key():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["key"] = request.headers.get("x-api-key")
        seen["accept_encoding"] = request.headers.get("accept-encoding")
        return httpx.Response(200, json={"s": "BTCUSD", "p": "1", "P": "1", "t": 1})

    client = mock_client(handler)
    trade = client.last.trade("crypto", "BTCUSD")

    assert trade["s"] == "BTCUSD"
    assert seen["url"] == "https://api.sifting.io/v1/last/trade/crypto/BTCUSD"
    assert seen["key"] == "sft_test"
    assert "gzip" in seen["accept_encoding"]


def test_query_params_drop_none_and_rename_from():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        return httpx.Response(200, json={"data": [], "meta": {"as_of": "x"}})

    client = mock_client(handler)
    client.stocks.filings("AAPL", form="10-K", from_="2024-01-01", limit=5)

    url = seen["url"]
    assert url.startswith("https://api.sifting.io/v1/fnd/stocks/AAPL/filings?")
    assert "form=10-K" in url
    assert "from=2024-01-01" in url  # from_ maps to the API's `from`
    assert "limit=5" in url
    assert "cursor" not in url  # None dropped


def test_custom_base_url():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        return httpx.Response(200, json={})

    client = SiftingClient(
        base_url="https://proxy.example.com",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    client.dex.wallet("eth", "0xABC")
    assert seen["url"] == "https://proxy.example.com/v1/fnd/dex/wallet/eth/0xABC"


def test_api_error_decoding():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            404,
            json={"error": "unknown_ticker", "message": "no such ticker"},
            headers={"X-Request-Id": "req-1"},
        )

    client = SiftingClient(
        api_key="k",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    with pytest.raises(SiftingAPIError) as exc:
        client.stocks.profile("NOPE")

    err = exc.value
    assert err.status == 404
    assert err.code == "unknown_ticker"
    assert err.message == "no such ticker"
    assert err.request_id == "req-1"


def test_rate_limit_retry_after():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "rate_limit_exceeded", "retry_after": 7})

    client = SiftingClient(
        api_key="k",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    with pytest.raises(SiftingAPIError) as exc:
        client.last.trade("crypto", "BTCUSD")
    assert exc.value.code == "rate_limit_exceeded"
    assert exc.value.retry_after == 7


def test_retry_then_success():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, json={"error": "rate_limit_exceeded"}, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"s": "X", "p": "1", "P": "1", "t": 1})

    client = SiftingClient(
        api_key="k",
        max_retries=2,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    trade = client.last.trade("crypto", "BTCUSD")
    assert trade["s"] == "X"
    assert calls["n"] == 2


def test_auto_paginate():
    pages = [
        {"data": [{"accession": "a"}, {"accession": "b"}], "meta": {"as_of": "x", "next_cursor": "c1"}},
        {"data": [{"accession": "c"}], "meta": {"as_of": "x"}},
    ]
    state = {"i": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        page = pages[state["i"]]
        state["i"] += 1
        return httpx.Response(200, json=page)

    client = mock_client(handler)
    seen = [f["accession"] for f in auto_paginate(lambda cursor: client.stocks.filings("AAPL", cursor=cursor))]
    assert seen == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_async_request_and_paginate():
    pages = [
        {"data": [{"x": 1}], "meta": {"as_of": "x", "next_cursor": "c1"}},
        {"data": [{"x": 2}], "meta": {"as_of": "x"}},
    ]
    state = {"i": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        page = pages[state["i"]]
        state["i"] += 1
        return httpx.Response(200, json=page)

    client = async_mock_client(handler)
    seen = [item["x"] async for item in aauto_paginate(lambda c: client.stocks.events("AAPL", cursor=c))]
    assert seen == [1, 2]
    await client.aclose()
