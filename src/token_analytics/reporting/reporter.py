from __future__ import annotations

import json
from pathlib import Path

from token_analytics.models.types import FeatureVector, FilterResult, ScoreResult


def _fmt(v):
    return "N/A" if v is None else v


def render_solhouse_style_report(token_name: str, mint: str, fv: FeatureVector, fr: FilterResult, sr: ScoreResult, probs: dict | None = None) -> str:
    v = fv.values
    status = "PASS" if fr.passed else "HIGH WARNING"
    probs = probs or {}
    return f"""# Market State: {status}

## Token
- Name: {token_name}
- Mint: {mint}
- Score: {sr.total_score}/100

## MARKET
- Price: {_fmt(v.get('price'))}
- Curve MC: {_fmt(v.get('curve_mc'))}
- Volume 1h / 24h: {_fmt(v.get('volume_1h'))} / {_fmt(v.get('volume_24h'))}
- Age (min): {_fmt(v.get('age_minutes'))}
- Delta 5m / 1h (%): {_fmt(v.get('delta_5m'))} / {_fmt(v.get('delta_1h'))}
- Curve progress: {_fmt(v.get('curve_progress_pct'))}%
- Migrated: {_fmt(v.get('migrated'))}

## BUY/SELL PRESSURE
- Buys vs Sells 5m: {_fmt(v.get('buys_5m'))} / {_fmt(v.get('sells_5m'))}
- Buys vs Sells 15m: {_fmt(v.get('buys_15m'))} / {_fmt(v.get('sells_15m'))}
- Buys vs Sells 1h: {_fmt(v.get('buys_1h'))} / {_fmt(v.get('sells_1h'))}
- Buy ratio 1h: {_fmt(v.get('buy_ratio_1h'))}
- Volume surge: {_fmt(v.get('volume_surge'))}

## RISKS
- Top10%: {_fmt(v.get('top10_pct'))}
- Top1%: {_fmt(v.get('top1_pct'))}
- Bundle wallets / supply%: {_fmt(v.get('bundle_wallets_count'))} / {_fmt(v.get('bundle_supply_pct'))}
- Fresh top holders%: {_fmt(v.get('fresh_top_holders_pct'))}
- Sniper supply%: {_fmt(v.get('sniper_supply_pct'))}
- Dev holding%: {_fmt(v.get('dev_holding_pct'))}
- Diamond hands%: {_fmt(v.get('diamond_hands_pct'))}
- Early dump%: {_fmt(v.get('early_dump_pct'))}
- Avg ROI early buyers: {_fmt(v.get('avg_roi_early_buyers'))}
- Avg hold time early buyers: {_fmt(v.get('avg_hold_time_early_buyers'))}

## DEV HISTORY / NETWORK
- Past tokens: {_fmt(v.get('dev_past_tokens_count'))}
- Migrated count: {_fmt(v.get('dev_migrated_count'))}
- Dead on curve count: {_fmt(v.get('dev_dead_on_curve_count'))}
- Median ROI deployer history: {_fmt(v.get('deployer_median_roi'))}

## ENTRY / EXIT
- Entry filters: {'PASS' if fr.passed else 'FAIL'}
- Fail reasons: {', '.join(fr.reasons) if fr.reasons else 'None'}
- Exit triggers monitored: LP removal / curve reversal / whale dump / volume collapse / post-migration slippage

## INTELLIGENCE
- TP x1.5 probability: {_fmt(probs.get('tp_1_5'))}
- TP x2 probability: {_fmt(probs.get('tp_2'))}
- TP x3 probability: {_fmt(probs.get('tp_3'))}
- TP x5 probability: {_fmt(probs.get('tp_5'))}
- Subscores: {sr.subscores}
- Feature contributions: {sr.contributions}
"""


def write_markdown(path: str, text: str) -> None:
    Path(path).write_text(text, encoding="utf-8")


def render_global_report(summary_json_path: str, backtest_json_path: str, out_path: str) -> None:
    s = json.loads(Path(summary_json_path).read_text(encoding="utf-8"))
    b = json.loads(Path(backtest_json_path).read_text(encoding="utf-8"))
    md = ["# Backtest Global Report", "", "## Aggregates"]
    for k, v in b.items():
        md.append(f"- {k}: {v}")
    md += ["", "## Per-token"]
    for mint, row in s.items():
        md.append(f"- {mint}: pass={row.get('filter_pass')} score={row.get('score')} probs={row.get('tp_probabilities')}")
    Path(out_path).write_text("\n".join(md), encoding="utf-8")
