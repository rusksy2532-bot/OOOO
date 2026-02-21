from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.backtest.engine import BacktestEngine, calc_backtest_stats
from src.features.extractor import FeatureExtractor
from src.features.similarity import find_similar_tokens
from src.filters.engine import FiltersEngine
from src.providers.historical_provider import HistoricalProvider
from src.providers.live_provider import LiveProvider
from src.reporter.generator import ReportGenerator
from src.scoring.engine import ScoringEngine


def load_config(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def run_scan(mint: str, config: dict) -> None:
    provider = HistoricalProvider()
    events = provider.get_events(mint) or LiveProvider().get_events(mint)
    extractor = FeatureExtractor()
    features = extractor.build(mint, events)
    filters = FiltersEngine().apply_entry_filters(features, config)
    scoring = ScoringEngine().score(features, config["scoring_weights"])
    intel = find_similar_tokens(features, _load_historical_features())
    report = ReportGenerator().generate(features, scoring, filters, intel)
    out = Path("data/results")
    out.mkdir(parents=True, exist_ok=True)
    file = out / f"report_{mint}.md"
    file.write_text(report, encoding="utf-8")
    print(report)


def run_backtest(config: dict) -> None:
    provider = HistoricalProvider()
    extractor = FeatureExtractor()
    filters_engine = FiltersEngine()
    scorer = ScoringEngine()
    backtest = BacktestEngine()

    results = []
    for mint in provider.list_mints():
        events = provider.get_events(mint)
        features = extractor.build(mint, events)
        filter_result = filters_engine.apply_entry_filters(features, config)
        _ = scorer.score(features, config["scoring_weights"])
        result = backtest.run_token(events, features, filter_result, config)
        results.append(result)

    ts = datetime.utcnow().strftime("%Y%m%d")
    out_dir = Path("data/results")
    out_dir.mkdir(parents=True, exist_ok=True)

    trades_file = out_dir / f"trades_{ts}.csv"
    with trades_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(results[0]).keys()) if results else ["mint"])
        writer.writeheader()
        for row in results:
            writer.writerow(asdict(row))

    summary = calc_backtest_stats(results)
    (out_dir / f"summary_{ts}.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / f"report_{ts}.md").write_text(_render_backtest_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def run_report(mint: str, features_file: str, config: dict) -> None:
    from src.providers.base import TokenFeatures

    payload = json.loads(Path(features_file).read_text(encoding="utf-8"))
    features = TokenFeatures(**payload)
    filters = FiltersEngine().apply_entry_filters(features, config)
    scoring = ScoringEngine().score(features, config["scoring_weights"])
    intel = find_similar_tokens(features, _load_historical_features())
    report = ReportGenerator().generate(features, scoring, filters, intel)
    print(report)


def _render_backtest_markdown(summary: dict) -> str:
    lines = ["# Backtest report", ""]
    for key, value in summary.items():
        lines.append(f"- **{key}**: {value if value is not None else 'N/A'}")
    return "\n".join(lines)


def _load_historical_features() -> list[dict]:
    path = Path("data/processed/historical_features.json")
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["scan", "backtest", "report"], required=True)
    parser.add_argument("--token", default="")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--features", default="")
    parser.add_argument("--start", default="")
    parser.add_argument("--end", default="")
    return parser.parse_args()


if __name__ == "__main__":
    load_dotenv()
    args = parse_args()
    config = load_config(args.config)
    if args.mode == "scan":
        run_scan(args.token, config)
    elif args.mode == "backtest":
        run_backtest(config)
    elif args.mode == "report":
        run_report(args.token, args.features, config)
