"""The sync :class:`SiftingClient` and async :class:`AsyncSiftingClient`."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from ._transport import (
    AsyncKeyProvider,
    SyncKeyProvider,
    _AsyncTransport,
    _SyncTransport,
)
from .resources.crypto import AsyncCryptoResource, CryptoResource
from .resources.dex import AsyncDexResource, DexResource
from .resources.economic_calendar import (
    AsyncEconomicCalendarResource,
    EconomicCalendarResource,
)
from .resources.filers import AsyncFilersResource, FilersResource
from .resources.forex import AsyncForexResource, ForexResource
from .resources.last import AsyncLastResource, LastResource
from .resources.markets import AsyncMarketsResource, MarketsResource
from .resources.stocks import AsyncStocksResource, StocksResource
from .ws.client import AsyncSiftingSocket, SiftingSocket


class SiftingClient:
    """Blocking client for the SiftingIO data API.

    ::

        from siftingio import SiftingClient

        client = SiftingClient(api_key="sft_...")
        trade = client.last.trade("crypto", "BTCUSDT")
        profile = client.stocks.profile("AAPL")

    Resources mirror the API URL structure, so the docs map 1:1 onto methods.
    Usable as a context manager to close the underlying HTTP connection pool.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        get_api_key: SyncKeyProvider | None = None,
        base_url: str | None = None,
        ws_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: Mapping[str, str] | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._t = _SyncTransport(
            api_key=api_key,
            get_api_key=get_api_key,
            base_url=base_url,
            ws_url=ws_url,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
            http_client=http_client,
        )
        self.last = LastResource(self._t)
        self.stocks = StocksResource(self._t)
        self.filers = FilersResource(self._t)
        self.markets = MarketsResource(self._t)
        self.forex = ForexResource(self._t)
        self.crypto = CryptoResource(self._t)
        self.dex = DexResource(self._t)
        self.economic_calendar = EconomicCalendarResource(self._t)

    def ws(self, **options: Any) -> SiftingSocket:
        """Create a blocking live WebSocket client (see :class:`SiftingSocket`)."""
        return SiftingSocket(self._t, **options)

    def close(self) -> None:
        self._t.close()

    def __enter__(self) -> SiftingClient:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


class AsyncSiftingClient:
    """Asyncio client for the SiftingIO data API.

    ::

        from siftingio import AsyncSiftingClient

        async with AsyncSiftingClient(api_key="sft_...") as client:
            trade = await client.last.trade("crypto", "BTCUSDT")
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        get_api_key: AsyncKeyProvider | None = None,
        base_url: str | None = None,
        ws_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: Mapping[str, str] | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._t = _AsyncTransport(
            api_key=api_key,
            get_api_key=get_api_key,
            base_url=base_url,
            ws_url=ws_url,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
            http_client=http_client,
        )
        self.last = AsyncLastResource(self._t)
        self.stocks = AsyncStocksResource(self._t)
        self.filers = AsyncFilersResource(self._t)
        self.markets = AsyncMarketsResource(self._t)
        self.forex = AsyncForexResource(self._t)
        self.crypto = AsyncCryptoResource(self._t)
        self.dex = AsyncDexResource(self._t)
        self.economic_calendar = AsyncEconomicCalendarResource(self._t)

    def ws(self, **options: Any) -> AsyncSiftingSocket:
        """Create an asyncio live WebSocket client (see :class:`AsyncSiftingSocket`)."""
        return AsyncSiftingSocket(self._t, **options)

    async def aclose(self) -> None:
        await self._t.aclose()

    async def __aenter__(self) -> AsyncSiftingClient:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.aclose()
