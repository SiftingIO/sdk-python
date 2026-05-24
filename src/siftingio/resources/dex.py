"""``/v1/fnd/dex/*`` — on-chain wallet portfolios across EVM chains."""

from __future__ import annotations

from ..types import WalletPortfolio
from ._base import Req, _AsyncResource, _SyncResource, seg


def _wallet(chain: str, address: str) -> Req:
    return Req(f"/v1/fnd/dex/wallet/{seg(chain)}/{seg(address)}")


class DexResource(_SyncResource):
    def wallet(self, chain: str, address: str) -> WalletPortfolio:
        """Token holdings for a wallet, e.g. ``wallet("eth", "0x...")``."""
        return self._get(_wallet(chain, address))


class AsyncDexResource(_AsyncResource):
    async def wallet(self, chain: str, address: str) -> WalletPortfolio:
        return await self._aget(_wallet(chain, address))
