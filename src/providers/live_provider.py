from __future__ import annotations

from src.providers.base import DataProvider, TokenEvent


class LiveProvider(DataProvider):
    """Заглушка live-провайдера для интеграции RPC/WS источников."""

    def get_events(self, mint: str) -> list[TokenEvent]:
        # Здесь должна быть интеграция с Helius/Pump.fun/Birdeye.
        return []
