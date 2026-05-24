"""``/v1/fnd/economic-calendar`` — US macro economic events."""

from __future__ import annotations

from ..types import EconomicCalendarResponse
from ._base import Req, _AsyncResource, _SyncResource


def _list(
    frm: str | None, to: str | None, country: str | None, impact: str | None,
    agency: str | None, event_id: str | None, limit: int | None,
) -> Req:
    return Req(
        "/v1/fnd/economic-calendar",
        {
            "from": frm, "to": to, "country": country, "impact": impact,
            "agency": agency, "event_id": event_id, "limit": limit,
        },
    )


class EconomicCalendarResource(_SyncResource):
    def list(
        self, *, from_: str | None = None, to: str | None = None,
        country: str | None = None, impact: str | None = None,
        agency: str | None = None, event_id: str | None = None,
        limit: int | None = None,
    ) -> EconomicCalendarResponse:
        return self._get(_list(from_, to, country, impact, agency, event_id, limit))


class AsyncEconomicCalendarResource(_AsyncResource):
    async def list(
        self, *, from_: str | None = None, to: str | None = None,
        country: str | None = None, impact: str | None = None,
        agency: str | None = None, event_id: str | None = None,
        limit: int | None = None,
    ) -> EconomicCalendarResponse:
        return await self._aget(_list(from_, to, country, impact, agency, event_id, limit))
