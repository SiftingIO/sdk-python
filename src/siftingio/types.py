"""Typed shapes for API responses.

Responses are returned as plain ``dict`` objects (parsed JSON); these
``TypedDict`` definitions give editors and type checkers full knowledge of the
fields without any runtime parsing cost. They are declared ``total=False``
because the API omits empty/optional fields and may add new ones over time.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict, Union

# Loose string unions: documented values, but any string is accepted so a
# server-side addition never breaks a pinned client.
Venue = Literal["stocks", "crypto", "forex", "dex"]
Chain = Literal["eth", "base", "arbitrum", "bsc", "polygon"]
BarInterval = Literal["1m", "5m", "15m", "30m", "1h"]
Impact = Literal["low", "medium", "high"]
Region = Literal["north_america", "europe", "asia_pacific", "latam", "global"]
Agency = Literal["BLS", "BEA", "Census", "Fed", "DOL", "EIA"]


class ListMeta(TypedDict, total=False):
    """``meta`` block on paginated list endpoints."""

    next_cursor: str
    as_of: str
    total: int


# ── Live ────────────────────────────────────────────────────────────────────


class LastTrade(TypedDict, total=False):
    s: str
    p: str
    P: str
    t: int


class LastQuote(TypedDict, total=False):
    b: str
    B: str
    a: str
    A: str
    t: int


class LastTVL(TypedDict, total=False):
    chain: str
    pair: str
    usd: str
    r0: str
    r1: str
    n: int
    v: int
    t: int


# ── Stocks: discovery & profile ──────────────────────────────────────────────


class StockSearchResult(TypedDict, total=False):
    ticker: str
    name: str
    cik: str
    exchange: str


class StockSearchResponse(TypedDict, total=False):
    data: list[StockSearchResult]
    meta: ListMeta


class CompanyProfile(TypedDict, total=False):
    ticker: str
    cik: str
    name: str
    exchanges: list[str]
    other_tickers: list[str]
    sic_code: str
    sic_description: str
    entity_type: str
    fiscal_year_end: str


# ── Stocks: filings ───────────────────────────────────────────────────────────


class Filing(TypedDict, total=False):
    accession: str
    form: str
    filed_at: str
    period_end: str
    accepted_at: str
    items: str
    primary_document_url: str
    description: str
    has_xbrl: bool


class FilingDetail(Filing, total=False):
    ticker: str
    cik: str
    archive_url: str
    files: list[str]


class Filings(TypedDict, total=False):
    """Paginated filings list: ``{"data": [Filing], "meta": {...}}``."""

    data: list[Filing]
    meta: ListMeta


class FilingSection(TypedDict, total=False):
    section: str
    content: str


class FilingSections(TypedDict, total=False):
    ticker: str
    cik: str
    accession: str
    form: str
    filed_at: str
    sections: list[FilingSection]


class FilingSectionDetail(TypedDict, total=False):
    ticker: str
    cik: str
    accession: str
    form: str
    filed_at: str
    section: str
    content: str


# ── Stocks: risk-factor diff ──────────────────────────────────────────────────


class FilingRef(TypedDict, total=False):
    accession: str
    form: str
    filed_at: str
    period_end: str


class DiffPair(TypedDict, total=False):
    before: str
    after: str


class SectionDiffStats(TypedDict, total=False):
    before_paragraphs: int
    after_paragraphs: int
    unchanged_count: int
    added_count: int
    removed_count: int
    modified_count: int


class SectionDiff(TypedDict, total=False):
    added: list[str]
    removed: list[str]
    modified: list[DiffPair]
    stats: SectionDiffStats


class RiskFactorsDiff(TypedDict, total=False):
    ticker: str
    cik: str
    current: FilingRef
    previous: FilingRef
    diff: SectionDiff


# ── Stocks: financials (XBRL) ─────────────────────────────────────────────────


class MetricValue(TypedDict, total=False):
    value: float
    unit: str
    period_start: str
    period_end: str
    fiscal_year: int
    fiscal_period: str
    form: str
    accession: str
    filed_at: str


class ConceptBlock(TypedDict, total=False):
    taxonomy: str
    concept: str
    label: str
    description: str
    series: list[MetricValue]


class Financials(TypedDict, total=False):
    ticker: str
    cik: str
    name: str
    concepts: list[ConceptBlock]


class FinancialConcept(TypedDict, total=False):
    ticker: str
    cik: str
    taxonomy: str
    concept: str
    label: str
    description: str
    series: list[MetricValue]


class ScreenerRow(TypedDict, total=False):
    cik: str
    name: str
    value: float
    unit: str
    period_end: str
    accession: str


class ScreenerResult(TypedDict, total=False):
    taxonomy: str
    concept: str
    period: str
    unit: str
    label: str
    rows: list[ScreenerRow]
    meta: ListMeta


# ── Stocks: ratios ────────────────────────────────────────────────────────────


class FinancialRatio(TypedDict, total=False):
    fiscal_year: int
    fiscal_period: str
    period_end: str
    form: str
    accession: str
    gross_margin: float
    operating_margin: float
    net_margin: float
    return_on_equity: float
    return_on_assets: float
    debt_to_equity: float
    current_ratio: float
    quick_ratio: float
    asset_turnover: float
    free_cash_flow: float
    fcf_margin: float


class Ratios(TypedDict, total=False):
    ticker: str
    cik: str
    latest: FinancialRatio
    history: list[FinancialRatio]


# ── Stocks: events / ownership / compensation / insiders ──────────────────────


class EventFiling(TypedDict, total=False):
    accession: str
    filed_at: str
    accepted_at: str
    items: list[str]
    primary_document_url: str
    description: str


class OwnershipFiling(TypedDict, total=False):
    form: str
    accession: str
    filed_at: str
    primary_document_url: str
    description: str


class CompensationFiling(TypedDict, total=False):
    form: str
    accession: str
    filed_at: str
    period_end: str
    primary_document_url: str


class InsiderTransaction(TypedDict, total=False):
    accession: str
    filed_at: str
    reporter: str
    reporter_cik: str
    roles: list[str]
    officer_title: str
    security: str
    transaction_date: str
    transaction_code: str
    transaction_description: str
    direction: str
    shares: float
    price_per_share: float
    notional_usd: float
    shares_owned_after: float
    ownership: str
    derivative: bool


# ── Generic list envelope ─────────────────────────────────────────────────────


class ListResponse(TypedDict, total=False):
    """Envelope for paginated list endpoints: ``{"data": [...], "meta": {...}}``."""

    data: list[Any]
    meta: ListMeta


# ── Historical bars ───────────────────────────────────────────────────────────


class Bar(TypedDict, total=False):
    t: int
    o: float
    h: float
    l: float  # noqa: E741 - API JSON key for "low"
    c: float
    v: float


class BarsMeta(TypedDict, total=False):
    as_of: str
    next_cursor: str
    symbol: str
    interval: str


class BarsResponse(TypedDict, total=False):
    data: list[Bar]
    meta: BarsMeta


# ── Filers (13F) ──────────────────────────────────────────────────────────────


class HoldingPosition(TypedDict, total=False):
    issuer: str
    security_type: str
    cusip: str
    value_usd: float
    shares: float
    shares_type: str
    discretion: str


class Holdings(TypedDict, total=False):
    filer_cik: str
    filer_name: str
    accession: str
    filed_at: str
    period_end: str
    total_value_usd: float
    positions: list[HoldingPosition]
    meta: ListMeta


# ── Markets ───────────────────────────────────────────────────────────────────


class MarketStats(TypedDict, total=False):
    market_cap_usd: int
    listed_companies: int
    currency: str
    as_of: str


class Market(TypedDict, total=False):
    market: str
    name: str
    type: str
    timezone: str
    region: str
    exchanges: list[str]
    stats: MarketStats


class MarketStatus(TypedDict, total=False):
    market: str
    type: str
    is_open: bool
    state: str
    session: str
    next_open: str
    next_close: str
    timezone: str
    stats: MarketStats


class Break(TypedDict, total=False):
    open: str
    close: str


class HoursSpec(TypedDict, total=False):
    open: str
    close: str
    breaks: list[Break]


class ForexSession(TypedDict, total=False):
    name: str
    start: str
    end: str


class MarketHoursBlock(TypedDict, total=False):
    regular: HoursSpec
    pre_market: HoursSpec
    post_market: HoursSpec


class MarketHours(TypedDict, total=False):
    market: str
    type: str
    timezone: str
    hours: MarketHoursBlock
    opens_at: str
    closes_at: str
    sessions: list[ForexSession]
    exchanges: list[str]


class CalendarDay(TypedDict, total=False):
    date: str
    name: str
    kind: str
    state: str
    early_close: str


class MarketsListResponse(TypedDict, total=False):
    data: list[Market]
    meta: dict[str, Any]


class MarketsStatusAllResponse(TypedDict, total=False):
    data: list[MarketStatus]
    meta: dict[str, Any]


class MarketStatusResponse(TypedDict, total=False):
    data: MarketStatus
    meta: dict[str, Any]


class MarketHoursResponse(TypedDict, total=False):
    data: MarketHours
    meta: dict[str, Any]


class MarketCalendarResponse(TypedDict, total=False):
    data: list[CalendarDay]
    meta: dict[str, Any]


# ── DEX ───────────────────────────────────────────────────────────────────────


class WalletToken(TypedDict, total=False):
    contract_address: str
    symbol: str
    name: str
    decimals: int
    logo: str
    raw_balance: str
    balance: str
    native: bool


class WalletPortfolio(TypedDict, total=False):
    chain: str
    address: str
    tokens: list[WalletToken]
    count: int
    updated_at: int


# ── Economic calendar ─────────────────────────────────────────────────────────


class EconomicEvent(TypedDict, total=False):
    event_id: str
    name: str
    country: str
    currency: str
    agency: str
    impact: str
    scheduled_at: str
    actual: float | None
    previous: float | None
    consensus: float | None
    released_at: str | None


class EconomicCalendarFilter(TypedDict, total=False):
    from_: str
    to: str
    country: str
    impact: str
    agency: str
    event_id: str
    limit: int


class EconomicCalendarResponse(TypedDict, total=False):
    events: list[EconomicEvent]
    count: int
    filter: dict[str, Any]


# Convenience: anything accepted where a query value is expected.
QueryValue = Union[str, int, float, bool, None]
