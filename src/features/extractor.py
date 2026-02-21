from __future__ import annotations

from statistics import mean, median

from src.providers.base import TokenEvent, TokenFeatures


class FeatureExtractor:
    """Извлечение фич по историческим событиям токена."""

    def build(self, mint: str, events: list[TokenEvent], snapshot_ts: int | None = None) -> TokenFeatures:
        if not events:
            return TokenFeatures(mint=mint, snapshot_ts=snapshot_ts or 0)

        snapshot_ts = snapshot_ts or events[-1].timestamp
        created = next((e for e in events if e.event_type == "token_created"), None)
        trade_events = [e for e in events if e.event_type == "trade" and e.timestamp <= snapshot_ts]
        holder_snapshots = [e for e in events if e.event_type == "holder_snapshot" and e.timestamp <= snapshot_ts]
        curve_events = [e for e in events if e.event_type == "curve_progress" and e.timestamp <= snapshot_ts]
        migration = any(e.event_type == "migration" and e.timestamp <= snapshot_ts for e in events)

        price_now = trade_events[-1].data.get("price_usd") if trade_events else None
        price_5m = self._price_ago(trade_events, snapshot_ts, minutes=5)
        price_1h = self._price_ago(trade_events, snapshot_ts, minutes=60)

        volume_1h = self._volume_window(trade_events, snapshot_ts, minutes=60)
        volume_24h = self._volume_window(trade_events, snapshot_ts, minutes=24 * 60)
        hourly_bins = self._hourly_volumes(trade_events, snapshot_ts)
        volume_surge = None
        if len(hourly_bins) >= 2 and hourly_bins[-1] is not None:
            baseline = mean(hourly_bins[:-1]) if hourly_bins[:-1] else None
            if baseline and baseline > 0:
                volume_surge = hourly_bins[-1] / baseline

        buys_5m = sum(1 for t in trade_events if t.timestamp >= snapshot_ts - 5 * 60 * 1000 and t.data.get("side") == "buy")
        sells_5m = sum(1 for t in trade_events if t.timestamp >= snapshot_ts - 5 * 60 * 1000 and t.data.get("side") == "sell")

        top10_pct = top1_pct = fresh_pct = bundle_supply_pct = bundle_count = None
        sniper_supply_pct = dev_holding_pct = diamond_pct = early_dump_pct = avg_roi_early = None
        avg_hold_time = None
        if holder_snapshots:
            latest_holders = holder_snapshots[-1].data
            total_supply = latest_holders.get("total_supply")
            holders = latest_holders.get("holders", [])
            if total_supply and holders:
                balances = sorted((h.get("balance", 0.0) for h in holders), reverse=True)
                top10_pct = sum(balances[:10]) / total_supply * 100 if balances else None
                top1_pct = balances[0] / total_supply * 100 if balances else None
                fresh = [h for h in holders if h.get("wallet_age_hours") is not None and h["wallet_age_hours"] < 48]
                fresh_pct = len(fresh) / len(holders) * 100 if holders else None
                bundles = [h for h in holders if h.get("is_bundle")]
                bundle_count = len(bundles)
                bundle_supply_pct = sum(h.get("balance", 0.0) for h in bundles) / total_supply * 100
                snipers = [h for h in holders if h.get("is_sniper")]
                sniper_supply_pct = sum(h.get("balance", 0.0) for h in snipers) / total_supply * 100
                dev = [h for h in holders if h.get("is_dev")]
                dev_holding_pct = sum(h.get("balance", 0.0) for h in dev) / total_supply * 100

                early = [h for h in holders if h.get("is_early_buyer")]
                if early:
                    diamond = [h for h in early if h.get("balance", 0) > 0]
                    dump = [h for h in early if h.get("sold_out")]
                    diamond_pct = len(diamond) / len(early) * 100
                    early_dump_pct = len(dump) / len(early) * 100
                    rois = [h.get("roi_pct") for h in early if h.get("roi_pct") is not None]
                    avg_roi_early = mean(rois) if rois else None
                    holds = [h.get("hold_minutes") for h in early if h.get("hold_minutes") is not None]
                    avg_hold_time = mean(holds) if holds else None

        dev_stats = self._dev_history(events)
        curve_progress_pct = curve_events[-1].data.get("curve_progress_pct") if curve_events else None

        return TokenFeatures(
            mint=mint,
            snapshot_ts=snapshot_ts,
            price_usd=price_now,
            market_cap_usd=(price_now * holder_snapshots[-1].data.get("total_supply")) if (price_now and holder_snapshots) else None,
            volume_1h=volume_1h,
            volume_24h=volume_24h,
            age_minutes=((snapshot_ts - created.timestamp) / 60000) if created else None,
            curve_progress_pct=curve_progress_pct,
            migrated=migration,
            delta_5m_pct=((price_now - price_5m) / price_5m * 100) if (price_now and price_5m) else None,
            delta_1h_pct=((price_now - price_1h) / price_1h * 100) if (price_now and price_1h) else None,
            buys_5m=buys_5m,
            sells_5m=sells_5m,
            buy_ratio_5m=(buys_5m / (buys_5m + sells_5m)) if (buys_5m + sells_5m) else None,
            volume_surge=volume_surge,
            top10_pct=top10_pct,
            top1_pct=top1_pct,
            bundle_count=bundle_count,
            bundle_supply_pct=bundle_supply_pct,
            fresh_holders_pct=fresh_pct,
            sniper_supply_pct=sniper_supply_pct,
            dev_holding_pct=dev_holding_pct,
            diamond_hands_pct=diamond_pct,
            early_dump_pct=early_dump_pct,
            avg_roi_early_buyers=avg_roi_early,
            avg_hold_time_minutes=avg_hold_time,
            dev_past_tokens=dev_stats.get("past_tokens"),
            dev_migrated_count=dev_stats.get("migrated_count"),
            dev_dead_count=dev_stats.get("dead_count"),
            dev_median_roi=dev_stats.get("median_roi"),
        )

    def _price_ago(self, trades: list[TokenEvent], snapshot_ts: int, minutes: int) -> float | None:
        threshold = snapshot_ts - minutes * 60 * 1000
        past = [t for t in trades if t.timestamp <= threshold]
        return past[-1].data.get("price_usd") if past else None

    def _volume_window(self, trades: list[TokenEvent], snapshot_ts: int, minutes: int) -> float | None:
        threshold = snapshot_ts - minutes * 60 * 1000
        window = [t.data.get("volume_usd", 0.0) for t in trades if t.timestamp >= threshold]
        return sum(window) if window else None

    def _hourly_volumes(self, trades: list[TokenEvent], snapshot_ts: int) -> list[float]:
        earliest = min((t.timestamp for t in trades), default=snapshot_ts)
        hours = max(1, int((snapshot_ts - earliest) / (60 * 60 * 1000)) + 1)
        result = []
        for i in range(hours):
            start = snapshot_ts - (hours - i) * 60 * 60 * 1000
            end = start + 60 * 60 * 1000
            bucket = [t.data.get("volume_usd", 0.0) for t in trades if start <= t.timestamp < end]
            result.append(sum(bucket))
        return result

    def _dev_history(self, events: list[TokenEvent]) -> dict:
        dev_meta = [e.data for e in events if e.event_type == "token_created" and e.data.get("dev_history")]
        if not dev_meta:
            return {"past_tokens": None, "migrated_count": None, "dead_count": None, "median_roi": None}
        history = dev_meta[-1].get("dev_history", [])
        rois = [item.get("roi_pct") for item in history if item.get("roi_pct") is not None]
        return {
            "past_tokens": len(history),
            "migrated_count": sum(1 for item in history if item.get("migrated")),
            "dead_count": sum(1 for item in history if item.get("dead")),
            "median_roi": median(rois) if rois else None,
        }
