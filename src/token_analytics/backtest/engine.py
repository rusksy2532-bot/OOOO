from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from statistics import median

from token_analytics.features.extractor import FeatureExtractor
from token_analytics.filters.engine import FiltersEngine
from token_analytics.models.types import BacktestSummary, EventType, TradeResult
from token_analytics.scoring.engine import ScoringEngine, knn_tp_probabilities


class BacktestEngine:
    def __init__(
        self,
        filters: FiltersEngine,
        extractor: FeatureExtractor,
        scorer: ScoringEngine,
        fee_bps: float = 100,
        slippage_bps: float = 150,
        tp_pct: float = 100,
        sl_pct: float = 30,
        max_hold_seconds: int = 3600,
    ) -> None:
        self.filters = filters
        self.extractor = extractor
        self.scorer = scorer
        self.fee = fee_bps / 10_000
        self.slippage = slippage_bps / 10_000
        self.tp_pct = tp_pct
        self.sl_pct = sl_pct
        self.max_hold_seconds = max_hold_seconds

    def run(self, timelines) -> tuple[list[TradeResult], dict, BacktestSummary]:
        trades: list[TradeResult] = []
        token_summary: dict = {}
        history_for_knn = []

        for timeline in timelines:
            fv = self.extractor.extract(timeline)
            fr = self.filters.evaluate(fv)
            score = self.scorer.score(fv)
            token_row = {"filter_pass": fr.passed, "fail_reasons": fr.reasons, "score": score.total_score}

            if not fr.passed:
                token_summary[timeline.token_mint] = token_row
                continue

            t = self._simulate_trade(timeline)
            if t:
                trades.append(t)
                outcome = {
                    "hit_tp_1_5": t.roi_pct >= 50,
                    "hit_tp_2": t.roi_pct >= 100,
                    "hit_tp_3": t.roi_pct >= 200,
                    "hit_tp_5": t.roi_pct >= 400,
                }
                history_for_knn.append((fv, outcome))
                token_row["trade"] = asdict(t)

            token_summary[timeline.token_mint] = token_row

        calibration = self._calibration(trades)
        summary = self._summary(trades, calibration)

        for timeline in timelines:
            fv = self.extractor.extract(timeline)
            probs = knn_tp_probabilities(fv, history_for_knn, k=5)
            token_summary[timeline.token_mint]["tp_probabilities"] = probs

        return trades, token_summary, summary

    def _simulate_trade(self, timeline):
        trades = [e for e in timeline.events if e.event_type == EventType.TRADE]
        if len(trades) < 2:
            return None

        entry = trades[0]
        entry_price = float(entry.payload.get("price", 0)) * (1 + self.slippage + self.fee)
        qty = 1 / entry_price if entry_price > 0 else 0
        tp_price = entry_price * (1 + self.tp_pct / 100)
        sl_price = entry_price * (1 - self.sl_pct / 100)
        deadline = entry.ts + self.max_hold_seconds

        exit_event = trades[-1]
        reason = "time_exit"
        for tr in trades[1:]:
            p = float(tr.payload.get("price", 0)) * (1 - self.slippage - self.fee)
            if p >= tp_price:
                exit_event = tr
                reason = "tp"
                break
            if p <= sl_price:
                exit_event = tr
                reason = "sl"
                break
            if tr.ts >= deadline:
                exit_event = tr
                reason = "time_exit"
                break

        exit_price = float(exit_event.payload.get("price", 0)) * (1 - self.slippage - self.fee)
        roi_pct = ((exit_price - entry_price) / entry_price) * 100 if entry_price else 0
        return TradeResult(
            token_mint=timeline.token_mint,
            entry_ts=entry.ts,
            exit_ts=exit_event.ts,
            entry_price=entry_price,
            exit_price=exit_price,
            qty=qty,
            roi_pct=roi_pct,
            reason_exit=reason,
        )

    def _summary(self, trades: list[TradeResult], calibration: dict[str, float]) -> BacktestSummary:
        if not trades:
            return BacktestSummary(0, 0, 0, 0, 0, 0, 0, 0, calibration)
        rois = [t.roi_pct for t in trades]
        wins = [r for r in rois if r > 0]
        losses = [r for r in rois if r <= 0]
        gross_profit = sum(wins)
        gross_loss = abs(sum(losses)) or 1e-9
        pf = gross_profit / gross_loss
        expectancy = sum(rois) / len(rois)
        dd = self._max_drawdown(rois)
        hold = [(t.exit_ts - t.entry_ts) for t in trades]
        return BacktestSummary(
            total_trades=len(trades),
            winrate=len(wins) / len(rois),
            avg_roi_pct=expectancy,
            median_roi_pct=median(rois),
            profit_factor=pf,
            max_drawdown_pct=dd,
            expectancy_pct=expectancy,
            avg_holding_seconds=sum(hold) / len(hold),
            calibration=calibration,
        )

    def _max_drawdown(self, rois: list[float]) -> float:
        equity = 1.0
        peak = 1.0
        max_dd = 0.0
        for r in rois:
            equity *= 1 + r / 100
            peak = max(peak, equity)
            dd = (peak - equity) / peak * 100
            max_dd = max(max_dd, dd)
        return max_dd

    def _calibration(self, trades: list[TradeResult]) -> dict[str, float]:
        if not trades:
            return {"brier_tp2": 0.0, "precision_tp2": 0.0, "recall_tp2": 0.0}
        labels = [1 if t.roi_pct >= 100 else 0 for t in trades]
        probs = [0.5 for _ in trades]
        brier = sum((p - y) ** 2 for p, y in zip(probs, labels)) / len(labels)
        tp = sum(1 for y in labels if y == 1)
        pred_pos = len(labels)
        precision = tp / pred_pos if pred_pos else 0.0
        recall = tp / sum(labels) if sum(labels) else 0.0
        return {"brier_tp2": brier, "precision_tp2": precision, "recall_tp2": recall}


def write_backtest_outputs(trades, token_summary, summary, outdir: str) -> None:
    p = Path(outdir)
    p.mkdir(parents=True, exist_ok=True)

    with (p / "per_trade.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(trades[0]).keys()) if trades else ["token_mint"])
        writer.writeheader()
        for t in trades:
            writer.writerow(asdict(t))

    with (p / "token_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(token_summary, handle, indent=2)

    with (p / "backtest_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(asdict(summary), handle, indent=2)
