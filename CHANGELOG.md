# Changelog

All notable changes to `siftingio` are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com); the project adheres to SemVer.

## [0.1.2] — 2026-06-22

### Added
- `commodities` namespace with `bars(...)` for OHLC commodity/metal bars
  (sync `CommoditiesResource`, async `AsyncCommoditiesResource`).
- `order` parameter (`"asc"` / `"desc"`) on `forex.bars` and `commodities.bars`.

## [0.1.1]

### Changed
- Ticker name updates.

## [0.1.0]

Initial release.

### Added
- `SiftingClient` (sync) and `AsyncSiftingClient` (async) covering the full data
  plane: `last`, `stocks`, `filers`, `markets`, `forex`, `crypto`, `dex`,
  `economic_calendar`.
- Live WebSocket clients: `AsyncSiftingSocket` (asyncio) and a thread-backed
  sync `SiftingSocket`, both with auto-reconnect and subscription replay.
- Cursor auto-pagination: `auto_paginate` / `collect_all` and async
  `aauto_paginate` / `acollect_all`.
- Automatic retries (429/5xx with `Retry-After`), gzip negotiation, per-request
  timeouts, and typed errors (`SiftingAPIError`, `SiftingConnectionError`).
- Full type hints (`py.typed`); responses typed via `TypedDict`.
- Python 3.9+; depends only on `httpx` and `websockets`.
