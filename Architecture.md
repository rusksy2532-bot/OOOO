# Architecture.md (V2)

## Layers

## 1) DataProvider
Interface:
```python
class DataProvider(ABC):
    def stream_events(self, token_mint: str|None=None) -> Iterable[Event]
```
Event schema:
- `timestamp`
- `event_type` in `{token_created, trade, curve_progress, migration, lp_add, lp_remove, holder_snapshot, dev_history}`
- `token_mint`
- `data: dict`

Implementations:
- `LiveRpcWsProvider(rpc_url, ws_url)` — адаптер для RPC/WS.
- `HistoricalFileProvider(events_path)` — CSV/JSON timeline replay.

## 2) FeatureExtractor
Детерминированные фичи (без ML-халлюцинаций):
- MARKET:
  - `price = last_trade_price`
  - `curve_mc = last(curve_progress.curve_mc)`
  - `volume_1h/24h = sum(trade.volume_usd in window)`
  - `age_minutes = now - token_created_ts`
  - `delta_5m = price_now / price_5m_ago - 1`
  - `delta_1h = price_now / price_1h_ago - 1`
  - `curve_progress_pct` and `migrated`
- PRESSURE:
  - `buy_ratio_w = buys_w / (buys_w + sells_w)` for 5m/15m/1h
  - `volume_surge = vol_1h / avg_hourly_vol_past_Nh`
- RISKS/DEV:
  - `top10_pct`, `top1_pct`, `bundle_supply_pct`, `fresh_top_holders_pct`, `sniper_supply_pct`, `dev_holding_pct`, `diamond_hands_pct`, `early_dump_pct`, etc.
  - `dev_past_tokens_count`, `dev_migrated_count`, `dev_dead_on_curve_count`, `deployer_median_roi_pct`

Если поле не присутствует в событиях, возвращается `N/A` (`None`).

## 3) Filters Engine
Input: `TokenFeatures + config.yaml`.
Output: `FilterResult {passed, reasons[]}`.

Фильтры:
- min/max curve_mc
- min/max age_minutes
- min volume_1h, min volume_surge
- max top10/top1/fresh_top_holders/early_dump/bundle/sniper
- dev history max rugs + min migrated
- curve progress range

Каждый FAIL возвращает человекочитаемую причину.

## 4) Scoring Engine
- Score 0..100
- Subscores: Market/Risk/Dev
- Explanations: feature contributions
- Intelligence: kNN по historical feature-space + вероятности TP(x1.5/x2/x3/x5)
- Accuracy metrics (Brier/precision/recall): `N/A`, пока нет размеченного validation набора.

## 5) Backtest Engine
- Event-driven replay per token.
- Entry: PASS entry filters.
- Execution model:
  - market buy entry,
  - slippage/fee from config,
  - optional latency hook (ext point).
- Exit:
  - TP/SL/time_exit/risk_exit/end_of_data.
- Modes:
  - backtest (готово),
  - paper/live как дальнейшие адаптеры provider+executor.

Metrics:
- winrate, avg/median ROI, profit factor, max DD, expectancy, holding times.
- calibration metrics: `N/A` при отсутствии labels.

Outputs:
- `per_trade.csv`
- `per_token_summary.json`
- `global_report.md`

## 6) Reporter
- SolHouse-style markdown block sections:
  - MARKET / PRESSURE / RISKS / DEV HISTORY / ENTRY/EXIT / INTELLIGENCE
- Exports:
  - JSON (`token_features.json`)
  - CSV (`per_trade.csv`, `global_summary.csv`)
  - Markdown (`token_report.md`, `global_report.md`)
  - Telegram text: используется тот же plain text markdown output.
