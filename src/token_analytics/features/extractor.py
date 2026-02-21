from __future__ import annotations

from collections import defaultdict
from statistics import mean

from token_analytics.models.types import EventType, FeatureVector, TokenTimeline


class FeatureExtractor:
    def extract(self, timeline: TokenTimeline) -> FeatureVector:
        trades = [e for e in timeline.events if e.event_type == EventType.TRADE]
        curve_events = [e for e in timeline.events if e.event_type == EventType.CURVE_PROGRESS]
        migration_events = [e for e in timeline.events if e.event_type == EventType.MIGRATION]

        if not trades:
            return FeatureVector(token_mint=timeline.token_mint, values={"age_minutes": 0, "migrated": False})

        first_ts = timeline.created_ts
        last_ts = trades[-1].ts
        age_minutes = max(0, (last_ts - first_ts) / 60)
        last_trade = trades[-1].payload
        price = last_trade.get("price")
        curve_mc = last_trade.get("curve_mc")

        def volume_in_window(seconds: int) -> float:
            low = last_ts - seconds
            return sum(float(t.payload.get("usd_size", 0)) for t in trades if t.ts >= low)

        vol_1h = volume_in_window(3600)
        vol_15m = volume_in_window(900)
        vol_5m = volume_in_window(300)

        hourly_buckets = defaultdict(float)
        for t in trades:
            bucket = (t.ts - first_ts) // 3600
            hourly_buckets[bucket] += float(t.payload.get("usd_size", 0))
        avg_hourly = mean(hourly_buckets.values()) if hourly_buckets else 0
        volume_surge = (vol_1h / avg_hourly) if avg_hourly > 0 else None

        window_metrics = {}
        for label, sec in [("5m", 300), ("15m", 900), ("1h", 3600)]:
            low = last_ts - sec
            subset = [t for t in trades if t.ts >= low]
            buys = sum(float(t.payload.get("usd_size", 0)) for t in subset if t.payload.get("side") == "buy")
            sells = sum(float(t.payload.get("usd_size", 0)) for t in subset if t.payload.get("side") == "sell")
            window_metrics[f"buys_{label}"] = buys
            window_metrics[f"sells_{label}"] = sells
            window_metrics[f"buy_ratio_{label}"] = buys / (buys + sells) if (buys + sells) > 0 else None

        curve_progress = curve_events[-1].payload.get("progress_pct") if curve_events else None

        # Holder/risk metrics are N/A unless holder snapshots are available.
        values = {
            "price": price,
            "curve_mc": curve_mc,
            "volume_1h": vol_1h,
            "volume_24h": volume_in_window(86400),
            "age_minutes": age_minutes,
            "delta_5m": self._price_delta(trades, last_ts, 300),
            "delta_1h": self._price_delta(trades, last_ts, 3600),
            "curve_progress_pct": curve_progress,
            "migrated": bool(migration_events),
            "volume_surge": volume_surge,
            "top10_pct": None,
            "top1_pct": None,
            "bundle_wallets_count": None,
            "bundle_supply_pct": None,
            "fresh_top_holders_pct": None,
            "sniper_supply_pct": None,
            "dev_holding_pct": None,
            "diamond_hands_pct": None,
            "early_dump_pct": None,
            "avg_roi_early_buyers": None,
            "avg_hold_time_early_buyers": None,
            "dev_past_tokens_count": None,
            "dev_migrated_count": None,
            "dev_dead_on_curve_count": None,
            "deployer_median_roi": None,
        }
        values.update(window_metrics)
        return FeatureVector(token_mint=timeline.token_mint, values=values)

    def _price_delta(self, trades, last_ts: int, window: int):
        low = last_ts - window
        candidates = [t for t in trades if t.ts >= low]
        if not candidates:
            return None
        start = float(candidates[0].payload.get("price", 0))
        end = float(candidates[-1].payload.get("price", 0))
        if start == 0:
            return None
        return ((end - start) / start) * 100
