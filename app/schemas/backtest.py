from datetime import datetime

from pydantic import BaseModel


class BacktestRunRequest(BaseModel):
    filter_id: int
    period_from: datetime
    period_to: datetime
    tp_levels: tuple[float, ...] = (1.5, 2.0, 5.0, 10.0)
    max_hold_minutes: int = 1440
    stop_loss: float | None = None


class BacktestResultRead(BaseModel):
    id: int
    filter_id: int
    signals_count: int
    avg_max_r: float | None
    created_at: datetime

    model_config = {"from_attributes": True}
