from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


from .backtest import BacktestEngine
from .features import FeatureExtractor
from .filters import FiltersEngine
from .providers import HistoricalFileProvider
from .reporter import Reporter
from .scoring import ScoringEngine
from .simple_yaml import load_simple_yaml


def load_config(path: Path) -> dict:
    return load_simple_yaml(path.read_text())


def group_by_token(events):
    d = defaultdict(list)
    for e in events:
        d[e.token_mint].append(e)
    return d


def cmd_backtest(args):
    cfg = load_config(Path(args.config))
    provider = HistoricalFileProvider(Path(args.events))
    grouped = group_by_token(provider.stream_events())
    bt = BacktestEngine(FeatureExtractor(), FiltersEngine(cfg), cfg)
    reporter = Reporter()
    _, summary, _ = bt.run(grouped, Path(args.out))
    reporter.export_backtest_global(Path(args.out), summary)


def cmd_scan(args):
    cfg = load_config(Path(args.config))
    provider = HistoricalFileProvider(Path(args.events))
    token_events = list(provider.stream_events(token_mint=args.token))
    if not token_events:
        raise SystemExit(f"No events for {args.token}")
    name = next((e.data.get("token_name") for e in token_events if e.event_type == "token_created"), args.token)
    features = FeatureExtractor().extract(args.token, name, token_events)
    filters = FiltersEngine(cfg).evaluate(features)
    score = ScoringEngine(Path(args.neighbors) if args.neighbors else None).score(features)
    reporter = Reporter()
    report = reporter.token_report(features, filters, score)
    reporter.export_token_artifacts(Path(args.out), features, report)
    print(report)


def cmd_report(args):
    payload = json.loads(Path(args.features_json).read_text())
    print(json.dumps(payload, indent=2))


def main():
    parser = argparse.ArgumentParser(prog="token-analytics")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("backtest")
    p1.add_argument("--config", required=True)
    p1.add_argument("--events", required=True)
    p1.add_argument("--out", default="output/backtest")
    p1.set_defaults(func=cmd_backtest)

    p2 = sub.add_parser("scan")
    p2.add_argument("--config", required=True)
    p2.add_argument("--events", required=True)
    p2.add_argument("--token", required=True)
    p2.add_argument("--neighbors")
    p2.add_argument("--out", default="output/scan")
    p2.set_defaults(func=cmd_scan)

    p3 = sub.add_parser("report")
    p3.add_argument("--features-json", required=True)
    p3.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
