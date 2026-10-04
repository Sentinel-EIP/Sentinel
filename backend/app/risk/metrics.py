"""Indicateurs de risque calcules sur une serie de prix de cloture.

Fonctions pures, sans base ni reseau : testables isolement.
Convention : drawdowns et volatilite en fractions positives (0.12 = 12 %).
"""

import math
from collections.abc import Sequence
from statistics import stdev


def log_returns(closes: Sequence[float]) -> list[float]:
    return [math.log(b / a) for a, b in zip(closes, closes[1:], strict=False)]


def realized_volatility(closes: Sequence[float], periods_per_year: float) -> float | None:
    """Volatilite annualisee : ecart-type des rendements log * sqrt(periodes par an).

    None si moins de 3 prix (ecart-type indefini).
    """
    returns = log_returns(closes)
    if len(returns) < 2:
        return None
    return stdev(returns) * math.sqrt(periods_per_year)


def drawdowns(closes: Sequence[float]) -> tuple[float, float]:
    """(drawdown maximal, drawdown courant) depuis le plus haut de la serie."""
    peak = -math.inf
    worst = current = 0.0
    for price in closes:
        peak = max(peak, price)
        current = (peak - price) / peak
        worst = max(worst, current)
    return worst, current
