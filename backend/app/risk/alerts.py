"""Synthese de risque d'un symbole et alertes de depassement de seuil.

Niveaux (design system v1.2, CONTRIBUTING regles 3 et 4) :
  - critical : depassement d'un seuil de risque critique (seul usage du rouge) ;
  - warning  : seuil d'avertissement depasse ;
  - stale    : donnees perimees (la collecte ne suit plus), jamais declenche
               par l'absence de variation du prix.

Seuils fixes dans le code pour l'instant. Quand ils deviendront reglables :
durcir est immediat, assouplir attend 24 h (CONTRIBUTING, regle 6).
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal

from app.risk.metrics import drawdowns, realized_volatility

Level = Literal["warning", "critical", "stale"]


@dataclass(frozen=True)
class Thresholds:
    drawdown_warning: float = 0.10
    drawdown_critical: float = 0.20
    volatility_warning: float = 0.80  # annualisee
    volatility_critical: float = 1.20
    stale_after_candles: int = 2  # bougies attendues mais absentes


DEFAULT_THRESHOLDS = Thresholds()


@dataclass(frozen=True)
class Alert:
    symbol: str
    level: Level
    code: str
    message: str
    value: float
    threshold: float


@dataclass(frozen=True)
class RiskSummary:
    symbol: str
    timeframe: str
    as_of: datetime  # ouverture de la derniere bougie
    last_price: float
    volatility: float | None
    max_drawdown: float
    current_drawdown: float
    sample_size: int
    alerts: list[Alert] = field(default_factory=list)


def summarize(
    symbol: str,
    timeframe: str,
    closes: list[float],
    as_of: datetime,
    step: timedelta,
    now: datetime,
    thresholds: Thresholds = DEFAULT_THRESHOLDS,
) -> RiskSummary:
    if not closes:
        raise ValueError("serie de prix vide")
    periods_per_year = timedelta(days=365) / step
    max_dd, current_dd = drawdowns(closes)
    summary = RiskSummary(
        symbol=symbol,
        timeframe=timeframe,
        as_of=as_of,
        last_price=closes[-1],
        volatility=realized_volatility(closes, periods_per_year),
        max_drawdown=max_dd,
        current_drawdown=current_dd,
        sample_size=len(closes),
    )
    summary.alerts.extend(evaluate(summary, step, now, thresholds))
    return summary


def _graded(
    symbol: str, code: str, label: str, value: float, warning: float, critical: float
) -> Alert | None:
    if value >= critical:
        return Alert(
            symbol, "critical", code, f"{label} {value:.0%} >= {critical:.0%}", value, critical
        )
    if value >= warning:
        return Alert(
            symbol, "warning", code, f"{label} {value:.0%} >= {warning:.0%}", value, warning
        )
    return None


def evaluate(
    summary: RiskSummary, step: timedelta, now: datetime, thresholds: Thresholds
) -> list[Alert]:
    alerts: list[Alert] = []
    # Une bougie est close une periode apres son ouverture ; au-dela de
    # stale_after_candles periodes de retard, la collecte ne suit plus.
    late = (now - summary.as_of - step) / step
    if late > thresholds.stale_after_candles:
        alerts.append(
            Alert(
                summary.symbol,
                "stale",
                "data_stale",
                f"Donnees perimees : {late:.0f} bougies de retard",
                late,
                thresholds.stale_after_candles,
            )
        )
    drawdown = _graded(
        summary.symbol,
        "drawdown",
        "Drawdown courant",
        summary.current_drawdown,
        thresholds.drawdown_warning,
        thresholds.drawdown_critical,
    )
    if drawdown:
        alerts.append(drawdown)
    if summary.volatility is not None:
        volatility = _graded(
            summary.symbol,
            "volatility",
            "Volatilite annualisee",
            summary.volatility,
            thresholds.volatility_warning,
            thresholds.volatility_critical,
        )
        if volatility:
            alerts.append(volatility)
    return alerts
