from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from .models import ScoreResult, TokenFeatures


@dataclass(slots=True)
class ScoringEngine:
    neighbors_path: Path | None = None

    def score(self, features: TokenFeatures) -> ScoreResult:
        f = features.values
        risk = self._bounded(100 - (f.get("top10_pct") or 100) - (f.get("bundle_supply_pct") or 0), 0, 100)
        market = self._bounded((f.get("volume_surge") or 0) * 20 + (f.get("buy_ratio_1h") or 0) * 30, 0, 100)
        dev = self._bounded((f.get("dev_migrated_count") or 0) * 10 - (f.get("dev_dead_on_curve_count") or 0) * 8 + 50, 0, 100)
        score = round(0.4 * market + 0.4 * risk + 0.2 * dev, 2)
        contributions = {
            "market": round(0.4 * market, 2),
            "risk": round(0.4 * risk, 2),
            "dev": round(0.2 * dev, 2),
        }
        tps = self._tp_probs_knn(features)
        return ScoreResult(score=score, sub_scores={"market": market, "risk": risk, "dev": dev}, contributions=contributions, tp_probabilities=tps)

    def _tp_probs_knn(self, features: TokenFeatures) -> dict[str, float]:
        if not self.neighbors_path or not self.neighbors_path.exists():
            return {"x1.5": math.nan, "x2": math.nan, "x3": math.nan, "x5": math.nan}
        import json

        db = json.loads(self.neighbors_path.read_text())
        vec = [features.values.get("volume_1h") or 0, features.values.get("curve_progress_pct") or 0, features.values.get("top10_pct") or 0]
        scored = []
        for row in db:
            rvec = [row.get("volume_1h", 0), row.get("curve_progress_pct", 0), row.get("top10_pct", 0)]
            dist = sum((a - b) ** 2 for a, b in zip(vec, rvec)) ** 0.5
            scored.append((dist, row))
        knn = [x[1] for x in sorted(scored, key=lambda x: x[0])[: min(20, len(scored))]]
        if not knn:
            return {"x1.5": math.nan, "x2": math.nan, "x3": math.nan, "x5": math.nan}
        return {
            "x1.5": sum(1 for x in knn if x.get("hit_1_5x")) / len(knn),
            "x2": sum(1 for x in knn if x.get("hit_2x")) / len(knn),
            "x3": sum(1 for x in knn if x.get("hit_3x")) / len(knn),
            "x5": sum(1 for x in knn if x.get("hit_5x")) / len(knn),
        }

    @staticmethod
    def _bounded(value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, round(value, 2)))
