from __future__ import annotations

import csv
import json
from dataclasses import asdict
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from statistics import median

from .features import FeatureExtractor
from .filters import FiltersEngine
from .models import BacktestSummary, Event, TradeResult


@dataclass(slots=True)
class BacktestEngine:
    feature_extractor: FeatureExtractor
    filters_engine: FiltersEngine
    config: dict

    def run(self, grouped_events: dict[str, list[Event]], out_dir: Path) -> tuple[list[TradeResult], BacktestSummary, list[dict]]:
        out_dir.mkdir(parents=True, exist_ok=True)
        trades: list[TradeResult] = []
        token_rows: list[dict] = []
        equity = [1.0]

        for mint, events in grouped_events.items():
            events = sorted(events, key=lambda e: e.timestamp)
            token_name = next((e.data.get("token_name") for e in events if e.event_type == "token_created"), mint)
            features = self.feature_extractor.extract(mint, token_name, events)
            fresult = self.filters_engine.evaluate(features)
            if not fresult.passed:
                token_rows.append({"token_mint": mint, "status": "filtered", "reasons": " | ".join(fresult.reasons)})
                continue

            tr = [e for e in events if e.event_type == "trade"]
            if len(tr) < 2:
                token_rows.append({"token_mint": mint, "status": "no_trades"})
                continue
            entry = tr[0]
            exit_evt, reason = self._find_exit(tr, entry)
            entry_price = float(entry.data.get("price"))
            exit_price = float(exit_evt.data.get("price"))
            slip_bps = self.config.get("execution", {}).get("slippage_bps", 0)
            fee_bps = self.config.get("execution", {}).get("fee_bps", 0)
            entry_effective = entry_price * (1 + slip_bps / 10_000)
            exit_effective = exit_price * (1 - slip_bps / 10_000)
            roi = (exit_effective / entry_effective - 1) * 100 - fee_bps / 100
            hold_m = (exit_evt.timestamp - entry.timestamp).total_seconds() / 60
            trade_result = TradeResult(
                token_mint=mint,
                entry_time=entry.timestamp,
                exit_time=exit_evt.timestamp,
                entry_price=entry_effective,
                exit_price=exit_effective,
                roi_pct=roi,
                exit_reason=reason,
                hold_minutes=hold_m,
            )
            trades.append(trade_result)
            equity.append(equity[-1] * (1 + roi / 100))
            token_rows.append({"token_mint": mint, "status": "traded", "roi_pct": roi, "exit_reason": reason})

        summary = self._summary(trades, equity)
        self._write_trade_csv(trades, out_dir / "per_trade.csv")
        (out_dir / "per_token_summary.json").write_text(json.dumps(token_rows, indent=2, default=str))
        return trades, summary, token_rows

    def _find_exit(self, trades: list[Event], entry: Event):
        cfg = self.config.get("strategy", {})
        tp = cfg.get("tp_pct", 50)
        sl = cfg.get("sl_pct", -20)
        max_hold = cfg.get("time_exit_minutes", 120)
        entry_px = float(entry.data.get("price"))
        for t in trades[1:]:
            roi = (float(t.data.get("price")) / entry_px - 1) * 100
            if roi >= tp:
                return t, "TP"
            if roi <= sl:
                return t, "SL"
            if t.timestamp - entry.timestamp >= timedelta(minutes=max_hold):
                return t, "TIME_EXIT"
            if t.data.get("risk_exit"):
                return t, "RISK_EXIT"
        return trades[-1], "END_OF_DATA"

    def _summary(self, trades: list[TradeResult], equity: list[float]) -> BacktestSummary:
        if not trades:
            return BacktestSummary(0, 0, 0, 0, 0, 0, 0, None)
        rois = [t.roi_pct for t in trades]
        wins = [r for r in rois if r > 0]
        losses = [-r for r in rois if r <= 0]
        gross_profit = sum(wins)
        gross_loss = sum(losses) if losses else 1e-9
        pf = gross_profit / gross_loss
        peaks = []
        peak = equity[0]
        max_dd = 0.0
        for e in equity:
            peak = max(peak, e)
            peaks.append(peak)
            max_dd = max(max_dd, (peak - e) / peak)
        expectancy = sum(rois) / len(rois)
        return BacktestSummary(
            total_trades=len(trades),
            winrate=len(wins) / len(rois),
            avg_roi=expectancy,
            median_roi=median(rois),
            profit_factor=pf,
            max_drawdown=max_dd * 100,
            expectancy=expectancy,
            brier_tp2=None,
        )

    def _write_trade_csv(self, trades: list[TradeResult], path: Path):
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(TradeResult.__dataclass_fields__.keys()))
            writer.writeheader()
            for t in trades:
                writer.writerow(asdict(t))
