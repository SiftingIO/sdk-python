"""``/v1/hist/forex/*`` — historical OHLC bars for FX pairs (volume is always 0)."""

from __future__ import annotations

from ..types import BarsResponse
from ._base import Req, _AsyncResource, _SyncResource, seg


def _bars(
    pair: str, start: str, end: str | None, interval: str | None,
    cursor: str | None, limit: int | None,
) -> Req:
    return Req(
        f"/v1/hist/forex/{seg(pair)}/bars",
        {"start": start, "end": end, "interval": interval, "cursor": cursor, "limit": limit},
    )


class ForexResource(_SyncResource):
    def bars(
        self, pair: str, *, start: str, end: str | None = None,
        interval: str | None = None, cursor: str | None = None, limit: int | None = None,
    ) -> BarsResponse:
        """OHLC bars, e.g. ``bars("EURUSD", start="2024-01-01")``. ``start`` is required."""
        return self._get(_bars(pair, start, end, interval, cursor, limit))


class AsyncForexResource(_AsyncResource):
    async def bars(
        self, pair: str, *, start: str, end: str | None = None,
        interval: str | None = None, cursor: str | None = None, limit: int | None = None,
    ) -> BarsResponse:
        return await self._aget(_bars(pair, start, end, interval, cursor, limit))
