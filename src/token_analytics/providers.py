from __future__ import annotations

import csv
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import Event


class DataProvider(ABC):
    @abstractmethod
    def stream_events(self, token_mint: str | None = None) -> Iterable[Event]:
        raise NotImplementedError


@dataclass(slots=True)
class HistoricalFileProvider(DataProvider):
    events_path: Path

    def stream_events(self, token_mint: str | None = None) -> Iterable[Event]:
        if self.events_path.suffix == ".json":
            rows = json.loads(self.events_path.read_text())
        else:
            with self.events_path.open() as f:
                rows = list(csv.DictReader(f))

        for row in rows:
            if token_mint and row["token_mint"] != token_mint:
                continue
            yield Event(
                timestamp=datetime.fromisoformat(row["timestamp"]),
                event_type=row["event_type"],
                token_mint=row["token_mint"],
                data={k: _coerce(v) for k, v in row.items() if k not in {"timestamp", "event_type", "token_mint"}},
            )


@dataclass(slots=True)
class LiveRpcWsProvider(DataProvider):
    rpc_url: str
    ws_url: str

    def stream_events(self, token_mint: str | None = None) -> Iterable[Event]:
        raise NotImplementedError(
            "Live provider is an interface placeholder. Integrate Solana RPC logsSubscribe/accountSubscribe and Pump.fun events decoder here."
        )


def _coerce(v: str):
    if isinstance(v, (int, float, bool)):
        return v
    if v is None or v in {"", "None", "null"}:
        return None
    try:
        return float(v)
    except ValueError:
        return v
