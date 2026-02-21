from __future__ import annotations

from dataclasses import dataclass

from token_analytics.models.types import FeatureVector, FilterResult


@dataclass(slots=True)
class FilterConfig:
    min_curve_mc: float | None = None
    max_curve_mc: float | None = None
    min_age_minutes: float | None = None
    max_age_minutes: float | None = None
    min_volume_1h: float | None = None
    volume_surge_min: float | None = None
    max_top10_pct: float | None = None
    max_top1_pct: float | None = None
    max_fresh_top_holders_pct: float | None = None
    max_early_dump_pct: float | None = None
    max_bundle_supply_pct: float | None = None
    max_sniper_supply_pct: float | None = None
    dev_history_max_past_rugs: int | None = None
    dev_history_min_migrated_count: int | None = None
    curve_progress_min: float | None = None
    curve_progress_max: float | None = None


class FiltersEngine:
    def __init__(self, config: FilterConfig) -> None:
        self.config = config

    def evaluate(self, fv: FeatureVector) -> FilterResult:
        reasons: list[str] = []
        values = fv.values
        self._check_range("curve_mc", values.get("curve_mc"), self.config.min_curve_mc, self.config.max_curve_mc, reasons)
        self._check_range("age_minutes", values.get("age_minutes"), self.config.min_age_minutes, self.config.max_age_minutes, reasons)
        self._check_min("volume_1h", values.get("volume_1h"), self.config.min_volume_1h, reasons)
        self._check_min("volume_surge", values.get("volume_surge"), self.config.volume_surge_min, reasons)
        self._check_max("top10_pct", values.get("top10_pct"), self.config.max_top10_pct, reasons)
        self._check_max("top1_pct", values.get("top1_pct"), self.config.max_top1_pct, reasons)
        self._check_max("fresh_top_holders_pct", values.get("fresh_top_holders_pct"), self.config.max_fresh_top_holders_pct, reasons)
        self._check_max("early_dump_pct", values.get("early_dump_pct"), self.config.max_early_dump_pct, reasons)
        self._check_max("bundle_supply_pct", values.get("bundle_supply_pct"), self.config.max_bundle_supply_pct, reasons)
        self._check_max("sniper_supply_pct", values.get("sniper_supply_pct"), self.config.max_sniper_supply_pct, reasons)
        self._check_min("dev_migrated_count", values.get("dev_migrated_count"), self.config.dev_history_min_migrated_count, reasons)
        self._check_max("dev_dead_on_curve_count", values.get("dev_dead_on_curve_count"), self.config.dev_history_max_past_rugs, reasons)
        self._check_range(
            "curve_progress_pct",
            values.get("curve_progress_pct"),
            self.config.curve_progress_min,
            self.config.curve_progress_max,
            reasons,
        )
        return FilterResult(passed=not reasons, reasons=reasons)

    def _check_min(self, field: str, value, threshold, reasons: list[str]) -> None:
        if threshold is None or value is None:
            return
        if value < threshold:
            reasons.append(f"FAIL {field}: {value} < min {threshold}")

    def _check_max(self, field: str, value, threshold, reasons: list[str]) -> None:
        if threshold is None or value is None:
            return
        if value > threshold:
            reasons.append(f"FAIL {field}: {value} > max {threshold}")

    def _check_range(self, field: str, value, low, high, reasons: list[str]) -> None:
        if value is None:
            return
        if low is not None and value < low:
            reasons.append(f"FAIL {field}: {value} < min {low}")
        if high is not None and value > high:
            reasons.append(f"FAIL {field}: {value} > max {high}")
