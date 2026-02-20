from datetime import datetime, timezone


def _check_min_max(value: float | int | None, min_value: float | int | None, max_value: float | int | None) -> bool:
    if value is None:
        return False
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def check_filter(candle: dict, holders_snap: dict | None, token: dict, params: dict) -> tuple[bool, str | None]:
    if holders_snap is None:
        return False, "holders_snapshot_missing"

    if token.get("first_dex_time") is None or candle.get("ts") is None:
        return False, "invalid_token_or_candle_time"

    first_dex: datetime = token["first_dex_time"]
    candle_ts: datetime = candle["ts"]

    if first_dex.tzinfo is None:
        first_dex = first_dex.replace(tzinfo=timezone.utc)
    if candle_ts.tzinfo is None:
        candle_ts = candle_ts.replace(tzinfo=timezone.utc)

    age_minutes = (candle_ts - first_dex).total_seconds() / 60

    checks = [
        _check_min_max(age_minutes, params.get("age_min_minutes"), params.get("age_max_minutes")),
        _check_min_max(candle.get("market_cap_usd"), params.get("mc_min_usd"), params.get("mc_max_usd")),
        _check_min_max(candle.get("liquidity_usd"), params.get("liq_min_usd"), params.get("liq_max_usd")),
        _check_min_max(candle.get("volume_usd"), params.get("volume_5m_min_usd"), params.get("volume_5m_max_usd")),
        _check_min_max(candle.get("trades_count"), params.get("trades_5m_min"), None),
        _check_min_max(candle.get("makers_count"), params.get("makers_5m_min"), None),
        _check_min_max(holders_snap.get("holders_total"), params.get("holders_min"), params.get("holders_max")),
        _check_min_max(holders_snap.get("top10_share"), None, params.get("top10_share_max")),
        _check_min_max(holders_snap.get("dev_team_share"), None, params.get("dev_share_max")),
    ]

    return all(checks), None
