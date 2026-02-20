def run_backtest(signals: list[dict], candles_by_signal: dict[int, list[dict]], tp_levels=(1.5, 2.0, 5.0, 10.0), max_hold_minutes=1440, stop_loss=None) -> dict:
    _ = max_hold_minutes
    hit_counts = {tp: 0 for tp in tp_levels}
    max_rs: list[float] = []

    for signal in signals:
        entry = signal["entry_price"]
        sid = signal["id"]
        future_candles = candles_by_signal.get(sid, [])
        seen_hits = {tp: False for tp in tp_levels}
        local_max_r = 1.0

        for candle in future_candles:
            r_high = candle["high_price"] / entry
            r_low = candle["low_price"] / entry
            local_max_r = max(local_max_r, r_high)

            for tp in tp_levels:
                if r_high >= tp:
                    seen_hits[tp] = True

            if stop_loss is not None and r_low <= stop_loss:
                break

        for tp, hit in seen_hits.items():
            if hit:
                hit_counts[tp] += 1

        max_rs.append(local_max_r)

    count = len(signals)

    return {
        "signals_count": count,
        "hit_counts": hit_counts,
        "hit_pct": {tp: (hit_counts[tp] / count * 100 if count else 0) for tp in tp_levels},
        "avg_max_r": (sum(max_rs) / len(max_rs)) if max_rs else None,
        "avg_drawdown": None,
        "params": {
            "tp_levels": tp_levels,
            "max_hold_minutes": max_hold_minutes,
            "stop_loss": stop_loss,
            "fees_and_slippage_included": False,
        },
    }
