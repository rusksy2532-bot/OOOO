from __future__ import annotations

import math

from token_analytics.models.types import FeatureVector, ScoreResult


class ScoringEngine:
    def score(self, fv: FeatureVector) -> ScoreResult:
        v = fv.values
        contrib = {
            "volume": self._cap((v.get("volume_surge") or 0) * 15, 0, 25),
            "pressure": self._cap((v.get("buy_ratio_1h") or 0.5) * 30, 0, 30),
            "market": self._market_component(v.get("curve_progress_pct"), v.get("migrated")),
            "risk_penalty": -self._risk_penalty(v),
        }
        total = max(0, min(100, sum(contrib.values())))
        subs = {
            "Market": max(0.0, contrib["market"]),
            "Risk": max(0.0, 30 - abs(contrib["risk_penalty"])),
            "Flow": contrib["pressure"],
            "Momentum": contrib["volume"],
        }
        return ScoreResult(total_score=round(total, 2), subscores=subs, contributions=contrib)

    def _market_component(self, curve_progress, migrated) -> float:
        if curve_progress is None:
            return 12.0
        base = 20 - abs(70 - curve_progress) * 0.2
        if migrated:
            base += 3
        return self._cap(base, 0, 25)

    def _risk_penalty(self, v: dict) -> float:
        keys = ["top10_pct", "top1_pct", "bundle_supply_pct", "sniper_supply_pct", "early_dump_pct"]
        penalty = 0.0
        for key in keys:
            val = v.get(key)
            if val is not None:
                penalty += float(val) * 0.2
        return min(30.0, penalty)

    def _cap(self, x: float, lo: float, hi: float) -> float:
        return min(hi, max(lo, x))


def knn_tp_probabilities(target: FeatureVector, history: list[tuple[FeatureVector, dict]], k: int = 5) -> dict[str, float | None]:
    usable = []
    dims = ["volume_surge", "buy_ratio_1h", "delta_1h", "curve_progress_pct"]
    for fv, outcome in history:
        dist = _distance(target.values, fv.values, dims)
        if dist is not None:
            usable.append((dist, outcome))
    usable.sort(key=lambda x: x[0])
    neighbors = usable[:k]
    if not neighbors:
        return {"tp_1_5": None, "tp_2": None, "tp_3": None, "tp_5": None}

    def ratio(key: str) -> float:
        return sum(1 for _, out in neighbors if out.get(key)) / len(neighbors)

    return {"tp_1_5": ratio("hit_tp_1_5"), "tp_2": ratio("hit_tp_2"), "tp_3": ratio("hit_tp_3"), "tp_5": ratio("hit_tp_5")}


def _distance(a: dict, b: dict, dims: list[str]) -> float | None:
    parts = []
    for d in dims:
        if a.get(d) is None or b.get(d) is None:
            continue
        parts.append((float(a[d]) - float(b[d])) ** 2)
    if not parts:
        return None
    return math.sqrt(sum(parts))
