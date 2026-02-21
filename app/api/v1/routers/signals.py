from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Signal

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("")
def list_signals(
    filter_id: int | None = None,
    risk_level: str | None = None,
    from_ts: datetime | None = None,
    to_ts: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Signal)
    if filter_id:
        query = query.filter(Signal.filter_id == filter_id)
    if risk_level:
        query = query.filter(Signal.risk_level == risk_level)
    if from_ts:
        query = query.filter(Signal.signal_time >= from_ts)
    if to_ts:
        query = query.filter(Signal.signal_time <= to_ts)
    items = query.order_by(Signal.signal_time.desc()).limit(limit).offset(offset).all()
    return items
