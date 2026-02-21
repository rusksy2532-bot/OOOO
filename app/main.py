from fastapi import Depends, FastAPI

from app.api.v1.routers import analytics, backtests, filters, signals
from app.core.config import settings
from app.core.security import verify_api_key
from app.db.base import Base
from app.db.init_data import seed_filter_presets
from app.db.session import SessionLocal, engine

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_filter_presets(db)


app.include_router(filters.router, prefix=settings.api_prefix, dependencies=[Depends(verify_api_key)])
app.include_router(backtests.router, prefix=settings.api_prefix, dependencies=[Depends(verify_api_key)])
app.include_router(signals.router, prefix=settings.api_prefix, dependencies=[Depends(verify_api_key)])
app.include_router(analytics.router, prefix=settings.api_prefix, dependencies=[Depends(verify_api_key)])


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
