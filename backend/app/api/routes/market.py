"""Historique de marche : symboles disponibles et bougies."""

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlmodel import col

from app.api.deps import CurrentUser, SessionDep
from app.models import Candle
from app.services.market import as_utc, read_candles

router = APIRouter(prefix="/market", tags=["market"])

Symbol = Annotated[str, Query(pattern=r"^[A-Z0-9]{2,20}$", examples=["BTCEUR"])]
Timeframe = Literal["1m", "15m", "1h", "4h", "1d"]


class SymbolInfo(BaseModel):
    symbol: str
    timeframe: str
    first: datetime
    last: datetime
    count: int


class CandleOut(BaseModel):
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@router.get("/symbols", response_model=list[SymbolInfo])
def symbols(_: CurrentUser, session: SessionDep) -> list[SymbolInfo]:
    # select de SQLAlchemy : celui de sqlmodel est limite a 4 colonnes.
    sym, tf_col, ts = col(Candle.symbol), col(Candle.timeframe), col(Candle.ts)
    query = (
        select(sym, tf_col, func.min(ts), func.max(ts), func.count())
        .group_by(sym, tf_col)
        .order_by(sym, tf_col)
    )
    return [
        SymbolInfo(symbol=symbol, timeframe=tf, first=as_utc(first), last=as_utc(last), count=n)
        for symbol, tf, first, last, n in session.execute(query).all()
    ]


@router.get("/candles", response_model=list[CandleOut])
def candles(
    _: CurrentUser,
    session: SessionDep,
    symbol: Symbol,
    timeframe: Timeframe = "1h",
    limit: int = Query(500, ge=1, le=1000),
    end: datetime | None = None,
) -> list[CandleOut]:
    """Les `limit` dernieres bougies (avant `end` si fourni), ordre chronologique."""
    return [
        CandleOut(
            ts=as_utc(c.ts), **c.model_dump(include={"open", "high", "low", "close", "volume"})
        )
        for c in read_candles(session, symbol, timeframe, limit, end)
    ]
