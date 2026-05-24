"""Internal HTTP transport. One sync and one async variant, sharing config,
header/URL building, gzip negotiation, retry policy, and error decoding.

Resources never touch httpx directly — they call :meth:`_SyncTransport.get` /
:meth:`_AsyncTransport.get`, which return parsed JSON or raise a typed error.
"""

from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Awaitable, Mapping
from typing import Any, Callable, Union
from urllib.parse import quote

import httpx

from .errors import SiftingAPIError, SiftingConnectionError

DEFAULT_BASE_URL = "https://api.sifting.io"
DEFAULT_WS_URL = "wss://stream.sifting.io/ws/v1"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2

SyncKeyProvider = Callable[[], str]
AsyncKeyProvider = Callable[[], Union[str, Awaitable[str]]]


def _clean_params(params: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """Drop ``None`` values and normalize booleans to lowercase strings."""
    if not params:
        return None
    out: dict[str, Any] = {}
    for key, value in params.items():
        if value is None:
            continue
        out[key] = "true" if value is True else "false" if value is False else value
    return out or None


class _BaseTransport:
    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str | None,
        ws_url: str | None,
        timeout: float | None,
        max_retries: int | None,
        headers: Mapping[str, str] | None,
    ) -> None:
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.ws_url = ws_url or DEFAULT_WS_URL
        self._api_key = api_key
        self.timeout = DEFAULT_TIMEOUT if timeout is None else timeout
        self.max_retries = DEFAULT_MAX_RETRIES if max_retries is None else max_retries
        self._extra_headers = dict(headers or {})

    def _headers(self, key: str | None) -> dict[str, str]:
        h = {
            "Accept": "application/json",
            # Required by the six heavy endpoints; harmless elsewhere. httpx
            # decompresses gzip responses transparently.
            "Accept-Encoding": "gzip",
            **self._extra_headers,
        }
        if key:
            h["X-API-Key"] = key
        return h

    @staticmethod
    def _backoff(attempt: int) -> float:
        return random.random() * min(10.0, 0.2 * 2 ** (attempt - 1))

    @staticmethod
    def _retryable(status: int) -> bool:
        return status == 429 or (500 <= status < 600 and status != 501)

    def _decode_error(self, response: httpx.Response) -> SiftingAPIError:
        code = f"http_{response.status_code}"
        message = f"Request failed with status {response.status_code}"
        body: dict[str, Any] | None = None
        try:
            parsed = response.json()
            if isinstance(parsed, dict):
                body = parsed
                if isinstance(parsed.get("error"), str):
                    code = parsed["error"]
                if isinstance(parsed.get("message"), str):
                    message = parsed["message"]
                elif isinstance(parsed.get("error"), str):
                    message = parsed["error"]
        except ValueError:
            pass  # Non-JSON error body (e.g. a gateway HTML page).

        retry_after = _parse_retry_after(response.headers.get("Retry-After"))
        if retry_after is None and body:
            for field in ("retry_after", "retry_after_seconds"):
                if isinstance(body.get(field), (int, float)):
                    retry_after = float(body[field])
                    break

        return SiftingAPIError(
            status=response.status_code,
            code=code,
            message=message,
            request_id=response.headers.get("X-Request-Id"),
            retry_after=retry_after,
            body=body,
        )

    def ws_connect_url(self, key: str | None) -> str:
        if not key:
            return self.ws_url
        sep = "&" if "?" in self.ws_url else "?"
        return f"{self.ws_url}{sep}key={quote(key, safe='')}"


def _parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


class _SyncTransport(_BaseTransport):
    def __init__(
        self,
        *,
        get_api_key: SyncKeyProvider | None = None,
        http_client: httpx.Client | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._get_api_key = get_api_key
        self._client = http_client or httpx.Client(timeout=self.timeout)
        self._owns_client = http_client is None

    def _resolve_key(self) -> str | None:
        if self._get_api_key is not None:
            return self._get_api_key()
        return self._api_key

    def get(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        url = self.base_url + path
        headers = self._headers(self._resolve_key())
        clean = _clean_params(params)

        attempt = 0
        while True:
            try:
                response = self._client.get(url, params=clean, headers=headers)
            except httpx.TimeoutException as exc:
                if attempt < self.max_retries:
                    attempt += 1
                    time.sleep(self._backoff(attempt))
                    continue
                msg = str(exc) or "Request timed out."
                raise SiftingConnectionError(msg, timeout=True) from exc
            except httpx.HTTPError as exc:
                if attempt < self.max_retries:
                    attempt += 1
                    time.sleep(self._backoff(attempt))
                    continue
                raise SiftingConnectionError(str(exc) or "Network request failed.") from exc

            if response.is_success:
                return response.json()

            if self._retryable(response.status_code) and attempt < self.max_retries:
                attempt += 1
                retry_after = _parse_retry_after(response.headers.get("Retry-After"))
                time.sleep(retry_after if retry_after is not None else self._backoff(attempt))
                continue

            raise self._decode_error(response)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()


class _AsyncTransport(_BaseTransport):
    def __init__(
        self,
        *,
        get_api_key: AsyncKeyProvider | None = None,
        http_client: httpx.AsyncClient | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._get_api_key = get_api_key
        self._client = http_client or httpx.AsyncClient(timeout=self.timeout)
        self._owns_client = http_client is None

    async def _resolve_key(self) -> str | None:
        if self._get_api_key is not None:
            result = self._get_api_key()
            if asyncio.iscoroutine(result):
                return await result
            return result  # type: ignore[return-value]
        return self._api_key

    async def get(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        url = self.base_url + path
        headers = self._headers(await self._resolve_key())
        clean = _clean_params(params)

        attempt = 0
        while True:
            try:
                response = await self._client.get(url, params=clean, headers=headers)
            except httpx.TimeoutException as exc:
                if attempt < self.max_retries:
                    attempt += 1
                    await asyncio.sleep(self._backoff(attempt))
                    continue
                msg = str(exc) or "Request timed out."
                raise SiftingConnectionError(msg, timeout=True) from exc
            except httpx.HTTPError as exc:
                if attempt < self.max_retries:
                    attempt += 1
                    await asyncio.sleep(self._backoff(attempt))
                    continue
                raise SiftingConnectionError(str(exc) or "Network request failed.") from exc

            if response.is_success:
                return response.json()

            if self._retryable(response.status_code) and attempt < self.max_retries:
                attempt += 1
                retry_after = _parse_retry_after(response.headers.get("Retry-After"))
                await asyncio.sleep(
                    retry_after if retry_after is not None else self._backoff(attempt)
                )
                continue

            raise self._decode_error(response)

    async def ws_connect_url_resolved(self) -> str:
        """Build the authenticated WebSocket URL (key in query)."""
        return self.ws_connect_url(await self._resolve_key())

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()
