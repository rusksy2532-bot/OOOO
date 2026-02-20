from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, Numeric, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    address: Mapped[str] = mapped_column(Text, unique=True, index=True)
    symbol: Mapped[str | None] = mapped_column(Text)
    name: Mapped[str | None] = mapped_column(Text)
    deploy_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    first_dex_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    launchpad: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_update: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Candle5m(Base):
    __tablename__ = "candles_5m"
    __table_args__ = (UniqueConstraint("token_id", "ts", name="uq_candles_token_ts"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_id: Mapped[int] = mapped_column(ForeignKey("tokens.id"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    open_price: Mapped[float | None] = mapped_column(Numeric)
    high_price: Mapped[float | None] = mapped_column(Numeric)
    low_price: Mapped[float | None] = mapped_column(Numeric)
    close_price: Mapped[float | None] = mapped_column(Numeric)
    volume_usd: Mapped[float | None] = mapped_column(Numeric)
    trades_count: Mapped[int | None] = mapped_column(Integer)
    makers_count: Mapped[int | None] = mapped_column(Integer)
    liquidity_usd: Mapped[float | None] = mapped_column(Numeric)
    market_cap_usd: Mapped[float | None] = mapped_column(Numeric)


class HoldersSnapshot(Base):
    __tablename__ = "holders_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_id: Mapped[int] = mapped_column(ForeignKey("tokens.id"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    holders_total: Mapped[int | None] = mapped_column(Integer)
    top1_share: Mapped[float | None] = mapped_column(Numeric)
    top10_share: Mapped[float | None] = mapped_column(Numeric)
    dev_team_share: Mapped[float | None] = mapped_column(Numeric)
    whale_count: Mapped[int | None] = mapped_column(Integer)


class LaunchStats(Base):
    __tablename__ = "launch_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_id: Mapped[int] = mapped_column(ForeignKey("tokens.id"), unique=True)
    sale_duration_min: Mapped[float | None] = mapped_column(Numeric)
    buyers_count: Mapped[int | None] = mapped_column(Integer)
    tx_count: Mapped[int | None] = mapped_column(Integer)
    total_raised_sol: Mapped[float | None] = mapped_column(Numeric)
    avg_buy_size_sol: Mapped[float | None] = mapped_column(Numeric)
    max_buy_share: Mapped[float | None] = mapped_column(Numeric)
    top10_sale_share: Mapped[float | None] = mapped_column(Numeric)
    bundles_count: Mapped[int | None] = mapped_column(Integer)


class Filter(Base):
    __tablename__ = "filters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    params: Mapped[dict] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (UniqueConstraint("token_id", "filter_id", "signal_time", name="uq_signal_unique"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_id: Mapped[int] = mapped_column(ForeignKey("tokens.id"))
    filter_id: Mapped[int] = mapped_column(ForeignKey("filters.id"), index=True)
    signal_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    entry_price: Mapped[float] = mapped_column(Numeric)
    age_at_signal_min: Mapped[float | None] = mapped_column(Numeric)
    volume_5m: Mapped[float | None] = mapped_column(Numeric)
    makers_5m: Mapped[int | None] = mapped_column(Integer)
    holders: Mapped[int | None] = mapped_column(Integer)
    market_cap_usd: Mapped[float | None] = mapped_column(Numeric)
    liquidity_usd: Mapped[float | None] = mapped_column(Numeric)
    risk_score: Mapped[int | None] = mapped_column(Integer)
    risk_level: Mapped[str | None] = mapped_column(Text, index=True)
    extra_data: Mapped[dict | None] = mapped_column(JSON)


class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filter_id: Mapped[int] = mapped_column(ForeignKey("filters.id"), index=True)
    period_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    period_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    signals_count: Mapped[int] = mapped_column(Integer)
    hit_1_5x: Mapped[int] = mapped_column(Integer)
    hit_2x: Mapped[int] = mapped_column(Integer)
    hit_5x: Mapped[int] = mapped_column(Integer)
    hit_10x: Mapped[int] = mapped_column(Integer)
    pct_1_5x: Mapped[float | None] = mapped_column(Numeric)
    pct_2x: Mapped[float | None] = mapped_column(Numeric)
    pct_5x: Mapped[float | None] = mapped_column(Numeric)
    pct_10x: Mapped[float | None] = mapped_column(Numeric)
    avg_max_r: Mapped[float | None] = mapped_column(Numeric)
    avg_drawdown: Mapped[float | None] = mapped_column(Numeric)
    params: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
