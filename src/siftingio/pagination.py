"""Cursor auto-pagination helpers for both sync and async list endpoints.

Pass a callable that fetches one page given a cursor (``None`` for the first
page); the SDK's list methods plug straight in::

    for filing in auto_paginate(lambda cursor: client.stocks.filings("AAPL", cursor=cursor)):
        print(filing["accession"])

    async for filing in aauto_paginate(
        lambda cursor: client.stocks.filings("AAPL", cursor=cursor)
    ):
        ...
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Iterator, Mapping
from typing import (
    Any,
    Callable,
)


def _page_items(page: Mapping[str, Any]) -> list[Any]:
    return list(page.get("data", []))


def _next_cursor(page: Mapping[str, Any]) -> str | None:
    meta = page.get("meta") or {}
    return meta.get("next_cursor")


def auto_paginate(
    fetch_page: Callable[[str | None], Mapping[str, Any]],
    max_items: int | None = None,
) -> Iterator[Any]:
    """Yield items across all pages of a cursor-based endpoint (sync)."""
    cursor: str | None = None
    count = 0
    while True:
        page = fetch_page(cursor)
        for item in _page_items(page):
            yield item
            count += 1
            if max_items is not None and count >= max_items:
                return
        cursor = _next_cursor(page)
        if not cursor:
            return


def collect_all(
    fetch_page: Callable[[str | None], Mapping[str, Any]],
    max_items: int | None = None,
) -> list[Any]:
    """Collect every page into a single list (sync)."""
    return list(auto_paginate(fetch_page, max_items))


async def aauto_paginate(
    fetch_page: Callable[[str | None], Awaitable[Mapping[str, Any]]],
    max_items: int | None = None,
) -> AsyncIterator[Any]:
    """Yield items across all pages of a cursor-based endpoint (async)."""
    cursor: str | None = None
    count = 0
    while True:
        page = await fetch_page(cursor)
        for item in _page_items(page):
            yield item
            count += 1
            if max_items is not None and count >= max_items:
                return
        cursor = _next_cursor(page)
        if not cursor:
            return


async def acollect_all(
    fetch_page: Callable[[str | None], Awaitable[Mapping[str, Any]]],
    max_items: int | None = None,
) -> list[Any]:
    """Collect every page into a single list (async)."""
    return [item async for item in aauto_paginate(fetch_page, max_items)]
