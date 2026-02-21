from __future__ import annotations

from token_analytics.filters.engine import FilterConfig


def _parse_scalar(value: str):
    v = value.strip()
    if v in {"true", "True"}:
        return True
    if v in {"false", "False"}:
        return False
    try:
        if "." in v:
            return float(v)
        return int(v)
    except ValueError:
        return v.strip('"').strip("'")


def _simple_yaml_parse(path: str) -> dict:
    root: dict = {}
    stack: list[tuple[int, dict]] = [(0, root)]
    with open(path, "r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            if not line.strip() or line.strip().startswith("#"):
                continue
            if line.lstrip().startswith("-"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            key, _, val = line.strip().partition(":")

            while stack and indent < stack[-1][0]:
                stack.pop()
            parent = stack[-1][1]

            if val.strip() == "":
                parent[key] = {}
                stack.append((indent + 2, parent[key]))
            else:
                parent[key] = _parse_scalar(val)
    return root


def load_filter_config(path: str) -> FilterConfig:
    raw = _simple_yaml_parse(path)
    entry = raw.get("entry_filters", {})
    return FilterConfig(
        min_curve_mc=entry.get("min_curve_mc"),
        max_curve_mc=entry.get("max_curve_mc"),
        min_age_minutes=entry.get("min_age_minutes"),
        max_age_minutes=entry.get("max_age_minutes"),
        min_volume_1h=entry.get("min_volume_1h"),
        volume_surge_min=entry.get("volume_surge_min"),
        max_top10_pct=entry.get("max_top10_pct"),
        max_top1_pct=entry.get("max_top1_pct"),
        max_fresh_top_holders_pct=entry.get("max_fresh_top_holders_pct"),
        max_early_dump_pct=entry.get("max_early_dump_pct"),
        max_bundle_supply_pct=entry.get("max_bundle_supply_pct"),
        max_sniper_supply_pct=entry.get("max_sniper_supply_pct"),
        dev_history_max_past_rugs=entry.get("dev_history", {}).get("max_past_rugs") if isinstance(entry.get("dev_history"), dict) else None,
        dev_history_min_migrated_count=entry.get("dev_history", {}).get("min_migrated_count") if isinstance(entry.get("dev_history"), dict) else None,
        curve_progress_min=entry.get("curve_progress_min"),
        curve_progress_max=entry.get("curve_progress_max"),
    )
