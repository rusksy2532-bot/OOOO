from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import mean

from .models import Event, TokenFeatures


@dataclass(slots=True)
class FeatureExtractor:
    volume_surge_lookback_hours: int = 6

    def extract(self, token_mint: str, token_name: str, events: list[Event]) -> TokenFeatures:
        events = sorted(events, key=lambda e: e.timestamp)
        now = events[-1].timestamp
        created = min((e.timestamp for e in events if e.event_type == "token_created"), default=events[0].timestamp)
        trades = [e for e in events if e.event_type == "trade"]

        volumes = {"5m": 0.0, "15m": 0.0, "1h": 0.0, "24h": 0.0}
        buys = {"5m": 0, "15m": 0, "1h": 0}
        sells = {"5m": 0, "15m": 0, "1h": 0}
        for t in trades:
            dt = now - t.timestamp
            vol = float(t.data.get("volume_usd") or 0.0)
            side = str(t.data.get("side") or "buy")
            if dt <= timedelta(minutes=5):
                volumes["5m"] += vol
                buys["5m"] += side == "buy"
                sells["5m"] += side == "sell"
            if dt <= timedelta(minutes=15):
                volumes["15m"] += vol
                buys["15m"] += side == "buy"
                sells["15m"] += side == "sell"
            if dt <= timedelta(hours=1):
                volumes["1h"] += vol
                buys["1h"] += side == "buy"
                sells["1h"] += side == "sell"
            if dt <= timedelta(hours=24):
                volumes["24h"] += vol

        last_price = float(trades[-1].data.get("price") if trades else 0.0)
        px_5m = _price_at(trades, now - timedelta(minutes=5))
        px_1h = _price_at(trades, now - timedelta(hours=1))
        delta_5m = (last_price / px_5m - 1) * 100 if px_5m else None
        delta_1h = (last_price / px_1h - 1) * 100 if px_1h else None

        hourly_bins = defaultdict(float)
        for t in trades:
            hour = t.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_bins[hour] += float(t.data.get("volume_usd") or 0.0)
        past_hours = sorted(hourly_bins)[-self.volume_surge_lookback_hours - 1 : -1]
        avg_hour = mean([hourly_bins[h] for h in past_hours]) if past_hours else 0.0
        surge = (volumes["1h"] / avg_hour) if avg_hour else None

        latest_snapshot = next((e for e in reversed(events) if e.event_type == "holder_snapshot"), None)
        curve = next((e for e in reversed(events) if e.event_type == "curve_progress"), None)
        dev = next((e for e in reversed(events) if e.event_type == "dev_history"), None)

        values = {
            "price": last_price,
            "curve_mc": float(curve.data.get("curve_mc") if curve else 0),
            "volume_24h": volumes["24h"],
            "volume_1h": volumes["1h"],
            "age_minutes": (now - created).total_seconds() / 60,
            "delta_5m_pct": delta_5m,
            "delta_1h_pct": delta_1h,
            "curve_progress_pct": float(curve.data.get("progress_pct")) if curve else None,
            "migrated": bool(curve and curve.data.get("migrated")),
            "buy_ratio_5m": _ratio(buys["5m"], sells["5m"]),
            "buy_ratio_15m": _ratio(buys["15m"], sells["15m"]),
            "buy_ratio_1h": _ratio(buys["1h"], sells["1h"]),
            "volume_surge": surge,
            "top10_pct": latest_snapshot.data.get("top10_pct") if latest_snapshot else None,
            "top1_pct": latest_snapshot.data.get("top1_pct") if latest_snapshot else None,
            "bundle_wallets_count": latest_snapshot.data.get("bundle_wallets_count") if latest_snapshot else None,
            "bundle_supply_pct": latest_snapshot.data.get("bundle_supply_pct") if latest_snapshot else None,
            "fresh_top_holders_pct": latest_snapshot.data.get("fresh_top_holders_pct") if latest_snapshot else None,
            "sniper_supply_pct": latest_snapshot.data.get("sniper_supply_pct") if latest_snapshot else None,
            "dev_holding_pct": latest_snapshot.data.get("dev_holding_pct") if latest_snapshot else None,
            "diamond_hands_pct": latest_snapshot.data.get("diamond_hands_pct") if latest_snapshot else None,
            "early_dump_pct": latest_snapshot.data.get("early_dump_pct") if latest_snapshot else None,
            "avg_roi_early_buyers_pct": latest_snapshot.data.get("avg_roi_early_buyers_pct") if latest_snapshot else None,
            "avg_hold_minutes_early_buyers": latest_snapshot.data.get("avg_hold_minutes_early_buyers") if latest_snapshot else None,
            "dev_past_tokens_count": dev.data.get("past_tokens_count") if dev else None,
            "dev_migrated_count": dev.data.get("migrated_count") if dev else None,
            "dev_dead_on_curve_count": dev.data.get("dead_on_curve_count") if dev else None,
            "deployer_median_roi_pct": dev.data.get("median_roi_pct") if dev else None,
        }
        return TokenFeatures(token_mint=token_mint, token_name=token_name, computed_at=now, values=values)


def _ratio(buys: int, sells: int) -> float | None:
    total = buys + sells
    return buys / total if total else None


def _price_at(trades: list[Event], cutoff: datetime) -> float | None:
    candidates = [t for t in trades if t.timestamp <= cutoff]
    if not candidates:
        return None
    return float(candidates[-1].data.get("price") or 0.0)
