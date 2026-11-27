"""Service des modeles IA — couche 2 (analyse).

Isole du backend : les dependances lourdes (PyTorch, transformers) ne doivent
pas ralentir les rebuilds de l'API.

Modules prevus, conformes au dossier technique :
  - indicateurs techniques (ta)
  - volatilite : modele de cone de volatilite
  - sentiment : scoring du flux de news
  - anomalies : detection de regimes de stress

Chaque sortie porte son niveau de confiance et son explication (US3.4).
Une direction de prix (tendance, signal achat / vente) peut etre produite,
toujours avec sa fiabilite mesuree : decision du 2026-09-27, a valider (voir
CONTRIBUTING, regle 1, et docs/ECARTS.md, E10).
"""

import math
import os
import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.volatility import MIN_RETURNS, MODEL_VERSION
from app.volatility import volatility_cone as compute_cone


def check_model_cache(*paths: str) -> None:
    """Echoue au demarrage si un cache de modeles n'est pas inscriptible.

    Sans ce controle, un volume cree par une autre image (fichiers root) ne se
    revele qu'au premier telechargement de modele, par un PermissionError loin
    de sa cause. Voir docs/ECARTS.md.
    """
    for path in paths:
        try:
            os.makedirs(path, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path):
                pass
        except OSError as exc:
            raise RuntimeError(
                f"{path} n'est pas inscriptible par l'uid {os.getuid()} ({exc}). "
                "Volume de modeles cree par une autre image ? Voir docs/ECARTS.md."
            ) from exc


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    caches = [get_settings().ML_MODEL_CACHE]
    if os.environ.get("HF_HOME"):
        caches.append(os.environ["HF_HOME"])
    check_model_cache(*caches)
    yield


app = FastAPI(title="Sentinel ML", version="0.1.0", lifespan=lifespan)

# /metrics : scrape interne par Prometheus (ml:8100/metrics). Un seul processus
# uvicorn : pas de mode multi-processus ici.
Instrumentator().instrument(app).expose(app, include_in_schema=False)


class VolatilityConeRequest(BaseModel):
    symbol: str = Field(examples=["BTCEUR"])
    horizon_hours: int = Field(default=4, ge=1, le=168)
    # Prix de cloture, du plus ancien au plus recent, a pas regulier.
    closes: list[float] = Field(min_length=MIN_RETURNS + 1, max_length=5000)
    interval_hours: float = Field(default=1, gt=0, le=24, description="Pas entre deux prix")
    confidence: float = Field(default=0.8, ge=0.5, le=0.99)


class VolatilityConeResponse(BaseModel):
    symbol: str
    horizon_hours: int = Field(description="Horizon demande")
    effective_horizon_hours: float = Field(
        description="Horizon reellement couvert : un nombre entier de bougies, >= horizon demande"
    )
    confidence: float = Field(description="Niveau de confiance de l'intervalle, 0-1")
    reference_price: float
    lower: float
    upper: float
    volatility: float = Field(description="Ecart-type des rendements log, par bougie")
    reliability: float | None = Field(
        description="Part des cas passes ou le cone a contenu le mouvement reel, 0-1"
    )
    backtest_size: int
    sample_size: int
    model_version: str = MODEL_VERSION
    explanation: str
    note: str = "Amplitude probable. Aucune direction implicite."


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/models")
def list_models() -> dict[str, list[str]]:
    """Inventaire des modules. Le cone de volatilite est un calcul, sans poids."""
    return {"loaded": ["volatility_cone"], "available": ["volatility_cone", "sentiment", "regime"]}


@app.post("/volatility/cone", response_model=VolatilityConeResponse)
def volatility_cone(req: VolatilityConeRequest) -> VolatilityConeResponse:
    """Amplitude probable du prix a l'horizon demande (volatilite realisee)."""
    # Le cone couvre un nombre entier de bougies : l'horizon reel peut depasser
    # l'horizon demande (4 h en bougies de 24 h = 1 bougie = 24 h). L'explication
    # cite l'horizon reel, jamais l'horizon demande seul.
    steps = max(1, math.ceil(req.horizon_hours / req.interval_hours))
    effective_hours = steps * req.interval_hours
    try:
        cone = compute_cone(req.closes, steps, req.confidence)
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc
    reliability = (
        f"Sur {cone.backtest_size} cas passes, l'intervalle a contenu le mouvement reel "
        f"dans {cone.reliability:.0%} des cas."
        if cone.reliability is not None
        else "Historique trop court pour mesurer la fiabilite."
    )
    horizon = f"{effective_hours:g} h"
    if not math.isclose(effective_hours, req.horizon_hours):
        horizon += (
            f" ({req.horizon_hours} h demandees, arrondies a {steps} bougie(s) "
            f"de {req.interval_hours:g} h)"
        )
    explanation = (
        f"Volatilite realisee sur {cone.sample_size} rendements : {cone.volatility:.2%} "
        f"par bougie de {req.interval_hours:g} h. Avec {req.confidence:.0%} de confiance, "
        f"le prix reste entre {cone.lower:,.2f} et {cone.upper:,.2f} dans "
        f"{horizon}. {reliability}"
    )
    return VolatilityConeResponse(
        symbol=req.symbol,
        horizon_hours=req.horizon_hours,
        effective_horizon_hours=effective_hours,
        confidence=req.confidence,
        reference_price=cone.reference_price,
        lower=cone.lower,
        upper=cone.upper,
        volatility=cone.volatility,
        reliability=cone.reliability,
        backtest_size=cone.backtest_size,
        sample_size=cone.sample_size,
        explanation=explanation,
    )
