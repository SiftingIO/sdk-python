"""``/v1/last/*`` — live market data snapshots."""

from __future__ import annotations

from ..types import LastClose, LastQuote, LastTrade, LastTVL
from ._base import Req, _AsyncResource, _SyncResource, seg


def _trade(venue: str, symbol: str) -> Req:
    return Req(f"/v1/last/trade/{seg(venue)}/{seg(symbol)}")


def _quote(venue: str, symbol: str) -> Req:
    return Req(f"/v1/last/quote/{seg(venue)}/{seg(symbol)}")


def _close(venue: str, symbol: str) -> Req:
    return Req(f"/v1/last/close/{seg(venue)}/{seg(symbol)}")


def _tvl(chain: str, pair: str) -> Req:
    return Req(f"/v1/last/tvl/{seg(chain)}/{seg(pair)}")


class LastResource(_SyncResource):
    """Live data, e.g. ``client.last.trade("crypto", "BTCUSD")``."""

    def trade(self, venue: str, symbol: str) -> LastTrade:
        return self._get(_trade(venue, symbol))

    def quote(self, venue: str, symbol: str) -> LastQuote:
        return self._get(_quote(venue, symbol))

    def close(self, venue: str, symbol: str) -> LastClose:
        """Previous close, e.g. ``client.last.close("stocks", "AAPL")``.

        Venues: stocks, crypto, forex, commodities (DEX has no close).
        """
        return self._get(_close(venue, symbol))

    def tvl(self, chain: str, pair: str) -> LastTVL:
        return self._get(_tvl(chain, pair))


class AsyncLastResource(_AsyncResource):
    async def trade(self, venue: str, symbol: str) -> LastTrade:
        return await self._aget(_trade(venue, symbol))

    async def quote(self, venue: str, symbol: str) -> LastQuote:
        return await self._aget(_quote(venue, symbol))

    async def close(self, venue: str, symbol: str) -> LastClose:
        return await self._aget(_close(venue, symbol))

    async def tvl(self, chain: str, pair: str) -> LastTVL:
        return await self._aget(_tvl(chain, pair))
