from __future__ import annotations

from token_analytics.models.types import TokenTimeline
from token_analytics.providers.base import DataProvider


class LiveSolanaProvider(DataProvider):
    """Stub for RPC/WS ingestion.

    In production this class should connect to Solana RPC/WS and transform raw events
    into canonical event types.
    """

    def __init__(self, rpc_url: str, ws_url: str) -> None:
        self.rpc_url = rpc_url
        self.ws_url = ws_url

    def get_token_timeline(self, token_mint: str) -> TokenTimeline:
        raise NotImplementedError("Live provider is a scaffold in this repository")

    def iter_token_timelines(self) -> list[TokenTimeline]:
        raise NotImplementedError("Live provider is a scaffold in this repository")
