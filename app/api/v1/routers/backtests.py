from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import BacktestResult
from app.schemas.backtest import BacktestResultRead, BacktestRunRequest

router = APIRouter(prefix="/backtests", tags=["backtests"])


@router.get("", response_model=list[BacktestResultRead])
def list_backtests(db: Session = Depends(get_db)):
    return db.query(BacktestResult).order_by(BacktestResult.created_at.desc()).all()


@router.post("/run")
def run_backtest_task(payload: BacktestRunRequest, db: Session = Depends(get_db)):
    row = BacktestResult(
        filter_id=payload.filter_id,
        period_from=payload.period_from,
        period_to=payload.period_to,
        signals_count=0,
        hit_1_5x=0,
        hit_2x=0,
        hit_5x=0,
        hit_10x=0,
        pct_1_5x=0,
        pct_2x=0,
        pct_5x=0,
        pct_10x=0,
        avg_max_r=None,
        avg_drawdown=None,
        params=payload.model_dump(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"task_status": "queued", "backtest_id": row.id}


@router.get("/{backtest_id}", response_model=BacktestResultRead)
def get_backtest(backtest_id: int, db: Session = Depends(get_db)):
    return db.get(BacktestResult, backtest_id)
