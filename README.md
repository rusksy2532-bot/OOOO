# Token Analytics + Backtest Framework (Pump.fun/Solana)

## Запуск

### 1) Backtest
```bash
PYTHONPATH=src python -m token_analytics.cli backtest --config config.yaml --events data/sample_events.json --out output/backtest
```

### 2) Scan single token
```bash
PYTHONPATH=src python -m token_analytics.cli scan --config config.yaml --events data/sample_events.json --token TOKEN1 --neighbors data/neighbors.json --out output/scan
```

### 3) Generate report from features json
```bash
PYTHONPATH=src python -m token_analytics.cli report --features-json output/scan/token_features.json
```

## Outputs
- `output/backtest/per_trade.csv`
- `output/backtest/per_token_summary.json`
- `output/backtest/global_report.md`
- `output/backtest/global_summary.csv`
- `output/scan/token_features.json`
- `output/scan/token_report.md`
