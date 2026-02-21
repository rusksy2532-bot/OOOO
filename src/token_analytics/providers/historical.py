from __future__ import annotations

import json
from pathlib import Path

from token_analytics.models.types import Event, EventType, TokenTimeline
from token_analytics.providers.base import DataProvider


class HistoricalFileProvider(DataProvider):
    def __init__(self, dataset_path: str) -> None:
        self.dataset_path = Path(dataset_path)
        with self.dataset_path.open("r", encoding="utf-8") as handle:
            self.raw = json.load(handle)

    def _build_timeline(self, row: dict) -> TokenTimeline:
        events = [
            Event(
                ts=e["ts"],
                token_mint=row["token_mint"],
                event_type=EventType(e["event_type"]),
                payload=e.get("payload", {}),
            )
            for e in sorted(row.get("events", []), key=lambda item: item["ts"])
        ]
        return TokenTimeline(
            token_name=row.get("token_name", row["token_mint"]),
            token_mint=row["token_mint"],
            deployer=row.get("deployer"),
            created_ts=row["created_ts"],
            events=events,
        )

    def get_token_timeline(self, token_mint: str) -> TokenTimeline:
        for row in self.raw["tokens"]:
            if row["token_mint"] == token_mint:
                return self._build_timeline(row)
        raise KeyError(f"Token not found: {token_mint}")

    def iter_token_timelines(self) -> list[TokenTimeline]:
        return [self._build_timeline(row) for row in self.raw["tokens"]]
