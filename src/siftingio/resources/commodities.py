"""``/v1/hist/commodities/*`` — historical OHLC bars for commodities.

Covers precious metals (XAUUSD, XAGUSD, XPTUSD, XPDUSD), energy, and
industrials (e.g. XCUUSD copper, USOUSD WTI, NATGAS). Supports the ``1d``
interval and ``order`` (asc/desc)."""

from __future__ import annotations

from ..types import BarsResponse
from ._base import Req, _AsyncResource, _SyncResource, seg


def _bars(
    symbol: str, start: str, end: str | None, interval: str | None,
    cursor: str | None, limit: int | None, order: str | None,
) -> Req:
    return Req(
        f"/v1/hist/commodities/{seg(symbol)}/bars",
        {"start": start, "end": end, "interval": interval, "cursor": cursor,
         "limit": limit, "order": order},
    )


class CommoditiesResource(_SyncResource):
    def bars(
        self, symbol: str, *, start: str, end: str | None = None,
        interval: str | None = None, cursor: str | None = None, limit: int | None = None,
        order: str | None = None,
    ) -> BarsResponse:
        """OHLC bars, e.g. ``bars("XAUUSD", start="2024-01-01", interval="1d", order="desc")``.

        ``start`` is required. ``interval`` may be 1m/5m/15m/30m/1h/1d.
        ``order`` is ``"asc"`` (default, oldest first) or ``"desc"`` (newest first)."""
        return self._get(_bars(symbol, start, end, interval, cursor, limit, order))


class AsyncCommoditiesResource(_AsyncResource):
    async def bars(
        self, symbol: str, *, start: str, end: str | None = None,
        interval: str | None = None, cursor: str | None = None, limit: int | None = None,
        order: str | None = None,
    ) -> BarsResponse:
        return await self._aget(_bars(symbol, start, end, interval, cursor, limit, order))
