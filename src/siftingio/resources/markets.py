"""``/v1/fnd/markets/*`` — catalog, status, hours, and holiday calendars."""

from __future__ import annotations

from ..types import (
    MarketCalendarResponse,
    MarketHoursResponse,
    MarketsListResponse,
    MarketsStatusAllResponse,
    MarketStatusResponse,
)
from ._base import Req, _AsyncResource, _SyncResource, seg


def _list(region: str | None) -> Req:
    return Req("/v1/fnd/markets", {"region": region})


def _status_all(region: str | None) -> Req:
    return Req("/v1/fnd/markets/status", {"region": region})


def _status(market: str) -> Req:
    return Req(f"/v1/fnd/markets/{seg(market)}/status")


def _hours(market: str) -> Req:
    return Req(f"/v1/fnd/markets/{seg(market)}/hours")


def _calendar(market: str, frm: str | None, to: str | None) -> Req:
    return Req(f"/v1/fnd/markets/{seg(market)}/calendar", {"from": frm, "to": to})


class MarketsResource(_SyncResource):
    def list(self, *, region: str | None = None) -> MarketsListResponse:
        return self._get(_list(region))

    def status_all(self, *, region: str | None = None) -> MarketsStatusAllResponse:
        return self._get(_status_all(region))

    def status(self, market: str) -> MarketStatusResponse:
        return self._get(_status(market))

    def hours(self, market: str) -> MarketHoursResponse:
        return self._get(_hours(market))

    def calendar(
        self, market: str, *, from_: str | None = None, to: str | None = None
    ) -> MarketCalendarResponse:
        return self._get(_calendar(market, from_, to))


class AsyncMarketsResource(_AsyncResource):
    async def list(self, *, region: str | None = None) -> MarketsListResponse:
        return await self._aget(_list(region))

    async def status_all(self, *, region: str | None = None) -> MarketsStatusAllResponse:
        return await self._aget(_status_all(region))

    async def status(self, market: str) -> MarketStatusResponse:
        return await self._aget(_status(market))

    async def hours(self, market: str) -> MarketHoursResponse:
        return await self._aget(_hours(market))

    async def calendar(
        self, market: str, *, from_: str | None = None, to: str | None = None
    ) -> MarketCalendarResponse:
        return await self._aget(_calendar(market, from_, to))
