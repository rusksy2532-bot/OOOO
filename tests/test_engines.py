from datetime import datetime, timedelta, timezone

from app.services.backtest_engine import run_backtest
from app.services.filters_engine import check_filter
from app.services.risk_engine import calc_risk_score


def test_check_filter_passes_with_valid_inputs():
    now = datetime.now(timezone.utc)
    token = {"first_dex_time": now - timedelta(minutes=30)}
    candle = {
        "ts": now,
        "market_cap_usd": 50000,
        "liquidity_usd": 20000,
        "volume_usd": 25000,
        "trades_count": 40,
        "makers_count": 90,
    }
    snap = {"holders_total": 350, "top10_share": 0.6, "dev_team_share": 0.2}
    params = {
        "age_min_minutes": 20,
        "age_max_minutes": 240,
        "mc_min_usd": 20000,
        "mc_max_usd": 250000,
        "liq_min_usd": 15000,
        "liq_max_usd": 80000,
        "volume_5m_min_usd": 20000,
        "volume_5m_max_usd": None,
        "trades_5m_min": 20,
        "makers_5m_min": 80,
        "holders_min": 300,
        "holders_max": None,
        "top10_share_max": 0.7,
        "dev_share_max": 0.5,
    }
    ok, reason = check_filter(candle, snap, token, params)
    assert ok is True
    assert reason is None


def test_calc_risk_score_high():
    launch = {
        "sale_duration_min": 5,
        "buyers_count": 20,
        "max_buy_share": 0.3,
        "top10_sale_share": 0.8,
        "bundles_count": 4,
    }
    snap = {"holders_total": 20, "top10_share": 0.8, "dev_team_share": 0.6, "whale_count": 7}
    score, level = calc_risk_score(launch, snap)
    assert score == 10
    assert level == "high"


def test_run_backtest_counts_hits():
    signals = [{"id": 1, "entry_price": 1.0}]
    candles = {1: [{"high_price": 2.1, "low_price": 0.95}, {"high_price": 5.2, "low_price": 0.8}]}
    result = run_backtest(signals, candles)
    assert result["signals_count"] == 1
    assert result["hit_counts"][2.0] == 1
    assert result["hit_counts"][5.0] == 1
