## До
Репозиторий был пустым: отсутствовали код, конфигурация, точка входа и модульная архитектура.

## После
Добавлен каркас Token Analytics + Backtest Framework v3 с модулями providers/features/filters/scoring/backtest/reporter, CLI-режимами `scan/backtest/report`, базовым `config.yaml`, документами и примерами данных.

## Data Sources
| Источник | Что даёт | Есть в проекте? |
|---|---|---|
| Helius RPC/WS | Транзакции, mint events, holders | Частично (интерфейс `LiveProvider` как заглушка) |
| Pump.fun WebSocket | token_created/trade/curve/migration | Частично (структуры событий + загрузка из history) |
| Birdeye API | OHLCV, volume, price | Нет (план интеграции в `LiveProvider`) |
| DexScreener | Pool stats, price history | Нет (только ссылки в отчёте) |
| Rugcheck/on-chain | Bundle/sniper detection | Частично (расчёт на основе флагов в `holder_snapshot`) |

## Dataflow
[Pump.fun WS] → collector → DB (tokens, trades, holders, curve)
                                   ↓
                            FeatureExtractor → Filters → Scoring → Reporter

## Modules
- collector/pumpfun_ws.py (запланировано)
- collector/birdeye.py (запланировано)
- features/extractor.py
- filters/engine.py
- scoring/engine.py
- backtest/engine.py
- reporter/generator.py

## Decision Logic
- Логика стратегии/бэктеста: `src/backtest/engine.py` (`BacktestEngine.run_token`).
- Ключи/кошельки: через `.env` и `python-dotenv` в `main.py`; в коде hardcode ключей отсутствует.
- Логирование результатов: CSV/JSON/Markdown в `data/results/`.
- Backtest-движок: есть, формат входа — список `TokenEvent`.

## Gap-аналитика
### Для SolHouse-отчёта
- [x] Концентрация холдеров (top10/top1)
- [x] Bundle wallets detection (по флагам snapshot)
- [x] Sniper wallet detection (по флагам snapshot)
- [x] Dev wallet history
- [x] Diamond hands / early dump
- [ ] Deployer network stats

### Для backtest
- [x] Исторический таймлайн событий по токену
- [x] curve_progress по времени
- [x] Миграция на DEX (флаг migration)
- [x] Slippage-модель

## Critical Security Risks
- [ ] API keys in code (check all .py/.ts files)
- [x] No input validation on mint address

## Backtest Integration Points
- filters/engine.py → add historical mode
- features/extractor.py → add batch/historical interface
