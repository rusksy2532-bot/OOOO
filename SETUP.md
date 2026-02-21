## Environment
- OS: Linux
- Python (текущее окружение): 3.10.19
- Python (целевая версия проекта): 3.11+
- Node: not used in current implementation

## Dependencies
Установить зависимости:

```bash
pip install -r requirements.txt
```

Список:
- python-dotenv
- PyYAML
- scikit-learn
- numpy

## Run Commands
```bash
cp .env.example .env
python main.py --mode scan --token <MINT>
python main.py --mode backtest --config config.yaml
python main.py --mode report --token <MINT_ADDRESS> --features data/processed/<mint>.json
```
