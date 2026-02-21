from __future__ import annotations

from abc import ABC, abstractmethod

from token_analytics.models.types import TokenTimeline


class DataProvider(ABC):
    @abstractmethod
    def get_token_timeline(self, token_mint: str) -> TokenTimeline:
        raise NotImplementedError

    @abstractmethod
    def iter_token_timelines(self) -> list[TokenTimeline]:
        raise NotImplementedError
