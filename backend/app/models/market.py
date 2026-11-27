"""Historique de marche : bougies OHLCV.

En production, `candles` est une hypertable TimescaleDB (migration), compressee
apres 30 jours. La cle (symbol, timeframe, ts) rend l'ingestion idempotente.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class Candle(SQLModel, table=True):
    __tablename__ = "candles"

    symbol: str = Field(max_length=20, primary_key=True)
    timeframe: str = Field(max_length=8, primary_key=True)  # ex. 1h, 1d
    # Ouverture de la bougie, UTC. Dernier element de la cle : colonne de
    # partitionnement de l'hypertable.
    ts: datetime = Field(sa_column=Column(DateTime(timezone=True), primary_key=True))
    open: float
    high: float
    low: float
    close: float
    volume: float
