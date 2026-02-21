# Audit.md

## PHASE 0

### 1) Структура
Исходный репозиторий в текущем окружении был пустым (`.gitkeep`), внешняя загрузка GitHub-архива недоступна из-за сетевого ограничения (`curl ... codeload.github.com -> 403`). Поэтому аудит "как есть" проведён для текущего содержимого, а затем реализован V2-фреймворк в этом репозитории.

### 2) Стек
- Язык: Python 3.10+
- Пакетирование: setuptools (`pyproject.toml`)
- Библиотеки: `pydantic` (декларативно), `PyYAML`
- Точка входа CLI: `token-analytics = token_analytics.cli.main:main`

### 3) Локальный запуск
- `pip install -e .`
- `token-analytics backtest --config examples/config.yaml --dataset examples/historical_tokens.json --outdir reports`

## PHASE 1 — Audit

### A) Data sources
- Historical: JSON dataset с timeline событий токена (`HistoricalFileProvider`).
- Live: scaffold `LiveSolanaProvider` с интерфейсом RPC/WS, без runtime-реализации.
- Поддержанные event-типы: `token_created`, `trade`, `curve_progress`, `migration`, `lp_add/remove`, `holder_snapshot`.

### B) Decision logic
- Entry logic: PASS/FAIL через `FiltersEngine` и `config.yaml`.
- Strategy/backtest: вход на первом trade после PASS, выход по TP/SL/time-exit.
- Risk/scoring: `ScoringEngine` с sub-scores + feature contributions.
- Keys/wallet storage: отсутствует (без секретов в репозитории).

### C) Gap-аналитика
- Недостает в данных для full SolHouse parity: реальные holder snapshots, bundle/sniper маркировка, ончейн dev history, wallet age graph.
- Недостает для production backtest: полноценные curve/DEX execution states, depth snapshots, mempool latency model, migration fill model.

## Dataflow (текстовая диаграмма)
1. `DataProvider` -> выдаёт `TokenTimeline`.
2. `FeatureExtractor` -> строит `FeatureVector`.
3. `FiltersEngine(config)` -> `PASS/FAIL + reasons`.
4. `ScoringEngine` -> `score + subscores + contributions`.
5. `BacktestEngine` -> per-trade симуляция и агрегаты.
6. `Reporter` -> Markdown/JSON/CSV/plain-text.

## Список модулей
- `providers/*` — источники данных
- `features/extractor.py` — расчёт метрик
- `filters/*` — конфиг и фильтрация
- `scoring/engine.py` — scoring + kNN TP-probabilities
- `backtest/engine.py` — deterministic event-driven simulation
- `reporting/reporter.py` — SolHouse-style markdown output
- `cli/main.py` — команды backtest/scan/render

## Критические security risks
- При добавлении live mode: хранение RPC key / private keys должно идти через env/secret manager, не через файлы.
- Нужен strict allowlist внешних endpoint'ов и timeout/retry политика.
- Нужны валидация входных JSON-схем и защита от poisoned historical datasets.

## Точки внедрения
- Backtest extensions: `BacktestEngine._simulate_trade` (fill/slippage/depth/migration).
- Filters extensions: `FiltersEngine.evaluate`.
- Report extensions: `render_solhouse_style_report`.
