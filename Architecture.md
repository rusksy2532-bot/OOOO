# Architecture.md

## V2 слои

### 1) DataProvider
Интерфейс:
- `get_token_timeline(token_mint) -> TokenTimeline`
- `iter_token_timelines() -> list[TokenTimeline]`

Реализации:
- `HistoricalFileProvider` (JSON/файл)
- `LiveSolanaProvider` (RPC/WS scaffold)

Canonical event schema:
- `Event{ts, token_mint, event_type, payload}`
- event_type: `token_created|trade|curve_progress|migration|lp_add|lp_remove|holder_snapshot`

### 2) FeatureExtractor
Детерминированно считает:
- MARKET: `price`, `curve_mc`, `volume_1h/24h`, `age_minutes`, `delta_5m/1h`, `curve_progress_pct`, `migrated`
- PRESSURE: `buys/sells_5m/15m/1h`, `buy_ratio`, `volume_surge`
- RISKS/DEV: если нет данных -> `None` (N/A в отчёте)

Формулы:
- `buy_ratio = buys / (buys+sells)`
- `volume_surge = vol_1h / avg_hourly_vol_past_Nh`
- `delta_w = (P_now - P_w_start)/P_w_start * 100`

### 3) Filters Engine
Вход: `FeatureVector + config.yaml`
Выход: `FilterResult{passed, reasons[]}`

Примеры правил:
- `curve_mc ∈ [min,max]`
- `volume_1h >= min_volume_1h`
- `top10_pct <= max_top10_pct`
- `curve_progress_pct ∈ [min,max]`

Причины FAIL в human-readable формате:
- `FAIL top10_pct: 41 > max 35`

### 4) Scoring Engine
- `score 0..100`
- sub-scores: Market/Risk/Flow/Momentum
- contributions: по фичам
- Intelligence: `kNN` по feature-space + TP probabilities (x1.5/x2/x3/x5)

### 5) Backtest Engine
Event-driven deterministic:
- Entry: токен проходит фильтры
- Execution: market buy + slippage_bps + fee_bps
- Exit: TP / SL / time_exit
- Modes: backtest реализован; paper/live расширяются через единый provider+strategy контракт

Метрики:
- winrate
- avg/median ROI
- profit factor
- max drawdown
- expectancy
- avg hold time
- calibration: brier/precision/recall

### 6) Reporter
Форматы:
- `per_trade.csv`
- `token_summary.json`
- `backtest_summary.json`
- `global_report.md`
- single token SolHouse-style markdown

## Типы данных
- `TokenTimeline(token_name, token_mint, deployer, created_ts, events[])`
- `FeatureVector(token_mint, values)`
- `FilterResult(passed, reasons[])`
- `ScoreResult(total_score, subscores, contributions)`
- `TradeResult(entry/exit/roi/reason)`
- `BacktestSummary(aggregates + calibration)`
