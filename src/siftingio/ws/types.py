"""WebSocket protocol types for ``wss://stream.sifting.io/ws/v1``."""

from __future__ import annotations

from typing import Literal, TypedDict

WsProduct = Literal["cex", "dex", "fx", "us", "tvl"]
WsEvent = Literal["open", "close", "reconnect", "tick", "tvl", "ack", "pong", "error", "message"]


class WsTick(TypedDict, total=False):
    f: Literal["tick"]
    s: str
    p: str
    P: str
    b: str
    B: str
    a: str
    A: str
    t: int


class WsTVL(TypedDict, total=False):
    f: Literal["tvl"]
    s: str
    usd: str
    r0: str
    r1: str
    n: int
    t: int


class WsAck(TypedDict, total=False):
    f: Literal["ack"]


class WsPong(TypedDict, total=False):
    f: Literal["pong"]


class WsErrorFrame(TypedDict, total=False):
    f: Literal["error"]
    code: str
    message: str
    limit: int
