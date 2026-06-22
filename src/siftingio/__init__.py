"""siftingio — official Python SDK for the SiftingIO market data API.

>>> from siftingio import SiftingClient
>>> client = SiftingClient(api_key="sft_...")
>>> client.last.trade("crypto", "BTCUSD")   # doctest: +SKIP
"""

from __future__ import annotations

__version__ = "0.1.2"

from .client import AsyncSiftingClient, SiftingClient
from .errors import SiftingAPIError, SiftingConnectionError, SiftingError
from .pagination import aauto_paginate, acollect_all, auto_paginate, collect_all
from .ws.client import AsyncSiftingSocket, SiftingSocket

__all__ = [
    "__version__",
    "SiftingClient",
    "AsyncSiftingClient",
    "SiftingSocket",
    "AsyncSiftingSocket",
    "SiftingError",
    "SiftingAPIError",
    "SiftingConnectionError",
    "auto_paginate",
    "collect_all",
    "aauto_paginate",
    "acollect_all",
]
