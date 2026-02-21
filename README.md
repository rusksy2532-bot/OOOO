# Token Analytics + Backtest Framework (Pump.fun/Solana)

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Backtest
```bash
token-analytics backtest --config examples/config.yaml --dataset examples/historical_tokens.json --outdir reports
```

### Scan single token (historical/live stub)
```bash
token-analytics scan-token --config examples/config.yaml --token-file examples/single_token.json --output reports/single_token_report.md
```

### Generate report from JSON summary
```bash
token-analytics render-report --summary-json reports/token_summary.json --output reports/rendered_report.md
```
