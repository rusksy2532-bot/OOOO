from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, median
from typing import Literal, Optional

from src.backtest.execution_model import calc_slippage
from src.backtest.strategy import should_exit_by_time
from src.providers.base import FilterResult, TokenEvent, TokenFeatures


@dataclass
class TradeResult:
    mint: str
    signal_ts: int
    entry_ts: int
    exit_ts: Optional[int]
    entry_price: float
    exit_price: Optional[float]
    exit_reason: Literal["TP", "SL", "TIME", "LP_REMOVED", "OPEN"]
    roi_pct: Optional[float]
    hold_minutes: Optional[float]
    tp_hit: dict
    slippage_applied_pct: float
    fees_paid_pct: float


class BacktestEngine:
    """Event-driven backtest для одного токена."""

    def run_token(
        self,
        events: list[TokenEvent],
        features_at_signal: TokenFeatures,
        filter_result: FilterResult,
        config: dict,
    ) -> TradeResult:
        # Детерминированно возвращаем OPEN, если фильтр не пройден или нет трейдов.
        trades = [e for e in events if e.event_type == "trade"]
        signal_ts = features_at_signal.snapshot_ts
        if not filter_result.passed or not trades:
            return TradeResult(
                mint=features_at_signal.mint,
                signal_ts=signal_ts,
                entry_ts=signal_ts,
                exit_ts=None,
                entry_price=0.0,
                exit_price=None,
                exit_reason="OPEN",
                roi_pct=None,
                hold_minutes=None,
                tp_hit={"1.5x": False, "2x": False, "3x": False, "5x": False},
                slippage_applied_pct=0.0,
                fees_paid_pct=config["backtest"].get("fee_pct", 0.25),
            )

        entry_delay_ms = config["backtest"].get("entry_delay_seconds", 30) * 1000
        entry_ts = signal_ts + entry_delay_ms
        entry_trade = next((t for t in trades if t.timestamp >= entry_ts), trades[-1])
        raw_entry_price = entry_trade.data.get("price_usd", 0.0)

        slippage = calc_slippage(
            features_at_signal.curve_progress_pct,
            trade_size_usd=100.0,
            model=config["backtest"].get("slippage_model", "curve_based"),
            fixed_slippage_pct=config["backtest"].get("fixed_slippage_pct", 1.0),
        )
        entry_price = raw_entry_price * (1 + slippage / 100)

        multipliers = config["backtest"].get("take_profit_multipliers", [1.5, 2.0, 3.0, 5.0])
        stop_loss = config["backtest"].get("stop_loss_pct", -40.0)
        max_hold = config["backtest"].get("max_hold_minutes", 240)

        tp_hit = {f"{m}x": False for m in multipliers}
        exit_ts = None
        exit_price = None
        reason: Literal["TP", "SL", "TIME", "LP_REMOVED", "OPEN"] = "OPEN"

        for trade in (t for t in trades if t.timestamp >= entry_trade.timestamp):
            price = trade.data.get("price_usd", entry_price)
            roi = (price / entry_price - 1) * 100 if entry_price else 0.0
            for m in multipliers:
                if price >= entry_price * m:
                    tp_hit[f"{m}x"] = True
            if any(tp_hit.values()):
                exit_ts, exit_price, reason = trade.timestamp, price, "TP"
                break
            if roi <= stop_loss:
                exit_ts, exit_price, reason = trade.timestamp, price, "SL"
                break
            hold_minutes = (trade.timestamp - entry_trade.timestamp) / 60000
            if should_exit_by_time(hold_minutes, max_hold):
                exit_ts, exit_price, reason = trade.timestamp, price, "TIME"
                break

        if exit_ts is None:
            last = trades[-1]
            exit_ts, exit_price = last.timestamp, last.data.get("price_usd", entry_price)
            reason = "OPEN"

        roi_pct = (exit_price / entry_price - 1) * 100 if entry_price and exit_price else None
        hold_minutes = (exit_ts - entry_trade.timestamp) / 60000 if exit_ts else None

        return TradeResult(
            mint=features_at_signal.mint,
            signal_ts=signal_ts,
            entry_ts=entry_trade.timestamp,
            exit_ts=exit_ts,
            entry_price=entry_price,
            exit_price=exit_price,
            exit_reason=reason,
            roi_pct=roi_pct,
            hold_minutes=hold_minutes,
            tp_hit=tp_hit,
            slippage_applied_pct=slippage,
            fees_paid_pct=config["backtest"].get("fee_pct", 0.25),
        )


def calc_backtest_stats(results: list[TradeResult]) -> dict:
    rois = [r.roi_pct for r in results if r.roi_pct is not None]
    wins = [r for r in rois if r > 0]
    losses = [r for r in rois if r < 0]
    return {
        "total_trades": len(results),
        "winrate_1_5x": _tp_rate(results, "1.5x"),
        "winrate_2x": _tp_rate(results, "2x"),
        "avg_roi_pct": mean(rois) if rois else None,
        "median_roi_pct": median(rois) if rois else None,
        "profit_factor": (sum(wins) / abs(sum(losses))) if losses else None,
        "max_drawdown_pct": _max_drawdown(rois),
        "expectancy_pct": mean(rois) if rois else None,
        "avg_hold_minutes": mean([r.hold_minutes for r in results if r.hold_minutes is not None]) if results else None,
        "brier_score_1_5x": None,
    }


def _tp_rate(results: list[TradeResult], key: str) -> float | None:
    if not results:
        return None
    return sum(1 for r in results if r.tp_hit.get(key)) / len(results) * 100


def _max_drawdown(rois: list[float]) -> float | None:
    if not rois:
        return None
    equity = 1.0
    peak = 1.0
    mdd = 0.0
    for roi in rois:
        equity *= 1 + roi / 100
        peak = max(peak, equity)
        mdd = min(mdd, (equity - peak) / peak * 100)
    return mdd
