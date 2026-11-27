"""Client du service ML (couche 2). Seul point de contact backend -> ML."""

from typing import Any

import httpx

from app.core.config import get_settings


class MLUnavailableError(Exception):
    """Le service ML ne repond pas, ou repond en erreur serveur."""


class MLRejectedError(Exception):
    """Le service ML refuse la requete (donnees insuffisantes ou invalides)."""


def volatility_cone(
    symbol: str,
    closes: list[float],
    horizon_hours: int,
    interval_hours: float,
    confidence: float,
) -> dict[str, Any]:
    payload = {
        "symbol": symbol,
        "closes": closes,
        "horizon_hours": horizon_hours,
        "interval_hours": interval_hours,
        "confidence": confidence,
    }
    try:
        with httpx.Client(base_url=get_settings().ML_SERVICE_URL, timeout=10) as client:
            response = client.post("/volatility/cone", json=payload)
    except httpx.HTTPError as exc:
        raise MLUnavailableError(type(exc).__name__) from exc
    if response.status_code >= 500:
        raise MLUnavailableError(f"http {response.status_code}")
    if response.status_code != 200:
        detail = response.json().get("detail", "requete refusee")
        raise MLRejectedError(str(detail))
    result: dict[str, Any] = response.json()
    return result
