"""Service des modeles IA — couche 2 (analyse).

Isole du backend : les dependances lourdes (PyTorch, transformers) ne doivent
pas ralentir les rebuilds de l'API.

Modules prevus, conformes au dossier technique :
  - indicateurs techniques (pandas-ta)
  - volatilite : modele de cone de volatilite
  - sentiment : scoring du flux de news
  - anomalies : detection de regimes de stress

IMPORTANT : ce service ne predit JAMAIS la direction du prix. Il produit des
amplitudes, des regimes et des scores, chacun accompagne de sa fiabilite
historique mesuree.
"""

import os
import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.core.config import get_settings


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


class VolatilityConeRequest(BaseModel):
    symbol: str = Field(examples=["BTCEUR"])
    horizon_hours: int = Field(default=4, ge=1, le=168)


class VolatilityConeResponse(BaseModel):
    symbol: str
    horizon_hours: int
    confidence: float = Field(description="Niveau de confiance de l'intervalle, 0-1")
    lower: float
    upper: float
    note: str = "Amplitude probable. Aucune direction implicite."


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/models")
def list_models() -> dict[str, list[str]]:
    """Inventaire des modules charges. Vide tant que rien n'est entraine."""
    return {"loaded": [], "available": ["volatility_cone", "sentiment", "regime"]}


@app.post("/volatility/cone", response_model=VolatilityConeResponse)
def volatility_cone(req: VolatilityConeRequest) -> VolatilityConeResponse:
    """Stub. A remplacer par un GARCH ou une volatilite realisee glissante.

    Le contrat de sortie est fige des maintenant pour que le frontend puisse
    etre developpe en parallele du modele.
    """
    raise NotImplementedError("Modele de volatilite non encore implemente")
