from __future__ import annotations

from dataclasses import dataclass

from .models import FilterResult, TokenFeatures


@dataclass(slots=True)
class FiltersEngine:
    config: dict

    def evaluate(self, features: TokenFeatures) -> FilterResult:
        f = features.values
        c = self.config.get("entry_filters", {})
        reasons: list[str] = []

        self._check_range("curve_mc", f.get("curve_mc"), c.get("curve_mc_min"), c.get("curve_mc_max"), reasons)
        self._check_range("age_minutes", f.get("age_minutes"), c.get("age_minutes_min"), c.get("age_minutes_max"), reasons)
        self._check_min("volume_1h", f.get("volume_1h"), c.get("volume_1h_min"), reasons)
        self._check_min("volume_surge", f.get("volume_surge"), c.get("volume_surge_min"), reasons)

        self._check_max("top10_pct", f.get("top10_pct"), c.get("top10_pct_max"), reasons)
        self._check_max("top1_pct", f.get("top1_pct"), c.get("top1_pct_max"), reasons)
        self._check_max("fresh_top_holders_pct", f.get("fresh_top_holders_pct"), c.get("fresh_top_holders_pct_max"), reasons)
        self._check_max("early_dump_pct", f.get("early_dump_pct"), c.get("early_dump_pct_max"), reasons)
        self._check_max("bundle_supply_pct", f.get("bundle_supply_pct"), c.get("bundle_supply_pct_max"), reasons)
        self._check_max("sniper_supply_pct", f.get("sniper_supply_pct"), c.get("sniper_supply_pct_max"), reasons)

        self._check_max("dev_past_rugs", f.get("dev_dead_on_curve_count"), c.get("dev_past_rugs_max"), reasons)
        self._check_min("dev_migrated_count", f.get("dev_migrated_count"), c.get("dev_migrated_count_min"), reasons)
        self._check_range(
            "curve_progress_pct", f.get("curve_progress_pct"), c.get("curve_progress_min"), c.get("curve_progress_max"), reasons
        )
        return FilterResult(passed=not reasons, reasons=reasons)

    def _check_min(self, name: str, value, min_value, reasons: list[str]):
        if min_value is None or value is None:
            return
        if value < min_value:
            reasons.append(f"FAIL {name}: {value:.4f} < min {min_value}")

    def _check_max(self, name: str, value, max_value, reasons: list[str]):
        if max_value is None or value is None:
            return
        if value > max_value:
            reasons.append(f"FAIL {name}: {value:.4f} > max {max_value}")

    def _check_range(self, name: str, value, min_value, max_value, reasons: list[str]):
        if value is None:
            return
        if min_value is not None and value < min_value:
            reasons.append(f"FAIL {name}: {value:.4f} < min {min_value}")
        if max_value is not None and value > max_value:
            reasons.append(f"FAIL {name}: {value:.4f} > max {max_value}")
