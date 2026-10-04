"""Historique de marche : collecte des bougies Binance et lecture.

Collecte idempotente : chaque passage reprend apres la derniere bougie stockee
(ou charge MARKET_BACKFILL_DAYS jours au premier passage) et ecrase une bougie
deja presente. Seules les bougies cloturees sont gardees.
"""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from sqlalchemy.dialects import postgresql, sqlite
from sqlmodel import Session, col, func, select

from app.models import Candle

TIMEFRAMES: dict[str, timedelta] = {
    "1m": timedelta(minutes=1),
    "15m": timedelta(minutes=15),
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
}
PAGE_SIZE = 1000  # maximum de l'API klines
MAX_PAGES = 20  # par symbole et par passage : borne la duree d'un passage


def as_utc(ts: datetime) -> datetime:
    """SQLite rend des dates naives : elles sont en UTC."""
    return ts if ts.tzinfo else ts.replace(tzinfo=UTC)


def to_ms(ts: datetime) -> int:
    return int(as_utc(ts).timestamp() * 1000)


def parse_klines(
    symbol: str, timeframe: str, rows: Sequence[Sequence[Any]], now: datetime
) -> list[Candle]:
    """Lignes de /api/v3/klines -> bougies cloturees (close_time passe)."""
    now_ms = to_ms(now)
    return [
        Candle(
            symbol=symbol,
            timeframe=timeframe,
            ts=datetime.fromtimestamp(int(r[0]) / 1000, UTC),
            open=float(r[1]),
            high=float(r[2]),
            low=float(r[3]),
            close=float(r[4]),
            volume=float(r[5]),
        )
        for r in rows
        if int(r[6]) < now_ms
    ]


def upsert_candles(session: Session, candles: Sequence[Candle]) -> int:
    if not candles:
        return 0
    dialect = session.get_bind().dialect.name
    insert = postgresql.insert if dialect == "postgresql" else sqlite.insert
    rows = [c.model_dump() for c in candles]
    stmt = insert(Candle).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["symbol", "timeframe", "ts"],
        set_={k: stmt.excluded[k] for k in ("open", "high", "low", "close", "volume")},
    )
    session.execute(stmt)
    session.commit()
    return len(rows)


def last_ts(session: Session, symbol: str, timeframe: str) -> datetime | None:
    query = select(func.max(Candle.ts)).where(
        Candle.symbol == symbol, Candle.timeframe == timeframe
    )
    ts = session.exec(query).one()
    return as_utc(ts) if ts else None


def fetch_klines(
    client: httpx.Client, symbol: str, timeframe: str, start: datetime
) -> list[list[Any]]:
    response = client.get(
        "/api/v3/klines",
        params={
            "symbol": symbol,
            "interval": timeframe,
            "startTime": to_ms(start),
            "limit": PAGE_SIZE,
        },
    )
    response.raise_for_status()
    rows: list[list[Any]] = response.json()
    return rows


def collect(
    session: Session,
    client: httpx.Client,
    symbol: str,
    timeframe: str,
    now: datetime,
    backfill_days: int,
) -> int:
    """Charge les bougies manquantes d'un symbole. Renvoie le nombre ecrit."""
    if timeframe not in TIMEFRAMES:
        raise ValueError(f"timeframe inconnu : {timeframe} ({', '.join(TIMEFRAMES)})")
    step = TIMEFRAMES[timeframe]
    last = last_ts(session, symbol, timeframe)
    start = last + step if last else now - timedelta(days=backfill_days)
    written = 0
    for _ in range(MAX_PAGES):
        rows = fetch_klines(client, symbol, timeframe, start)
        candles = parse_klines(symbol, timeframe, rows, now)
        written += upsert_candles(session, candles)
        if len(rows) < PAGE_SIZE or not candles:
            break
        start = candles[-1].ts + step
    return written


def read_candles(
    session: Session, symbol: str, timeframe: str, limit: int, end: datetime | None = None
) -> list[Candle]:
    """Les `limit` dernieres bougies avant `end`, dans l'ordre chronologique."""
    query = select(Candle).where(Candle.symbol == symbol, Candle.timeframe == timeframe)
    if end is not None:
        query = query.where(Candle.ts <= end)
    rows = session.exec(query.order_by(col(Candle.ts).desc()).limit(limit)).all()
    return list(reversed(rows))
