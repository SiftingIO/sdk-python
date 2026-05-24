"""``/v1/fnd/filers/*`` — 13F institutional holdings."""

from __future__ import annotations

from ..types import Holdings
from ._base import Req, _AsyncResource, _SyncResource, seg


def _holdings(filer: str, cursor: str | None, limit: int | None) -> Req:
    return Req(f"/v1/fnd/filers/{seg(filer)}/holdings", {"cursor": cursor, "limit": limit})


class FilersResource(_SyncResource):
    def holdings(
        self, filer: str, *, cursor: str | None = None, limit: int | None = None
    ) -> Holdings:
        """Latest 13F-HR positions. ``filer`` accepts a CIK (numeric) or a ticker."""
        return self._get(_holdings(filer, cursor, limit))


class AsyncFilersResource(_AsyncResource):
    async def holdings(
        self, filer: str, *, cursor: str | None = None, limit: int | None = None
    ) -> Holdings:
        return await self._aget(_holdings(filer, cursor, limit))
