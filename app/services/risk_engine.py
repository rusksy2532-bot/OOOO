def calc_risk_score(launch: dict | None, snap: dict | None, candle: dict | None = None) -> tuple[int, str]:
    _ = candle
    launch = launch or {}
    snap = snap or {}

    score = 0

    if launch.get("sale_duration_min") is not None and launch["sale_duration_min"] < 10:
        score += 2
    if launch.get("buyers_count") is not None and launch["buyers_count"] < 50:
        score += 2
    if launch.get("max_buy_share") is not None and launch["max_buy_share"] > 0.25:
        score += 2
    if launch.get("top10_sale_share") is not None and launch["top10_sale_share"] > 0.70:
        score += 2
    if launch.get("bundles_count") is not None and launch["bundles_count"] >= 3:
        score += 2

    if snap.get("holders_total") is not None and snap["holders_total"] < 50:
        score += 1
    if snap.get("top10_share") is not None and snap["top10_share"] > 0.70:
        score += 2
    if snap.get("dev_team_share") is not None and snap["dev_team_share"] > 0.50:
        score += 2
    if snap.get("whale_count") is not None and snap["whale_count"] >= 5:
        score += 1

    score = min(10, max(0, score))

    if score <= 3:
        return score, "low"
    if score <= 6:
        return score, "medium"
    return score, "high"
