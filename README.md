# Solana Memecoin Signals (MVP Scaffold)

Базовый каркас платформы для:
- трекинга новых токенов (Pump.fun/PumpPortal),
- применения фильтров к 5m-свечам,
- расчёта риск-скоринга,
- запуска бэктестов.

## Что уже есть
- FastAPI приложение с API key авторизацией (`X-API-Key`).
- SQLAlchemy модели для `tokens`, `candles_5m`, `holders_snapshots`, `launch_stats`, `filters`, `signals`, `backtest_results`.
- CRUD для фильтров.
- Заглушки для backtests/signals/analytics.
- Бизнес-движки:
  - `check_filter(...)`
  - `calc_risk_score(...)`
  - `run_backtest(...)` (без комиссий/проскальзывания, как V1)
- Автоматический сид стартовых фильтров при запуске приложения:
  - `PostMigration_Expansion`
  - `Early_LowCap`
  - `Late_Scalp`

## Что делать дальше (практически)
1. Подними API локально и проверь `/health`.
2. Проверь что фильтры уже сидированы: `GET /api/v1/filters`.
3. Создай первый токен + свечи в БД (черновые данные), затем запусти `check_filter` и `run_backtest`.
4. Следующий рабочий шаг в коде: реализовать collector для Pump.fun WebSocket и запись в `tokens`.

## Быстрый старт
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Пример запросов
```bash
# health
curl http://127.0.0.1:8000/health

# filters (по умолчанию ключ: change-me)
curl -H 'X-API-Key: change-me' http://127.0.0.1:8000/api/v1/filters
```

По умолчанию ключ: `change-me`, заголовок: `X-API-Key`.
