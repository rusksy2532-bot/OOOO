from __future__ import annotations

from src.providers.base import ScoringResult, TokenFeatures


class ScoringEngine:
    """Взвешенный скоринг токена по блокам market/pressure/risk/dev."""

    def score(self, features: TokenFeatures, weights: dict) -> ScoringResult:
        market = self._bounded(self._avg([features.delta_5m_pct, features.delta_1h_pct, features.curve_progress_pct]))
        pressure = self._bounded(self._avg([
            features.buy_ratio_5m * 100 if features.buy_ratio_5m is not None else None,
            features.volume_surge * 20 if features.volume_surge is not None else None,
        ]))
        risk = self._bounded(100 - self._avg([features.top10_pct, features.top1_pct, features.bundle_supply_pct, features.sniper_supply_pct]))
        dev = self._bounded(self._avg([features.dev_median_roi, (features.dev_migrated_count or 0) * 10]))

        total = (
            market * weights.get("market", 0.25)
            + pressure * weights.get("pressure", 0.25)
            + risk * weights.get("risk", 0.30)
            + dev * weights.get("dev", 0.20)
        )
        return ScoringResult(
            total_score=round(total, 2),
            market_score=round(market, 2),
            pressure_score=round(pressure, 2),
            risk_score=round(risk, 2),
            dev_score=round(dev, 2),
            contributions={
                "market": market,
                "pressure": pressure,
                "risk": risk,
                "dev": dev,
            },
        )

    def _avg(self, vals: list[float | None]) -> float:
        nums = [v for v in vals if v is not None]
        return sum(nums) / len(nums) if nums else 0.0

    def _bounded(self, value: float) -> float:
        return max(0.0, min(100.0, value))
