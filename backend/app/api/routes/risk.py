"""Synthese de risque par symbole et alertes en cours."""

from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Candle
from app.risk.alerts import Level, RiskSummary, summarize
from app.services.market import TIMEFRAMES, as_utc, read_candles

router = APIRouter(tags=["risk"])

Timeframe = Literal["1h", "4h", "1d"]


class AlertOut(BaseModel):
    symbol: str
    level: Level
    code: str
    message: str
    value: float
    threshold: float


class RiskSummaryOut(BaseModel):
    symbol: str
    timeframe: str
    as_of: datetime
    last_price: float
    volatility: float | None
    max_drawdown: float
    current_drawdown: float
    sample_size: int
    alerts: list[AlertOut]


def _summary(session: SessionDep, symbol: str, timeframe: str, window: int) -> RiskSummary | None:
    candles = read_candles(session, symbol, timeframe, window)
    if not candles:
        return None
    return summarize(
        symbol,
        timeframe,
        [c.close for c in candles],
        as_utc(candles[-1].ts),
        TIMEFRAMES[timeframe],
        datetime.now(UTC),
    )


@router.get("/risk/summary", response_model=RiskSummaryOut)
def risk_summary(
    _: CurrentUser,
    session: SessionDep,
    symbol: str = Query(pattern=r"^[A-Z0-9]{2,20}$"),
    timeframe: Timeframe = "1h",
    window: int = Query(720, ge=10, le=5000, description="Bougies prises en compte"),
) -> RiskSummary:
    summary = _summary(session, symbol, timeframe, window)
    if summary is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Aucune donnee pour {symbol} {timeframe}")
    return summary


@router.get("/alerts", response_model=list[AlertOut])
def alerts(
    _: CurrentUser,
    session: SessionDep,
    timeframe: Timeframe = "1h",
    window: int = Query(720, ge=10, le=5000),
) -> list[AlertOut]:
    """Alertes en cours sur tous les symboles collectes, critiques d'abord."""
    query = select(Candle.symbol).where(Candle.timeframe == timeframe).distinct()
    found: list[AlertOut] = []
    for symbol in sorted(session.exec(query)):
        summary = _summary(session, symbol, timeframe, window)
        if summary:
            found.extend(AlertOut(**a.__dict__) for a in summary.alerts)
    order = {"critical": 0, "warning": 1, "stale": 2}
    return sorted(found, key=lambda a: order[a.level])
