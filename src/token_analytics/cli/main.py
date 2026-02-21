from __future__ import annotations

import argparse
import json

from token_analytics.backtest.engine import BacktestEngine, write_backtest_outputs
from token_analytics.features.extractor import FeatureExtractor
from token_analytics.filters.config_loader import load_filter_config
from token_analytics.filters.engine import FiltersEngine
from token_analytics.providers.historical import HistoricalFileProvider
from token_analytics.reporting.reporter import render_global_report, render_solhouse_style_report, write_markdown
from token_analytics.scoring.engine import ScoringEngine


def cmd_backtest(args):
    provider = HistoricalFileProvider(args.dataset)
    fconf = load_filter_config(args.config)
    engine = BacktestEngine(FiltersEngine(fconf), FeatureExtractor(), ScoringEngine())
    trades, token_summary, summary = engine.run(provider.iter_token_timelines())
    write_backtest_outputs(trades, token_summary, summary, args.outdir)
    render_global_report(f"{args.outdir}/token_summary.json", f"{args.outdir}/backtest_summary.json", f"{args.outdir}/global_report.md")


def cmd_scan_token(args):
    with open(args.token_file, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    provider = HistoricalFileProvider(args.token_file)
    timeline = provider.iter_token_timelines()[0]
    extractor = FeatureExtractor()
    fv = extractor.extract(timeline)
    fconf = load_filter_config(args.config)
    fr = FiltersEngine(fconf).evaluate(fv)
    sr = ScoringEngine().score(fv)
    text = render_solhouse_style_report(payload["tokens"][0].get("token_name", "unknown"), timeline.token_mint, fv, fr, sr)
    write_markdown(args.output, text)


def cmd_render_report(args):
    summary = json.loads(open(args.summary_json, "r", encoding="utf-8").read())
    first_mint = next(iter(summary.keys()))
    row = summary[first_mint]
    lines = ["# Token Report", f"- mint: {first_mint}", f"- pass: {row.get('filter_pass')}", f"- score: {row.get('score')}"]
    write_markdown(args.output, "\n".join(lines))


def main():
    parser = argparse.ArgumentParser(prog="token-analytics")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_backtest = sub.add_parser("backtest")
    p_backtest.add_argument("--config", required=True)
    p_backtest.add_argument("--dataset", required=True)
    p_backtest.add_argument("--outdir", required=True)
    p_backtest.set_defaults(func=cmd_backtest)

    p_scan = sub.add_parser("scan-token")
    p_scan.add_argument("--config", required=True)
    p_scan.add_argument("--token-file", required=True)
    p_scan.add_argument("--output", required=True)
    p_scan.set_defaults(func=cmd_scan_token)

    p_render = sub.add_parser("render-report")
    p_render.add_argument("--summary-json", required=True)
    p_render.add_argument("--output", required=True)
    p_render.set_defaults(func=cmd_render_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
