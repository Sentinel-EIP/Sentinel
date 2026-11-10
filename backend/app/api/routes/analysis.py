"""Analyses IA : calcul a la demande et historique des resultats.

Les sorties ne portent aucune direction de prix ni signal achat / vente
(docs/ECARTS.md, E10) : amplitude, confiance, fiabilite mesuree, explication.
"""

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlmodel import col, select

from app.api.deps import CurrentUser, SessionDep
from app.core.logging import log
from app.models import AiResult
from app.services import audit, ml_client
from app.services.market import TIMEFRAMES, read_candles

router = APIRouter(prefix="/analysis", tags=["analysis"])

HISTORY = 500  # bougies envoyees au modele
MIN_CANDLES = 31


class VolatilityRequest(BaseModel):
    symbol: str = Field(pattern=r"^[A-Z0-9]{2,20}$", examples=["BTCEUR"])
    timeframe: Literal["1h", "4h", "1d"] = "1h"
    horizon_hours: int = Field(default=4, ge=1, le=168)
    confidence: float = Field(default=0.8, ge=0.5, le=0.99)


class AiResultOut(BaseModel):
    id: int
    kind: str
    symbol: str
    model_version: str
    confidence: float
    reliability: float | None
    explanation: str
    value: dict[str, Any]
    created_at: datetime


@router.post("/volatility", response_model=AiResultOut, status_code=status.HTTP_201_CREATED)
def run_volatility(body: VolatilityRequest, user: CurrentUser, session: SessionDep) -> AiResult:
    """Cone de volatilite sur les dernieres bougies stockees, enregistre."""
    candles = read_candles(session, body.symbol, body.timeframe, HISTORY)
    if len(candles) < MIN_CANDLES:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Historique insuffisant : {len(candles)} bougies, {MIN_CANDLES} minimum",
        )
    interval_hours = TIMEFRAMES[body.timeframe].total_seconds() / 3600
    try:
        cone = ml_client.volatility_cone(
            body.symbol,
            [c.close for c in candles],
            body.horizon_hours,
            interval_hours,
            body.confidence,
        )
    except ml_client.MLUnavailableError as exc:
        log.warning("analysis.ml_unavailable", error=str(exc))
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "Service d'analyse indisponible"
        ) from exc
    except ml_client.MLRejectedError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc

    result = AiResult(
        kind="volatility_cone",
        symbol=body.symbol,
        model_version=cone["model_version"],
        confidence=cone["confidence"],
        reliability=cone["reliability"],
        explanation=cone["explanation"],
        value={
            key: cone[key]
            for key in (
                "reference_price",
                "lower",
                "upper",
                "volatility",
                "horizon_hours",
                "backtest_size",
                "sample_size",
                "note",
            )
        }
        | {"timeframe": body.timeframe, "as_of": candles[-1].ts.isoformat()},
        requested_by=user.id,
    )
    session.add(result)
    audit.record(
        session, "analysis.volatility", user.id, symbol=body.symbol, timeframe=body.timeframe
    )
    session.commit()
    session.refresh(result)
    return result


@router.get("/results", response_model=list[AiResultOut])
def results(
    _: CurrentUser,
    session: SessionDep,
    symbol: str | None = Query(None, pattern=r"^[A-Z0-9]{2,20}$"),
    kind: str | None = Query(None, max_length=32),
    limit: int = Query(20, ge=1, le=200),
) -> list[AiResult]:
    """Derniers resultats, du plus recent au plus ancien."""
    query = select(AiResult)
    if symbol:
        query = query.where(AiResult.symbol == symbol)
    if kind:
        query = query.where(AiResult.kind == kind)
    query = query.order_by(col(AiResult.created_at).desc(), col(AiResult.id).desc()).limit(limit)
    return list(session.exec(query))
