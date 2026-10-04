"""Cone de volatilite realisee.

Amplitude probable du prix a un horizon donne, sans direction : l'intervalle
est symetrique en rendement logarithmique autour du dernier prix.

  sigma   = ecart-type des rendements log par bougie
  bornes  = prix * exp(+/- z * sigma * sqrt(horizon en bougies))
  z       = quantile de la loi normale pour le niveau de confiance demande

La fiabilite est mesuree sur l'historique fourni : pour chaque point passe, le
cone calcule avec les seules donnees anterieures a-t-il contenu le mouvement
reel ? (CONTRIBUTING, regle 5 : fiabilite historique mesuree.)
"""

import math
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np

MODEL_VERSION = "realized-vol-v1"
MIN_RETURNS = 30  # en dessous, l'ecart-type n'a pas de sens
MIN_BACKTEST = 20  # points passes minimum pour annoncer une fiabilite


@dataclass(frozen=True)
class Cone:
    reference_price: float
    lower: float
    upper: float
    volatility: float  # par bougie
    reliability: float | None
    backtest_size: int
    sample_size: int


def z_score(confidence: float) -> float:
    return NormalDist().inv_cdf((1 + confidence) / 2)


def volatility_cone(closes: list[float], horizon_steps: int, confidence: float) -> Cone:
    prices = np.asarray(closes, dtype=float)
    if horizon_steps < 1:
        raise ValueError("horizon_steps doit etre >= 1")
    if np.any(prices <= 0):
        raise ValueError("les prix doivent etre strictement positifs")
    returns = np.diff(np.log(prices))
    if len(returns) < MIN_RETURNS:
        raise ValueError(f"au moins {MIN_RETURNS + 1} prix sont necessaires")

    z = z_score(confidence)
    sigma = float(np.std(returns, ddof=1))
    width = z * sigma * math.sqrt(horizon_steps)
    reference = float(prices[-1])

    # Backtest : a chaque date i, sigma estime sur les rendements anterieurs,
    # puis comparaison avec le mouvement reel entre i et i + horizon.
    hits = total = 0
    for i in range(MIN_RETURNS, len(prices) - horizon_steps):
        past_sigma = float(np.std(returns[:i], ddof=1))
        move = abs(math.log(prices[i + horizon_steps] / prices[i]))
        hits += move <= z * past_sigma * math.sqrt(horizon_steps)
        total += 1
    reliability = hits / total if total >= MIN_BACKTEST else None

    return Cone(
        reference_price=reference,
        lower=reference * math.exp(-width),
        upper=reference * math.exp(width),
        volatility=sigma,
        reliability=reliability,
        backtest_size=total,
        sample_size=len(returns),
    )
