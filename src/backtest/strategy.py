from __future__ import annotations


def should_exit_by_time(hold_minutes: float, max_hold_minutes: float) -> bool:
    """Проверка time-exit."""
    return hold_minutes >= max_hold_minutes
