"""``/v1/fnd/stocks/*`` and ``/v1/hist/stocks/*`` — everything keyed by a US
equity ticker, plus the cross-sectional screener and OHLCV bars."""

from __future__ import annotations

from ..types import (
    BarsResponse,
    CompanyProfile,
    FilingDetail,
    Filings,
    FilingSectionDetail,
    FilingSections,
    FinancialConcept,
    Financials,
    ListResponse,
    Ratios,
    RiskFactorsDiff,
    ScreenerResult,
    StockSearchResponse,
)
from ._base import Req, _AsyncResource, _SyncResource, seg

# ── Request builders (single source of truth) ─────────────────────────────────


def _search(q: str, limit: int | None) -> Req:
    return Req("/v1/fnd/stocks/search", {"q": q, "limit": limit})


def _profile(ticker: str) -> Req:
    return Req(f"/v1/fnd/stocks/{seg(ticker)}/profile")


def _filings(
    ticker: str, form: str | None, frm: str | None, to: str | None,
    cursor: str | None, limit: int | None,
) -> Req:
    return Req(
        f"/v1/fnd/stocks/{seg(ticker)}/filings",
        {"form": form, "from": frm, "to": to, "cursor": cursor, "limit": limit},
    )


def _filing(ticker: str, accession: str) -> Req:
    return Req(f"/v1/fnd/stocks/{seg(ticker)}/filings/{seg(accession)}")


def _sections(ticker: str, accession: str) -> Req:
    return Req(f"/v1/fnd/stocks/{seg(ticker)}/filings/{seg(accession)}/sections")


def _section(ticker: str, accession: str, section: str) -> Req:
    return Req(
        f"/v1/fnd/stocks/{seg(ticker)}/filings/{seg(accession)}/sections/{seg(section)}"
    )


def _risk_factors_diff(ticker: str) -> Req:
    return Req(f"/v1/fnd/stocks/{seg(ticker)}/risk-factors-diff")


def _ratios(ticker: str) -> Req:
    return Req(f"/v1/fnd/stocks/{seg(ticker)}/ratios")


def _earnings(ticker: str, cursor: str | None, limit: int | None) -> Req:
    return Req(f"/v1/fnd/stocks/{seg(ticker)}/earnings", {"cursor": cursor, "limit": limit})


def _financials(ticker: str) -> Req:
    return Req(f"/v1/fnd/stocks/{seg(ticker)}/financials")


def _financial_concept(ticker: str, concept: str, taxonomy: str | None) -> Req:
    return Req(
        f"/v1/fnd/stocks/{seg(ticker)}/financials/{seg(concept)}",
        {"taxonomy": taxonomy},
    )


def _insiders(ticker: str, cursor: str | None, limit: int | None) -> Req:
    return Req(f"/v1/fnd/stocks/{seg(ticker)}/insiders", {"cursor": cursor, "limit": limit})


def _ownership(ticker: str, cursor: str | None, limit: int | None) -> Req:
    return Req(f"/v1/fnd/stocks/{seg(ticker)}/ownership", {"cursor": cursor, "limit": limit})


def _events(ticker: str, item: str | None, cursor: str | None, limit: int | None) -> Req:
    return Req(
        f"/v1/fnd/stocks/{seg(ticker)}/events",
        {"item": item, "cursor": cursor, "limit": limit},
    )


def _compensation(ticker: str, cursor: str | None, limit: int | None) -> Req:
    return Req(
        f"/v1/fnd/stocks/{seg(ticker)}/compensation", {"cursor": cursor, "limit": limit}
    )


def _screener(
    concept: str, period: str, taxonomy: str | None, unit: str | None,
    cursor: str | None, limit: int | None,
) -> Req:
    return Req(
        f"/v1/fnd/stocks/screener/{seg(concept)}/{seg(period)}",
        {"taxonomy": taxonomy, "unit": unit, "cursor": cursor, "limit": limit},
    )


def _bars(
    ticker: str, start: str | None, end: str | None, interval: str | None,
    cursor: str | None, limit: int | None,
) -> Req:
    return Req(
        f"/v1/hist/stocks/{seg(ticker)}/bars",
        {"start": start, "end": end, "interval": interval, "cursor": cursor, "limit": limit},
    )


# ── Sync ──────────────────────────────────────────────────────────────────────


