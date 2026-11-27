"""Analyses : appel du service ML, stockage, erreurs, historique."""

import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlmodel import Session

from app.models import Candle
from app.services import ml_client
from app.services.market import upsert_candles

START = datetime(2026, 9, 1, tzinfo=UTC)


def seed(engine: Engine, n: int) -> None:
    with Session(engine) as s:
        upsert_candles(
            s,
            [
                Candle(
                    symbol="BTCEUR",
                    timeframe="1h",
                    ts=START + timedelta(hours=i),
                    open=100,
                    high=101,
                    low=99,
                    close=100 + (i % 5),
                    volume=1,
                )
                for i in range(n)
            ],
        )


def ml_cone(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    last = body["closes"][-1]
    return httpx.Response(
        200,
        json={
            "symbol": body["symbol"],
            "horizon_hours": body["horizon_hours"],
            "effective_horizon_hours": float(body["horizon_hours"]),
            "confidence": body["confidence"],
            "reference_price": last,
            "lower": last * 0.97,
            "upper": last * 1.03,
            "volatility": 0.01,
            "reliability": 0.79,
            "backtest_size": 400,
            "sample_size": len(body["closes"]) - 1,
            "model_version": "realized-vol-v1",
            "explanation": "explication",
            "note": "Amplitude probable. Aucune direction implicite.",
        },
    )


def fake_ml(
    monkeypatch: pytest.MonkeyPatch, handler: Callable[[httpx.Request], httpx.Response]
) -> list[dict[str, Any]]:
    """Remplace le service ML ; renvoie la liste des corps de requete recus."""
    seen: list[dict[str, Any]] = []
    real = httpx.Client

    def recording(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        return handler(request)

    def factory(**kwargs: Any) -> httpx.Client:
        return real(transport=httpx.MockTransport(recording), **kwargs)

    monkeypatch.setattr(ml_client.httpx, "Client", factory)
    return seen


BODY = {"symbol": "BTCEUR", "timeframe": "1h", "horizon_hours": 4, "confidence": 0.8}


def test_analyse_stockee_et_journalisee(
    client: TestClient,
    engine: Engine,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed(engine, 600)
    seen = fake_ml(monkeypatch, ml_cone)
    r = client.post("/analysis/volatility", json=BODY, headers=auth_headers)
    assert r.status_code == 201, r.text
    result = r.json()
    assert result["kind"] == "volatility_cone"
    assert result["reliability"] == 0.79
    assert result["value"]["upper"] > result["value"]["lower"]
    assert result["value"]["as_of"].startswith("2026-09-25T23:00:00")
    # 500 dernieres bougies, pas de 1 h, dans l'ordre.
    assert len(seen[0]["closes"]) == 500 and seen[0]["interval_hours"] == 1

    history = client.get("/analysis/results?symbol=BTCEUR", headers=auth_headers).json()
    assert [h["id"] for h in history] == [result["id"]]
    assert client.get("/analysis/results?kind=autre", headers=auth_headers).json() == []
    activity = client.get("/users/me/activity", headers=auth_headers).json()
    assert activity[0]["action"] == "analysis.volatility"


def test_resultats_limites_a_l_utilisateur_connecte(
    client: TestClient,
    engine: Engine,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed(engine, 600)
    fake_ml(monkeypatch, ml_cone)
    mine = client.post("/analysis/volatility", json=BODY, headers=auth_headers).json()

    bob = {"username": "bob", "password": "autre-mot-de-passe"}
    assert client.post("/auth/register", json=bob).status_code == 201
    token = client.post("/auth/login", json=bob).json()["access_token"]
    bob_headers = {"Authorization": f"Bearer {token}"}

    # Bob ne voit pas l'analyse d'alice, alice la voit.
    assert client.get("/analysis/results", headers=bob_headers).json() == []
    alice_ids = [h["id"] for h in client.get("/analysis/results", headers=auth_headers).json()]
    assert alice_ids == [mine["id"]]


def test_historique_insuffisant(
    client: TestClient, engine: Engine, auth_headers: dict[str, str]
) -> None:
    seed(engine, 10)
    r = client.post("/analysis/volatility", json=BODY, headers=auth_headers)
    assert r.status_code == 409
    assert "10 bougies" in r.json()["error"]["message"]


@pytest.mark.parametrize(
    ("handler", "code"),
    [
        (lambda _: httpx.Response(500, json={}), 503),
        (lambda _: httpx.Response(422, json={"detail": "prix invalides"}), 422),
    ],
)
def test_erreurs_du_service_ml(
    client: TestClient,
    engine: Engine,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
    handler: Callable[[httpx.Request], httpx.Response],
    code: int,
) -> None:
    seed(engine, 100)
    fake_ml(monkeypatch, handler)
    r = client.post("/analysis/volatility", json=BODY, headers=auth_headers)
    assert r.status_code == code


def test_service_ml_injoignable(
    client: TestClient,
    engine: Engine,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed(engine, 100)

    def down(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refuse")

    fake_ml(monkeypatch, down)
    r = client.post("/analysis/volatility", json=BODY, headers=auth_headers)
    assert r.status_code == 503
    assert r.json()["error"]["message"] == "Service d'analyse indisponible"


def test_authentification_requise(client: TestClient) -> None:
    assert client.post("/analysis/volatility", json=BODY).status_code == 401
    assert client.get("/analysis/results").status_code == 401
