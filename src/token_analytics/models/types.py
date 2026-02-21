from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventType(str, Enum):
    TOKEN_CREATED = "token_created"
    TRADE = "trade"
    CURVE_PROGRESS = "curve_progress"
    MIGRATION = "migration"
    LP_ADD = "lp_add"
    LP_REMOVE = "lp_remove"
    HOLDER_SNAPSHOT = "holder_snapshot"


@dataclass(slots=True)
class Event:
    ts: int
    token_mint: str
    event_type: EventType
    payload: dict[str, Any]


@dataclass(slots=True)
class TokenTimeline:
    token_name: str
    token_mint: str
    deployer: str | None
    created_ts: int
    events: list[Event] = field(default_factory=list)


@dataclass(slots=True)
class FeatureVector:
    token_mint: str
    values: dict[str, float | int | bool | str | None]


@dataclass(slots=True)
class FilterResult:
    passed: bool
    reasons: list[str]


@dataclass(slots=True)
class ScoreResult:
    total_score: float
    subscores: dict[str, float]
    contributions: dict[str, float]


@dataclass(slots=True)
class TradeResult:
    token_mint: str
    entry_ts: int
    exit_ts: int
    entry_price: float
    exit_price: float
    qty: float
    roi_pct: float
    reason_exit: str


@dataclass(slots=True)
class BacktestSummary:
    total_trades: int
    winrate: float
    avg_roi_pct: float
    median_roi_pct: float
    profit_factor: float
    max_drawdown_pct: float
    expectancy_pct: float
    avg_holding_seconds: float
    calibration: dict[str, float]
