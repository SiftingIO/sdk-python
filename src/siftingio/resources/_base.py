"""Shared plumbing for resource classes.

Each endpoint's path + params are built once by a module-level ``_req`` helper
(the single source of truth). The sync and async resource classes are thin:
they call :meth:`_SyncResource._get` / :meth:`_AsyncResource._aget` with that
:class:`Req`. This keeps the duplication between sync and async to mechanical
one-line method bodies while the actual routing logic lives in one place.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, NamedTuple
from urllib.parse import quote

from .._transport import _AsyncTransport, _SyncTransport


class Req(NamedTuple):
    """A built request: a path and optional query params."""

    path: str
    params: Mapping[str, Any] | None = None


def seg(value: str) -> str:
    """URL-encode a single path segment."""
    return quote(str(value), safe="")


class _SyncResource:
    def __init__(self, transport: _SyncTransport) -> None:
        self._t = transport

    def _get(self, req: Req) -> Any:
        return self._t.get(req.path, req.params)


class _AsyncResource:
    def __init__(self, transport: _AsyncTransport) -> None:
        self._t = transport

    async def _aget(self, req: Req) -> Any:
        return await self._t.get(req.path, req.params)
