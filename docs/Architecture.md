## Repository Structure

```
project/
├── config.yaml
├── .env
├── main.py
├── docs/
│   ├── Audit.md
│   └── Architecture.md
├── data/
│   ├── raw/
│   ├── processed/
│   └── results/
├── src/
│   ├── providers/
│   │   ├── base.py
│   │   ├── live_provider.py
│   │   └── historical_provider.py
│   ├── features/
│   │   ├── extractor.py
│   │   └── similarity.py
│   ├── filters/
│   │   └── engine.py
│   ├── scoring/
│   │   └── engine.py
│   ├── backtest/
│   │   ├── engine.py
│   │   ├── execution_model.py
│   │   └── strategy.py
│   └── reporter/
│       └── generator.py
└── tests/
```

## Data Contracts
См. `src/providers/base.py`: `TokenEvent`, `TokenFeatures`, `FilterResult`, `ScoringResult`.

## Runtime Flow
1. Provider читает события токена (historical/live).
2. FeatureExtractor рассчитывает набор признаков по снапшоту.
3. FiltersEngine применяет пороги из `config.yaml`.
4. ScoringEngine считает weighted score.
5. ReportGenerator формирует SolHouse-style текст.
6. BacktestEngine симулирует вход/выход и метрики.

## Backtest Notes
- Детерминированный проход trade-событий.
- Slippage: `curve_based` или `fixed`.
- Результаты сохраняются в CSV/JSON/Markdown.
