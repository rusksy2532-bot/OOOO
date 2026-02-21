# Audit.md

## PHASE 0 — развертывание и стек

> Ограничение среды: архив `https://github.com/Jackhuang166/ai-memecoin-trading-bot` недоступен из контейнера (403 CONNECT tunnel), поэтому аудит исходного репозитория выполнен как **gap-audit** по требуемому функционалу и реализован новый каркас V2 в текущем репо.

### Команды, которые были выполнены
- `git clone https://github.com/Jackhuang166/ai-memecoin-trading-bot source_repo` → 403.
- `curl -I https://codeload.github.com/...` → 403.

### Текущая структура (после реализации V2 каркаса)
- `src/token_analytics/` — ядро framework.
- `config.yaml` — фильтры/пороги/execution.
- `data/sample_events.json` — пример исторических событий.
- `data/neighbors.json` — база для kNN вероятностей TP.
- `Architecture.md` — целевая архитектура.

### Стек
- Язык: Python 3.10+
- Зависимости: стандартная библиотека Python (кастомный простой YAML parser)
- Entry points:
  - `token-analytics backtest ...`
  - `token-analytics scan ...`
  - `token-analytics report ...`

## PHASE 1 — аудит (data/decision/security/gaps)

## A) Data sources (что реализовано в V2)
- `HistoricalFileProvider` читает события из CSV/JSON и нормализует в `Event`.
- `LiveRpcWsProvider` определен как интерфейсный слой (заглушка) для будущей интеграции Solana RPC/WS.
- Единые события: `token_created`, `trade`, `curve_progress`, `holder_snapshot`, `dev_history`, `migration` (через `event_type`).

## B) Decision logic
- Стратегия и сигналы:
  - Entry: только после `FiltersEngine PASS`.
  - Exit: `TP/SL/time_exit/risk_exit/end_of_data`.
- Risk control:
  - фильтры концентрации/снайперов/бандлов/истории дева;
  - execution учитывает slippage + fee.
- Лог сделок:
  - `output/backtest/per_trade.csv`, `per_token_summary.json`.
- Конфиги/секреты:
  - `config.yaml`; ключи/кошельки не хранятся в коде.

## C) Gap-аналитика (по сравнению с SolHouse-style)
- Что покрыто:
  - market/pressure/risk/dev-history признаки;
  - фильтры с fail reasons;
  - deterministic backtest;
  - markdown/json/csv репорты.
- Что пока N/A без ончейн-обогащения:
  - точный bundle clustering,
  - достоверная идентификация sniper cohort,
  - dev wallet graph across launches,
  - migration/liquidity lifecycle из реального DEX event stream.

## Dataflow diagram (text)
1. Provider загружает события (`Event`).
2. `FeatureExtractor` вычисляет фичи токена (детерминированно по timeline).
3. `FiltersEngine` применяет пороги из `config.yaml` → PASS/FAIL + причины.
4. `ScoringEngine` рассчитывает общий score + sub-scores + kNN TP probabilities.
5. `BacktestEngine` запускает event-driven симуляцию и формирует сделки/метрики.
6. `Reporter` экспортирует Markdown/JSON/CSV.

## Модули
- `models.py` — типы данных.
- `providers.py` — live/historical providers.
- `features.py` — feature extraction.
- `filters.py` — filters engine.
- `scoring.py` — scoring + intelligence.
- `backtest.py` — симуляция и метрики.
- `reporter.py` — отчеты.
- `cli.py` — команды.

## Critical security risks
- Нельзя хранить приватные ключи в `config.yaml` (только env/secret manager).
- Для live режима нужен rate-limit + retry/backoff на RPC/WS.
- Валидация входных CSV/JSON обязательна (защита от malformed data).
- Отдельный sandbox для исполнения стратегий/плагинов.

## Точки внедрения
- Backtest/filters/report уже отделены интерфейсами и могут расширяться без изменения provider API.
