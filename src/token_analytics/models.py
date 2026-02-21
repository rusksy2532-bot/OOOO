from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Event:
    timestamp: datetime
    event_type: str
    token_mint: str
    data: dict[str, Any]


@dataclass(slots=True)
class Trade:
    timestamp: datetime
    token_mint: str
    side: str
    price: float
    volume_usd: float
    wallet: str


@dataclass(slots=True)
class TokenFeatures:
    token_mint: str
    token_name: str
    computed_at: datetime
    values: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class FilterResult:
    passed: bool
    reasons: list[str]


@dataclass(slots=True)
class ScoreResult:
    score: float
    sub_scores: dict[str, float]
    contributions: dict[str, float]
    tp_probabilities: dict[str, float]


@dataclass(slots=True)
class Position:
    token_mint: str
    entry_time: datetime
    entry_price: float
    size_usd: float


@dataclass(slots=True)
class TradeResult:
    token_mint: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    roi_pct: float
    exit_reason: str
    hold_minutes: float


@dataclass(slots=True)
class BacktestSummary:
    total_trades: int
    winrate: float
    avg_roi: float
    median_roi: float
    profit_factor: float
    max_drawdown: float
    expectancy: float
    brier_tp2: float | None
