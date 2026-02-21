from __future__ import annotations


def calc_slippage(
    curve_progress_pct: float | None,
    trade_size_usd: float,
    model: str = "curve_based",
    fixed_slippage_pct: float = 1.0,
) -> float:
    """Расчёт проскальзывания для входа/выхода."""
    if model == "curve_based" and curve_progress_pct is not None:
        base = 0.5
        return base * (1 + curve_progress_pct / 100)
    return fixed_slippage_pct