class StocksResource(_SyncResource):
    def search(self, q: str, *, limit: int | None = None) -> StockSearchResponse:
        return self._get(_search(q, limit))

    def profile(self, ticker: str) -> CompanyProfile:
        return self._get(_profile(ticker))

    def filings(
        self, ticker: str, *, form: str | None = None, from_: str | None = None,
        to: str | None = None, cursor: str | None = None, limit: int | None = None,
    ) -> Filings:
        return self._get(_filings(ticker, form, from_, to, cursor, limit))

    def filing(self, ticker: str, accession: str) -> FilingDetail:
        return self._get(_filing(ticker, accession))

    def sections(self, ticker: str, accession: str) -> FilingSections:
        return self._get(_sections(ticker, accession))

    def section(self, ticker: str, accession: str, section: str) -> FilingSectionDetail:
        return self._get(_section(ticker, accession, section))

    def risk_factors_diff(self, ticker: str) -> RiskFactorsDiff:
        return self._get(_risk_factors_diff(ticker))

    def ratios(self, ticker: str) -> Ratios:
        return self._get(_ratios(ticker))

    def earnings(
        self, ticker: str, *, cursor: str | None = None, limit: int | None = None
    ) -> ListResponse:
        return self._get(_earnings(ticker, cursor, limit))

    def financials(self, ticker: str) -> Financials:
        return self._get(_financials(ticker))

    def financial_concept(
        self, ticker: str, concept: str, *, taxonomy: str | None = None
    ) -> FinancialConcept:
        return self._get(_financial_concept(ticker, concept, taxonomy))

    def insiders(
        self, ticker: str, *, cursor: str | None = None, limit: int | None = None
    ) -> ListResponse:
        return self._get(_insiders(ticker, cursor, limit))

    def ownership(
        self, ticker: str, *, cursor: str | None = None, limit: int | None = None
    ) -> ListResponse:
        return self._get(_ownership(ticker, cursor, limit))

    def events(
        self, ticker: str, *, item: str | None = None,
        cursor: str | None = None, limit: int | None = None,
    ) -> ListResponse:
        return self._get(_events(ticker, item, cursor, limit))

    def compensation(
        self, ticker: str, *, cursor: str | None = None, limit: int | None = None
    ) -> ListResponse:
        return self._get(_compensation(ticker, cursor, limit))

    def screener(
        self, concept: str, period: str, *, taxonomy: str | None = None,
        unit: str | None = None, cursor: str | None = None, limit: int | None = None,
    ) -> ScreenerResult:
        return self._get(_screener(concept, period, taxonomy, unit, cursor, limit))

    def bars(
        self, ticker: str, *, start: str | None = None, end: str | None = None,
        interval: str | None = None, cursor: str | None = None, limit: int | None = None,
    ) -> BarsResponse:
        return self._get(_bars(ticker, start, end, interval, cursor, limit))


# ── Async ─────────────────────────────────────────────────────────────────────


class AsyncStocksResource(_AsyncResource):
    async def search(self, q: str, *, limit: int | None = None) -> StockSearchResponse:
        return await self._aget(_search(q, limit))

    async def profile(self, ticker: str) -> CompanyProfile:
        return await self._aget(_profile(ticker))

    async def filings(
        self, ticker: str, *, form: str | None = None, from_: str | None = None,
        to: str | None = None, cursor: str | None = None, limit: int | None = None,
    ) -> Filings:
        return await self._aget(_filings(ticker, form, from_, to, cursor, limit))

    async def filing(self, ticker: str, accession: str) -> FilingDetail:
        return await self._aget(_filing(ticker, accession))

    async def sections(self, ticker: str, accession: str) -> FilingSections:
        return await self._aget(_sections(ticker, accession))

    async def section(self, ticker: str, accession: str, section: str) -> FilingSectionDetail:
        return await self._aget(_section(ticker, accession, section))

    async def risk_factors_diff(self, ticker: str) -> RiskFactorsDiff:
        return await self._aget(_risk_factors_diff(ticker))

    async def ratios(self, ticker: str) -> Ratios:
        return await self._aget(_ratios(ticker))

    async def earnings(
        self, ticker: str, *, cursor: str | None = None, limit: int | None = None
    ) -> ListResponse:
        return await self._aget(_earnings(ticker, cursor, limit))

    async def financials(self, ticker: str) -> Financials:
        return await self._aget(_financials(ticker))

    async def financial_concept(
        self, ticker: str, concept: str, *, taxonomy: str | None = None
    ) -> FinancialConcept:
        return await self._aget(_financial_concept(ticker, concept, taxonomy))

    async def insiders(
        self, ticker: str, *, cursor: str | None = None, limit: int | None = None
    ) -> ListResponse:
        return await self._aget(_insiders(ticker, cursor, limit))

    async def ownership(
        self, ticker: str, *, cursor: str | None = None, limit: int | None = None
    ) -> ListResponse:
        return await self._aget(_ownership(ticker, cursor, limit))

    async def events(
        self, ticker: str, *, item: str | None = None,
        cursor: str | None = None, limit: int | None = None,
    ) -> ListResponse:
        return await self._aget(_events(ticker, item, cursor, limit))

    async def compensation(
        self, ticker: str, *, cursor: str | None = None, limit: int | None = None
    ) -> ListResponse:
        return await self._aget(_compensation(ticker, cursor, limit))

    async def screener(
        self, concept: str, period: str, *, taxonomy: str | None = None,
        unit: str | None = None, cursor: str | None = None, limit: int | None = None,
    ) -> ScreenerResult:
        return await self._aget(_screener(concept, period, taxonomy, unit, cursor, limit))

    async def bars(
        self, ticker: str, *, start: str | None = None, end: str | None = None,
        interval: str | None = None, cursor: str | None = None, limit: int | None = None,
    ) -> BarsResponse:
        return await self._aget(_bars(ticker, start, end, interval, cursor, limit))
