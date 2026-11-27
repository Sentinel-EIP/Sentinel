from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlmodel import Session

from app.models import Candle
from app.services.market import upsert_candles

START = datetime(2026, 10, 1, tzinfo=UTC)


def seed(engine: Engine, symbol: str = "BTCEUR", n: int = 30) -> None:
    with Session(engine) as s:
        upsert_candles(
            s,
            [
                Candle(
                    symbol=symbol,
                    timeframe="1h",
                    ts=START + timedelta(hours=i),
                    open=100 + i,
                    high=101 + i,
                    low=99 + i,
                    close=100.5 + i,
                    volume=1,
                )
                for i in range(n)
            ],
        )


def test_symboles(client: TestClient, engine: Engine, auth_headers: dict[str, str]) -> None:
    seed(engine)
    seed(engine, "ETHEUR", 5)
    body = client.get("/market/symbols", headers=auth_headers).json()
    assert [(s["symbol"], s["count"]) for s in body] == [("BTCEUR", 30), ("ETHEUR", 5)]
    assert body[0]["last"].startswith("2026-10-02T05:00:00")


def test_bougies(client: TestClient, engine: Engine, auth_headers: dict[str, str]) -> None:
    seed(engine)
    r = client.get("/market/candles?symbol=BTCEUR&limit=3", headers=auth_headers)
    assert r.status_code == 200
    assert [c["close"] for c in r.json()] == [127.5, 128.5, 129.5]

    end = (START + timedelta(hours=1)).isoformat()
    r = client.get("/market/candles", params={"symbol": "BTCEUR", "end": end}, headers=auth_headers)
    assert [c["close"] for c in r.json()] == [100.5, 101.5]


def test_parametres_invalides(client: TestClient, auth_headers: dict[str, str]) -> None:
    for query in ["symbol=btc;drop", "symbol=BTCEUR&timeframe=3h", "symbol=BTCEUR&limit=5000"]:
        assert client.get(f"/market/candles?{query}", headers=auth_headers).status_code == 422


def test_authentification_requise(client: TestClient) -> None:
    assert client.get("/market/symbols").status_code == 401
    assert client.get("/market/candles?symbol=BTCEUR").status_code == 401
