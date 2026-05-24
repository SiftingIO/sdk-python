# CLAUDE.md — `siftingio` (Python)

Guidance for maintaining and extending the SiftingIO Python SDK. It wraps the
**data plane only** — the API-key-authenticated `/v1/*` endpoints from
`SiftingIO_API_V1/router/router.go`. It does **not** wrap the `/ops/v1/*`
control plane (auth, billing, account); that is the SPA's surface.

The package mirrors the TypeScript SDK (`../typescript`) endpoint-for-endpoint,
so keep the two in sync when the API changes.

## Layout

```
src/siftingio/
  __init__.py        — public surface + __version__ (hatch reads this)
  client.py          — SiftingClient (sync) + AsyncSiftingClient (async)
  _transport.py      — _SyncTransport / _AsyncTransport: auth, gzip, retries, errors
  errors.py          — SiftingError / SiftingAPIError / SiftingConnectionError
  types.py           — TypedDict response shapes + Literal unions
  pagination.py      — auto_paginate / collect_all (+ async aauto_paginate / acollect_all)
  resources/
    _base.py         — Req namedtuple, seg(), _SyncResource / _AsyncResource bases
    *.py             — one module per namespace; see "sync/async pattern" below
  ws/
    client.py        — AsyncSiftingSocket + thread-backed sync SiftingSocket
    types.py         — WebSocket protocol TypedDicts
tests/               — pytest (httpx.MockTransport for REST, a local ws server for WS)
examples/            — runnable rest.py / websocket.py
```

## The sync/async pattern (important)

Each resource module has **one request-builder per endpoint** (`_profile`,
`_filings`, …) that returns a `Req(path, params)` — this is the single source of
truth for routing. Then two thin classes, `XResource` (sync) and
`AsyncXResource` (async), each expose one-line methods that call `self._get` /
`self._aget`. When you add an endpoint you write: one builder + two one-liners +
a `TypedDict`. The actual logic lives only in the builder.

Python keyword collisions (`from`) use a trailing-underscore kwarg (`from_`) on
the public method; the builder maps it to the real query key (`"from"`).

## Commands

```bash
python -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q          # tests (REST + WebSocket)
.venv/bin/mypy src/siftingio # strict type check
.venv/bin/ruff check src     # lint
.venv/bin/python -m build --wheel   # build distribution
```

## Adding or changing an endpoint

The Go API is the source of truth — read `router.go` for the route and
`model/fundamentals.go` (or the relevant `service/*`) for the response struct.

1. Add a `_req` builder in the matching `resources/*.py`, encoding every dynamic
   segment with `seg(...)` and listing query params in the params dict.
2. Add a `TypedDict` in `types.py` mirroring the Go struct field-for-field
   (JSON casing, `total=False`).
3. Add the sync method to `XResource` and the async method to `AsyncXResource`.
4. Re-export new public types from `__init__.py` if user-facing.
5. Add a test in `tests/` using `httpx.MockTransport`.
6. Run `pytest`, `mypy`, `ruff`. Mirror the change in the TypeScript SDK.

### Gzip-required endpoints

`stocks.screener`, `stocks.financials`, `stocks.financial_concept`,
`stocks.bars`, `forex.bars`, `crypto.bars` return 406 without
`Accept-Encoding: gzip`. The transport sends it on every request and httpx
decompresses transparently, so no per-method handling is needed.

## Conventions

- Runtime deps are only `httpx` + `websockets`. Don't add more without cause.
- `from __future__ import annotations` at the top of every module — this is what
  lets us use `list[...]` / `X | None` while still supporting Python 3.9.
- Responses are returned as raw dicts (typed via `TypedDict`); we don't validate
  or construct models at runtime. `mypy` runs with `warn_return_any = false`
  because of this.
- Resources never import httpx — only the transport does.
- Semver, mirrored with the TS package. Keep `CHANGELOG.md` and `__version__`
  in step.

## Releasing

`pytest && mypy src/siftingio && ruff check src` → bump `__version__` →
update `CHANGELOG.md` → `python -m build` → `twine upload dist/*`.
