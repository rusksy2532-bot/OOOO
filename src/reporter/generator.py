from __future__ import annotations

from src.providers.base import FilterResult, ScoringResult, TokenFeatures


def _fmt(value, suffix="") -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.2f}{suffix}"
    return f"{value}{suffix}"


class ReportGenerator:
    """Генератор SolHouse-style текстового отчёта."""

    def generate(
        self,
        features: TokenFeatures,
        score: ScoringResult,
        filt: FilterResult,
        intel: dict,
        token_name: str = "N/A",
        symbol: str = "N/A",
    ) -> str:
        status = "PASS FILTERS" if filt.passed else "FAIL FILTERS"
        reasons = "All filters passed" if filt.passed else "; ".join(filt.reasons)
        return f"""╔══════════════════════════════════════════════════╗
║  🔥 TOKEN REPORT — PUMP.FUN/SOLANA               ║
║  Powered by TokenAnalytics v3                    ║
╚══════════════════════════════════════════════════╝

📛 NAME: {token_name} | {symbol}
🔑 MINT: {features.mint}
🕒 Age: {_fmt(features.age_minutes, ' min')} | Snapshot: {features.snapshot_ts}

🎯 SCORE: {_fmt(score.total_score)}/100
   ├─ Market:   {_fmt(score.market_score)}/100
   ├─ Pressure: {_fmt(score.pressure_score)}/100
   ├─ Risk:     {_fmt(score.risk_score)}/100
   └─ Dev:      {_fmt(score.dev_score)}/100

✅  STATUS: {'PRE-MIGRATION' if not features.migrated else 'POST-MIGRATION'} | {status}

━━━━━━━━━━━━━━ 📊 MARKET ━━━━━━━━━━━━━━
Price:          ${_fmt(features.price_usd)}
Market Cap:     ${_fmt(features.market_cap_usd)}
Volume 1h:      ${_fmt(features.volume_1h)}
Volume 24h:     ${_fmt(features.volume_24h)}
Curve Progress: {_fmt(features.curve_progress_pct, '%')}  (migrated: {'YES' if features.migrated else 'NO'})
Δ5m / Δ1h:      {_fmt(features.delta_5m_pct, '%')} / {_fmt(features.delta_1h_pct, '%')}

━━━━━━━━━━━━━━ 🔴 BUY/SELL ━━━━━━━━━━━━━━
Buys 5m:        {_fmt(features.buys_5m)}
Sells 5m:       {_fmt(features.sells_5m)}
Buy Ratio 5m:   {_fmt(features.buy_ratio_5m * 100 if features.buy_ratio_5m is not None else None, '%')}
Volume Surge:   {_fmt(features.volume_surge, 'x')}

━━━━━━━━━━━━━━ ⚠️ RISKS ━━━━━━━━━━━━━━
Top 10%:        {_fmt(features.top10_pct, '%')}
Top 1%:         {_fmt(features.top1_pct, '%')}
Bundle Wallets: {_fmt(features.bundle_count)} wallets / {_fmt(features.bundle_supply_pct, '%')}
Fresh Holders:  {_fmt(features.fresh_holders_pct, '%')}
Snipers:        {_fmt(features.sniper_supply_pct, '%')}
Dev Holding:    {_fmt(features.dev_holding_pct, '%')}
Diamond Hands:  {_fmt(features.diamond_hands_pct, '%')}
Early Dump:     {_fmt(features.early_dump_pct, '%')}
Avg ROI Early:  {_fmt(features.avg_roi_early_buyers, '%')}

━━━━━━━━━━━━━━ 👨‍💻 DEV HISTORY ━━━━━━━━━━━━
Past Tokens:    {_fmt(features.dev_past_tokens)}
  └─ Migrated:  {_fmt(features.dev_migrated_count)}
  └─ Dead:      {_fmt(features.dev_dead_count)}
Median ROI:     {_fmt(features.dev_median_roi, '%')}

━━━━━━━━━━━━━━ 🧠 INTELLIGENCE ━━━━━━━━━━━━
Similar Tokens: {_fmt(intel.get('neighbors_count'))} in DB
TP Probability:
  1.5x → {_fmt(intel.get('tp_1_5x_prob'), '%')} | 2x → {_fmt(intel.get('tp_2x_prob'), '%')}
  3x  → {_fmt(intel.get('tp_3x_prob'), '%')} | 5x → {_fmt(intel.get('tp_5x_prob'), '%')}
Model Calibration: {intel.get('model_calibration', 'N/A')}

━━━━━━━━━━━━━━ 🟢 ENTRY ━━━━━━━━━━━━━━
Status:         {'PASS' if filt.passed else 'FAIL'}
Reasons:        {reasons}

🔗 Birdeye: https://birdeye.so/token/{features.mint}
🔗 DexScreener: https://dexscreener.com/solana/{features.mint}
🔗 Solscan: https://solscan.io/token/{features.mint}
"""
