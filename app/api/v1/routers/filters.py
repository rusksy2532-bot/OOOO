from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Filter
from app.schemas.filter import FilterCreate, FilterRead, FilterUpdate

router = APIRouter(prefix="/filters", tags=["filters"])


@router.get("", response_model=list[FilterRead])
def list_filters(db: Session = Depends(get_db)):
    return db.query(Filter).order_by(Filter.id.desc()).all()


@router.post("", response_model=FilterRead)
def create_filter(payload: FilterCreate, db: Session = Depends(get_db)):
    row = Filter(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/{filter_id}", response_model=FilterRead)
def update_filter(filter_id: int, payload: FilterUpdate, db: Session = Depends(get_db)):
    row = db.get(Filter, filter_id)
    if not row:
        raise HTTPException(status_code=404, detail="Filter not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{filter_id}")
def deactivate_filter(filter_id: int, db: Session = Depends(get_db)):
    row = db.get(Filter, filter_id)
    if not row:
        raise HTTPException(status_code=404, detail="Filter not found")
    row.is_active = False
    db.commit()
    return {"status": "ok"}
