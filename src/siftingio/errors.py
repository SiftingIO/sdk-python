"""Exception types raised by the SDK.

Everything raised by the SDK derives from :class:`SiftingError`, so a single
``except SiftingError`` covers all cases. HTTP-level failures surface the API's
machine-readable ``error`` code as :attr:`SiftingAPIError.code`.
"""

from __future__ import annotations

from typing import Any


class SiftingError(Exception):
    """Base class for every error raised by the SDK."""


class SiftingAPIError(SiftingError):
    """Raised when the API returns a non-2xx response.

    Attributes:
        status: HTTP status code (e.g. 401, 404, 429).
        code: Machine-readable code from the response body's ``error`` field.
        request_id: ``X-Request-Id`` response header, if present.
        retry_after: Seconds to wait before retrying (429), if known.
        body: The full parsed error body, including any non-standard fields.
    """

    def __init__(
        self,
        *,
        status: int,
        code: str,
        message: str,
        request_id: str | None = None,
        retry_after: float | None = None,
        body: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(f"[{status} {code}] {message}")
        self.status = status
        self.code = code
        self.message = message
        self.request_id = request_id
        self.retry_after = retry_after
        self.body = body


class SiftingConnectionError(SiftingError):
    """Raised when no HTTP response was produced (network failure, timeout)."""

    def __init__(self, message: str, *, timeout: bool = False) -> None:
        super().__init__(message)
        self.timeout = timeout
