from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .models import BacktestSummary, FilterResult, ScoreResult, TokenFeatures


class Reporter:
    def token_report(self, features: TokenFeatures, filters: FilterResult, score: ScoreResult) -> str:
        v = features.values
        def fmt(x):
            return "N/A" if x is None else x
        lines = [
            "# Market State: Pump.fun / Solana",
            f"Token: {features.token_name} ({features.token_mint})",
            f"Score: {score.score}/100 | Flags: {'PASS' if filters.passed else 'HIGH WARNING'}",
            "",
            "## MARKET",
            f"- price: {fmt(v.get('price'))}",
            f"- curve_mc: {fmt(v.get('curve_mc'))}",
            f"- volume_24h / 1h: {fmt(v.get('volume_24h'))} / {fmt(v.get('volume_1h'))}",
            f"- age_minutes: {fmt(v.get('age_minutes'))}",
            f"- delta_5m / 1h: {fmt(v.get('delta_5m_pct'))}% / {fmt(v.get('delta_1h_pct'))}%",
            f"- curve_progress: {fmt(v.get('curve_progress_pct'))}% | migrated: {fmt(v.get('migrated'))}",
            "## PRESSURE",
            f"- buy ratios (5m/15m/1h): {fmt(v.get('buy_ratio_5m'))} / {fmt(v.get('buy_ratio_15m'))} / {fmt(v.get('buy_ratio_1h'))}",
            f"- volume_surge: {fmt(v.get('volume_surge'))}",
            "## RISKS",
            f"- top10/top1: {fmt(v.get('top10_pct'))}% / {fmt(v.get('top1_pct'))}%",
            f"- bundle count/supply: {fmt(v.get('bundle_wallets_count'))} / {fmt(v.get('bundle_supply_pct'))}%",
            f"- fresh top holders: {fmt(v.get('fresh_top_holders_pct'))}%",
            f"- sniper supply: {fmt(v.get('sniper_supply_pct'))}%",
            f"- dev holding: {fmt(v.get('dev_holding_pct'))}%",
            f"- diamond hands: {fmt(v.get('diamond_hands_pct'))}%",
            f"- early dump: {fmt(v.get('early_dump_pct'))}%",
            "## DEV HISTORY / NETWORK",
            f"- past tokens: {fmt(v.get('dev_past_tokens_count'))}",
            f"- migrated/dead-on-curve: {fmt(v.get('dev_migrated_count'))} / {fmt(v.get('dev_dead_on_curve_count'))}",
            f"- deployer median ROI: {fmt(v.get('deployer_median_roi_pct'))}%",
            "## ENTRY / EXIT",
            f"- Entry filters: {'PASS' if filters.passed else 'FAIL'}",
            *[f"  - {r}" for r in filters.reasons],
            "## INTELLIGENCE",
            f"- TP probs (kNN): {score.tp_probabilities}",
            f"- contributions: {score.contributions}",
        ]
        return "\n".join(lines)

    def export_token_artifacts(self, out_dir: Path, features: TokenFeatures, report: str):
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "token_features.json").write_text(json.dumps(features.values, indent=2, default=str))
        (out_dir / "token_report.md").write_text(report)

    def export_backtest_global(self, out_dir: Path, summary: BacktestSummary):
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "global_report.md").write_text(
            "\n".join(
                [
                    "# Backtest Global Report",
                    f"- total_trades: {summary.total_trades}",
                    f"- winrate: {summary.winrate:.4f}",
                    f"- avg_roi: {summary.avg_roi:.4f}",
                    f"- median_roi: {summary.median_roi:.4f}",
                    f"- profit_factor: {summary.profit_factor:.4f}",
                    f"- max_drawdown: {summary.max_drawdown:.4f}%",
                    f"- expectancy: {summary.expectancy:.4f}",
                    f"- brier_tp2: {summary.brier_tp2}",
                ]
            )
        )
        with (out_dir / "global_summary.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=asdict(summary).keys())
            w.writeheader()
            w.writerow(asdict(summary))
