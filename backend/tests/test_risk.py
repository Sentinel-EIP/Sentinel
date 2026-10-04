"""Risk-governor : indicateurs, seuils, donnees perimees, routes."""

import math
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlmodel import Session

from app.models import Candle
from app.risk import metrics
from app.risk.alerts import Thresholds, summarize
from app.services.market import upsert_candles

HOUR = timedelta(hours=1)
T0 = datetime(2026, 10, 1, tzinfo=UTC)


def test_drawdowns() -> None:
    assert metrics.drawdowns([100, 120, 90, 110]) == (pytest.approx(0.25), pytest.approx(1 / 12))
    assert metrics.drawdowns([1, 2, 3]) == (0.0, 0.0)


def test_volatilite_annualisee() -> None:
    closes = [100.0, 101.0, 100.0, 101.0]
    r = math.log(1.01)
    expected = math.sqrt(sum((x - r / 3) ** 2 for x in (r, -r, r)) / 2) * math.sqrt(8760)
    assert metrics.realized_volatility(closes, 8760) == pytest.approx(expected)
    assert metrics.realized_volatility([100.0, 101.0], 8760) is None


def summary_for(
    closes: list[float], late_hours: float = 0, **thresholds: float
) -> list[tuple[str, str]]:
    as_of = T0 + HOUR * (len(closes) - 1)
    now = as_of + HOUR + timedelta(hours=late_hours)
    s = summarize("BTCEUR", "1h", closes, as_of, HOUR, now, Thresholds(**thresholds))
    return [(a.level, a.code) for a in s.alerts]


def test_aucune_alerte_sur_un_marche_calme() -> None:
    assert summary_for([100.0 + 0.01 * (i % 2) for i in range(50)]) == []


@pytest.mark.parametrize(
    ("last", "expected"),
    [(85.0, [("warning", "drawdown")]), (75.0, [("critical", "drawdown")])],
)
def test_seuils_de_drawdown(last: float, expected: list[tuple[str, str]]) -> None:
    closes = [100.0] * 30 + [last]
    assert summary_for(closes, volatility_warning=100, volatility_critical=100) == expected


def test_seuils_de_volatilite() -> None:
    closes = [100.0 * (1.02 if i % 2 else 1.0) for i in range(50)]
    assert summary_for(closes, drawdown_warning=1, drawdown_critical=1) == [
        ("critical", "volatility")
    ]
    assert summary_for(closes, volatility_critical=10, drawdown_warning=1, drawdown_critical=1) == [
        ("warning", "volatility")
    ]


def test_donnees_perimees() -> None:
    calm = [100.0] * 30
    assert summary_for(calm, late_hours=1.5) == []
    assert summary_for(calm, late_hours=3) == [("stale", "data_stale")]


def test_serie_vide() -> None:
    with pytest.raises(ValueError, match="vide"):
        summarize("BTCEUR", "1h", [], T0, HOUR, T0)


def seed(engine: Engine, symbol: str, closes: list[float], end: datetime) -> None:
    start = end - HOUR * (len(closes) - 1)
    with Session(engine) as s:
        upsert_candles(
            s,
            [
                Candle(
                    symbol=symbol,
                    timeframe="1h",
                    ts=start + HOUR * i,
                    open=c,
                    high=c,
                    low=c,
                    close=c,
                    volume=1,
                )
                for i, c in enumerate(closes)
            ],
        )


def test_routes(client: TestClient, engine: Engine, auth_headers: dict[str, str]) -> None:
    fresh = datetime.now(UTC).replace(minute=0, second=0, microsecond=0) - HOUR
    seed(engine, "BTCEUR", [100.0] * 30 + [70.0], fresh)  # drawdown critique
    seed(engine, "ETHEUR", [100.0] * 30, fresh - timedelta(days=2))  # perimees

    r = client.get("/risk/summary?symbol=BTCEUR", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["current_drawdown"] == pytest.approx(0.3)
    assert body["sample_size"] == 31
    assert body["alerts"][0]["level"] == "critical"

    alerts = client.get("/alerts", headers=auth_headers).json()
    assert [(a["symbol"], a["level"]) for a in alerts][0] == ("BTCEUR", "critical")
    assert ("ETHEUR", "stale") in [(a["symbol"], a["level"]) for a in alerts]


def test_symbole_sans_donnees(client: TestClient, auth_headers: dict[str, str]) -> None:
    assert client.get("/risk/summary?symbol=XRPEUR", headers=auth_headers).status_code == 404
    assert client.get("/alerts", headers=auth_headers).json() == []


def test_authentification_requise(client: TestClient) -> None:
    assert client.get("/risk/summary?symbol=BTCEUR").status_code == 401
    assert client.get("/alerts").status_code == 401
