"""Cone de volatilite : calcul, fiabilite mesuree, validation des entrees."""

import math

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app import volatility
from app.main import app

client = TestClient(app)


def random_walk(n: int, sigma: float = 0.01, seed: int = 7) -> list[float]:
    rng = np.random.default_rng(seed)
    return list(100 * np.exp(np.cumsum(rng.normal(0, sigma, n))))


def test_cone_symetrique_en_log() -> None:
    closes = random_walk(500)
    cone = volatility.volatility_cone(closes, horizon_steps=4, confidence=0.8)
    assert cone.reference_price == pytest.approx(closes[-1])
    assert math.log(cone.upper / cone.reference_price) == pytest.approx(
        -math.log(cone.lower / cone.reference_price)
    )
    assert cone.volatility == pytest.approx(0.01, rel=0.15)


def test_fiabilite_proche_du_niveau_de_confiance() -> None:
    """Sur une marche aleatoire gaussienne, le cone a 80 % contient ~80 % des cas."""
    cone = volatility.volatility_cone(random_walk(1500), horizon_steps=1, confidence=0.8)
    assert cone.reliability == pytest.approx(0.8, abs=0.05)
    assert cone.backtest_size > 1000


def test_historique_trop_court_pour_la_fiabilite() -> None:
    cone = volatility.volatility_cone(random_walk(40), horizon_steps=4, confidence=0.8)
    assert cone.reliability is None


def test_plus_de_confiance_cone_plus_large() -> None:
    closes = random_walk(200)
    narrow = volatility.volatility_cone(closes, 4, 0.5)
    wide = volatility.volatility_cone(closes, 4, 0.95)
    assert wide.upper > narrow.upper and wide.lower < narrow.lower


@pytest.mark.parametrize(
    ("closes", "steps", "message"),
    [
        ([100.0] * 10, 1, "au moins"),
        ([100.0] * 40 + [0.0], 1, "strictement positifs"),
        ([100.0] * 40, 0, "horizon_steps"),
    ],
)
def test_entrees_invalides(closes: list[float], steps: int, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        volatility.volatility_cone(closes, steps, 0.8)


def test_route() -> None:
    r = client.post(
        "/volatility/cone",
        json={
            "symbol": "BTCEUR",
            "horizon_hours": 4,
            "closes": random_walk(300),
            "confidence": 0.8,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["lower"] < body["reference_price"] < body["upper"]
    assert body["model_version"] == volatility.MODEL_VERSION
    assert "80 %" in body["explanation"] or "80%" in body["explanation"]
    assert "direction" in body["note"]


def test_route_horizon_en_bougies_journalieres() -> None:
    r = client.post(
        "/volatility/cone",
        json={
            "symbol": "BTCEUR",
            "horizon_hours": 48,
            "interval_hours": 24,
            "closes": random_walk(60),
        },
    )
    assert r.status_code == 200
    assert r.json()["reliability"] is not None


def cone_via_route(horizon_hours: int, interval_hours: float) -> dict[str, object]:
    r = client.post(
        "/volatility/cone",
        json={
            "symbol": "BTCEUR",
            "horizon_hours": horizon_hours,
            "interval_hours": interval_hours,
            "closes": random_walk(120),
        },
    )
    assert r.status_code == 200
    body: dict[str, object] = r.json()
    return body


def test_explication_cite_l_horizon_reel_quand_il_est_arrondi() -> None:
    # 4 h en bougies journalieres : le cone porte sur une bougie, soit 24 h.
    body = cone_via_route(4, 24)
    assert body["horizon_hours"] == 4
    assert body["effective_horizon_hours"] == 24
    explanation = str(body["explanation"])
    assert "dans 24 h (4 h demandees, arrondies a 1 bougie(s) de 24 h)" in explanation
    # Memes bornes qu'une demande explicite a 24 h : c'est bien le meme calcul.
    exact = cone_via_route(24, 24)
    assert (body["lower"], body["upper"]) == (exact["lower"], exact["upper"])


def test_explication_sans_arrondi_quand_l_horizon_tombe_juste() -> None:
    body = cone_via_route(48, 24)
    assert body["effective_horizon_hours"] == 48
    assert "dans 48 h." in str(body["explanation"])
    assert "arrondies" not in str(body["explanation"])


def test_route_prix_invalides() -> None:
    closes = [100.0] * 40 + [-1.0]
    r = client.post("/volatility/cone", json={"symbol": "BTCEUR", "closes": closes})
    assert r.status_code == 422
    assert "positifs" in r.json()["detail"]


def test_route_historique_trop_court() -> None:
    r = client.post("/volatility/cone", json={"symbol": "BTCEUR", "closes": [1.0] * 5})
    assert r.status_code == 422
