from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/by_hour")
def by_hour(filter_id: int):
    return {"filter_id": filter_id, "note": "TODO: implement aggregation by hour"}


@router.get("/by_weekday")
def by_weekday(filter_id: int):
    return {"filter_id": filter_id, "note": "TODO: implement aggregation by weekday"}


@router.get("/by_risk")
def by_risk(filter_id: int):
    return {"filter_id": filter_id, "note": "TODO: implement aggregation by risk level"}


@router.get("/by_params")
def by_params(filter_id: int):
    return {"filter_id": filter_id, "note": "TODO: implement parameter analytics"}
