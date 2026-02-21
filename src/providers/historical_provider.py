from __future__ import annotations

import json
from pathlib import Path

from src.providers.base import DataProvider, TokenEvent


class HistoricalProvider(DataProvider):
    """Провайдер исторических событий из локальных JSON-файлов."""

    def __init__(self, raw_dir: str = "data/raw"):
        self.raw_dir = Path(raw_dir)

    def get_events(self, mint: str) -> list[TokenEvent]:
        path = self.raw_dir / f"{mint}.json"
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        events = []
        for row in payload.get("events", []):
            events.append(
                TokenEvent(
                    event_type=row["event_type"],
                    mint=row.get("mint", mint),
                    timestamp=row["timestamp"],
                    data=row.get("data", {}),
                )
            )
        return sorted(events, key=lambda item: item.timestamp)

    def list_mints(self) -> list[str]:
        return [p.stem for p in sorted(self.raw_dir.glob("*.json"))]
