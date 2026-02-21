from __future__ import annotations

from src.providers.base import FilterResult, TokenFeatures


class FiltersEngine:
    """Движок входных фильтров для токенов."""

    def apply_entry_filters(self, features: TokenFeatures, config: dict) -> FilterResult:
        rules = config["entry_filters"]
        reasons: list[str] = []

        self._max_check(features.top10_pct, rules.get("top10_pct_max"), "Концентрация топ-10 слишком высока", reasons)
        self._max_check(features.top1_pct, rules.get("top1_pct_max"), "Концентрация топ-1 слишком высока", reasons)
        self._max_check(features.bundle_supply_pct, rules.get("bundle_supply_pct_max"), "Bundle supply слишком высокий", reasons)
        self._max_check(features.sniper_supply_pct, rules.get("sniper_supply_pct_max"), "Sniper supply слишком высокий", reasons)
        self._max_check(features.early_dump_pct, rules.get("early_dump_pct_max"), "Слишком высокий early dump", reasons)
        self._range_check(features.curve_progress_pct, rules.get("curve_progress_min_pct"), rules.get("curve_progress_max_pct"), "curve_progress_pct", reasons)
        self._range_check(features.age_minutes, rules.get("age_min_minutes"), rules.get("age_max_minutes"), "age_minutes", reasons)

        if features.volume_1h is not None and rules.get("volume_1h_min_usd") is not None and features.volume_1h < rules["volume_1h_min_usd"]:
            reasons.append(f"Низкий volume_1h: {features.volume_1h:.2f} < {rules['volume_1h_min_usd']}")
        if features.volume_surge is not None and rules.get("volume_surge_min") is not None and features.volume_surge < rules["volume_surge_min"]:
            reasons.append(f"Volume surge ниже порога: {features.volume_surge:.2f} < {rules['volume_surge_min']}")

        if features.dev_dead_count is not None and features.dev_dead_count > rules["dev_history"].get("max_past_rugs", 0):
            reasons.append("История dev содержит слишком много мёртвых токенов")
        if features.dev_migrated_count is not None and features.dev_migrated_count < rules["dev_history"].get("min_migrated_count", 0):
            reasons.append("Недостаточно миграций в истории dev")

        return FilterResult(passed=len(reasons) == 0, reasons=reasons)

    def _max_check(self, value: float | None, max_value: float | None, name: str, reasons: list[str]) -> None:
        if value is not None and max_value is not None and value > max_value:
            reasons.append(f"{name}: {value:.1f}% > {max_value}%")

    def _range_check(self, value: float | None, min_value: float | None, max_value: float | None, name: str, reasons: list[str]) -> None:
        if value is None:
            return
        if min_value is not None and value < min_value:
            reasons.append(f"{name} ниже минимума: {value:.2f} < {min_value}")
        if max_value is not None and value > max_value:
            reasons.append(f"{name} выше максимума: {value:.2f} > {max_value}")
