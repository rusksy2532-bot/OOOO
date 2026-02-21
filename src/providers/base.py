from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class TokenEvent:
    event_type: Literal[
        "token_created",
        "trade",
        "curve_progress",
        "migration",
        "lp_add",
        "lp_remove",
        "holder_snapshot",
    ]
    mint: str
    timestamp: int
    data: dict


@dataclass
class TokenFeatures:
    mint: str
    snapshot_ts: int
    price_usd: Optional[float] = None
    market_cap_usd: Optional[float] = None
    volume_1h: Optional[float] = None
    volume_24h: Optional[float] = None
    age_minutes: Optional[float] = None
    curve_progress_pct: Optional[float] = None
    migrated: bool = False
    delta_5m_pct: Optional[float] = None
    delta_1h_pct: Optional[float] = None
    buys_5m: Optional[int] = None
    sells_5m: Optional[int] = None
    buy_ratio_5m: Optional[float] = None
    volume_surge: Optional[float] = None
    top10_pct: Optional[float] = None
    top1_pct: Optional[float] = None
    bundle_count: Optional[int] = None
    bundle_supply_pct: Optional[float] = None
    fresh_holders_pct: Optional[float] = None
    sniper_supply_pct: Optional[float] = None
    dev_holding_pct: Optional[float] = None
    diamond_hands_pct: Optional[float] = None
    early_dump_pct: Optional[float] = None
    avg_roi_early_buyers: Optional[float] = None
    avg_hold_time_minutes: Optional[float] = None
    dev_past_tokens: Optional[int] = None
    dev_migrated_count: Optional[int] = None
    dev_dead_count: Optional[int] = None
    dev_median_roi: Optional[float] = None


@dataclass
class FilterResult:
    passed: bool
    reasons: list[str]


@dataclass
class ScoringResult:
    total_score: float
    market_score: float
    risk_score: float
    dev_score: float
    pressure_score: float
    contributions: dict


class DataProvider:
    """Базовый интерфейс провайдера данных."""

    def get_events(self, mint: str) -> list[TokenEvent]:
        raise NotImplementedError
