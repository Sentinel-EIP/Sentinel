"""Collecte des bougies : reprise, idempotence, pagination, erreurs."""

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import pytest
from sqlalchemy import Engine
from sqlmodel import Session, select

from app import worker
from app.models import Candle
from app.services import market

NOW = datetime(2026, 10, 4, 12, 30, tzinfo=UTC)
HOUR_MS = 3_600_000


def fake_binance(calls: list[dict[str, Any]], page_size: int = 1000) -> httpx.Client:
    """Binance factice : bougies 1h de startTime jusqu'a NOW (la courante non close)."""

    def handler(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        calls.append(params)
        if params["symbol"] == "INCONNU":
            return httpx.Response(400, json={"code": -1121, "msg": "Invalid symbol."})
        start = int(params["startTime"])
        rows = []
        t = start - start % HOUR_MS
        while t <= market.to_ms(NOW) and len(rows) < page_size:
            price = 100 + (t // HOUR_MS) % 7
            rows.append(
                [
                    t,
                    str(price),
                    str(price + 2),
                    str(price - 1),
                    str(price + 1),
                    "3.5",
                    t + HOUR_MS - 1,
                ]
            )
            t += HOUR_MS
        return httpx.Response(200, json=rows)

    return httpx.Client(base_url="https://binance.test", transport=httpx.MockTransport(handler))


def count(session: Session) -> int:
    return len(session.exec(select(Candle)).all())


def test_premier_passage_puis_reprise(session: Session) -> None:
    calls: list[dict[str, Any]] = []
    client = fake_binance(calls)
    written = market.collect(session, client, "BTCEUR", "1h", NOW, backfill_days=2)
    # 2 jours d'historique, sans la bougie en cours (12:00-13:00 non close).
    assert written == 48
    assert market.last_ts(session, "BTCEUR", "1h") == datetime(2026, 10, 4, 11, tzinfo=UTC)

    # Reprise : demande a partir de la bougie suivante, rien de nouveau a ecrire.
    assert market.collect(session, client, "BTCEUR", "1h", NOW, backfill_days=2) == 0
    assert int(calls[-1]["startTime"]) == market.to_ms(datetime(2026, 10, 4, 12, tzinfo=UTC))
    assert count(session) == 48


def test_upsert_idempotent(session: Session) -> None:
    rows = [[0, "1", "2", "0.5", "1.5", "10", HOUR_MS - 1]]
    first = market.parse_klines("BTCEUR", "1h", rows, NOW)
    market.upsert_candles(session, first)
    corrected = [[0, "1", "2", "0.5", "1.8", "11", HOUR_MS - 1]]
    market.upsert_candles(session, market.parse_klines("BTCEUR", "1h", corrected, NOW))
    candle = session.exec(select(Candle)).one()
    assert (candle.close, candle.volume) == (1.8, 11)
    assert market.upsert_candles(session, []) == 0


def test_pagination(session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(market, "PAGE_SIZE", 10)
    calls: list[dict[str, Any]] = []
    written = market.collect(
        session, fake_binance(calls, page_size=10), "BTCEUR", "1h", NOW, backfill_days=1
    )
    assert written == 24
    assert len(calls) == 3


def test_timeframe_inconnu(session: Session) -> None:
    with pytest.raises(ValueError, match="timeframe inconnu"):
        market.collect(session, fake_binance([]), "BTCEUR", "3h", NOW, 1)


def test_lecture_ordre_chronologique(session: Session) -> None:
    market.collect(session, fake_binance([]), "BTCEUR", "1h", NOW, backfill_days=1)
    last = market.read_candles(session, "BTCEUR", "1h", limit=5)
    assert [market.as_utc(c.ts).hour for c in last] == [7, 8, 9, 10, 11]
    before = market.read_candles(
        session, "BTCEUR", "1h", limit=2, end=datetime(2026, 10, 4, 9, tzinfo=UTC)
    )
    assert [market.as_utc(c.ts).hour for c in before] == [8, 9]


def test_tache_celery(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> None:
    """Un symbole en erreur n'empeche pas les autres."""
    from app.db import session as db_session

    monkeypatch.setattr(db_session, "engine", engine)
    monkeypatch.setattr(worker.settings, "MARKET_SYMBOLS", "BTCEUR,INCONNU")
    monkeypatch.setattr(worker.settings, "MARKET_TIMEFRAMES", "1h")
    monkeypatch.setattr(worker.settings, "MARKET_BACKFILL_DAYS", 1)
    fake = fake_binance([])

    def client_factory(**_: Any) -> httpx.Client:
        return fake

    monkeypatch.setattr(worker.httpx, "Client", client_factory)
    monkeypatch.setattr(worker, "datetime", _FixedNow)
    result = worker.collect_candles.run()
    assert result == {"BTCEUR:1h": 24, "INCONNU:1h": -1}


class _FixedNow(datetime):
    @classmethod
    def now(cls, tz: Any = None) -> "_FixedNow":
        return cls.fromtimestamp(NOW.timestamp(), tz)


def test_ping() -> None:
    assert worker.ping.run() == "pong"


def test_reglages_marche() -> None:
    assert market.TIMEFRAMES["1d"] == timedelta(days=1)
    assert worker.settings.market_symbols == [
        s.strip().upper() for s in worker.settings.MARKET_SYMBOLS.split(",")
    ]
