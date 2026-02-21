from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.neighbors import NearestNeighbors

from src.providers.base import TokenFeatures

VECTOR_FIELDS = [
    "curve_progress_pct",
    "top10_pct",
    "volume_surge",
    "buy_ratio_5m",
    "sniper_supply_pct",
    "age_minutes",
]


def find_similar_tokens(features: TokenFeatures, historical_db: list[dict], k: int = 20) -> dict[str, Any]:
    rows = [row for row in historical_db if all(row.get(field) is not None for field in VECTOR_FIELDS)]
    target = [getattr(features, field) for field in VECTOR_FIELDS]
    if any(value is None for value in target) or not rows:
        return {
            "tp_1_5x_prob": None,
            "tp_2x_prob": None,
            "tp_3x_prob": None,
            "tp_5x_prob": None,
            "neighbors_count": 0,
            "model_calibration": "N/A",
        }

    matrix = np.array([[row[field] for field in VECTOR_FIELDS] for row in rows], dtype=float)
    model = NearestNeighbors(n_neighbors=min(k, len(rows)))
    model.fit(matrix)
    _, idx = model.kneighbors(np.array([target], dtype=float))
    neighbors = [rows[i] for i in idx[0]]

    def prob(key: str) -> float | None:
        vals = [1 if n.get(key) else 0 for n in neighbors if n.get(key) is not None]
        return (sum(vals) / len(vals) * 100) if vals else None

    return {
        "tp_1_5x_prob": prob("tp_1_5x"),
        "tp_2x_prob": prob("tp_2x"),
        "tp_3x_prob": prob("tp_3x"),
        "tp_5x_prob": prob("tp_5x"),
        "neighbors_count": len(neighbors),
        "model_calibration": "N/A",
    }
