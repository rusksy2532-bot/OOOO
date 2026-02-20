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

## Быстрый старт (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
python -m uvicorn app.main:app --reload
```

## Быстрый старт (Linux/macOS)
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
python -m uvicorn app.main:app --reload
```

## Почему `uvicorn` «не распознано»
В PowerShell это обычно значит, что venv не активирован или Scripts не в PATH.
Надёжный запуск без зависимости от PATH:
```powershell
python -m uvicorn app.main:app --reload
```

## Если `pip install -e .[dev]` падает на build dependencies
1. Убедись, что используешь свежий pip (`python -m pip install --upgrade pip`).
2. Запускай через `python -m pip`, а не `pip`.
3. Проверь, что venv активирован.
4. Если в сети прокси/ограничения, попробуй без изоляции сборки:
```powershell
python -m pip install --no-build-isolation -e .[dev]
```


## Частая ошибка в PowerShell (`curl -H ...`)
Если видишь ошибку `Cannot convert value ... to type IDictionary`, это из-за алиаса `curl` -> `Invoke-WebRequest`.
Используй один из вариантов:

```powershell
# Вариант 1 (рекомендуется)
$headers = @{ "X-API-Key" = "change-me" }
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/filters" -Headers $headers

# Вариант 2 (настоящий curl.exe)
curl.exe -H "X-API-Key: change-me" http://127.0.0.1:8000/api/v1/filters
```

## Пример запросов (Windows PowerShell)
```powershell
# В PowerShell curl = Invoke-WebRequest, поэтому заголовки передаются hashtable
Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:8000/health"

$headers = @{ "X-API-Key" = "change-me" }
Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:8000/api/v1/filters" -Headers $headers
```

## Пример запросов (bash / Git Bash / WSL)
```bash
curl http://127.0.0.1:8000/health
curl -H "X-API-Key: change-me" http://127.0.0.1:8000/api/v1/filters
```

По умолчанию ключ: `change-me`, заголовок: `X-API-Key`.
