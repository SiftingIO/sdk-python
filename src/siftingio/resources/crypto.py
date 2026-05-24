"""``/v1/hist/crypto/*`` — historical OHLCV bars for USD-quoted crypto symbols.

When ``start`` predates all upstreams' coverage the API returns HTTP 422 with
code ``data_unavailable``; the raised :class:`~siftingio.errors.SiftingAPIError`
carries ``body["earliest"]`` with the earliest available date.
"""

from __future__ import annotations

from ..types import BarsResponse
from ._base import Req, _AsyncResource, _SyncResource, seg


def _bars(
    symbol: str, start: str, end: str | None, interval: str | None,
    cursor: str | None, limit: int | None,
) -> Req:
    return Req(
        f"/v1/hist/crypto/{seg(symbol)}/bars",
        {"start": start, "end": end, "interval": interval, "cursor": cursor, "limit": limit},
    )


class CryptoResource(_SyncResource):
    def bars(
        self, symbol: str, *, start: str, end: str | None = None,
        interval: str | None = None, cursor: str | None = None, limit: int | None = None,
    ) -> BarsResponse:
        """OHLCV bars, e.g. ``bars("BTCUSD", start="2024-01-01")``. ``start`` required; max ``limit`` 5000."""  # noqa: E501
        return self._get(_bars(symbol, start, end, interval, cursor, limit))


class AsyncCryptoResource(_AsyncResource):
    async def bars(
        self, symbol: str, *, start: str, end: str | None = None,
        interval: str | None = None, cursor: str | None = None, limit: int | None = None,
    ) -> BarsResponse:
        return await self._aget(_bars(symbol, start, end, interval, cursor, limit))
