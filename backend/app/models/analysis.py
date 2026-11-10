"""Resultats des modeles IA.

Format generique, sans direction de prix ni signal achat / vente : la decision
est en suspens (docs/ECARTS.md, E10). Chaque resultat porte son niveau de
confiance, sa fiabilite historique mesuree et son explication (US3.4,
CONTRIBUTING regle 5). Ajouter une direction plus tard = une colonne de plus.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Index, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class AiResult(SQLModel, table=True):
    __tablename__ = "ai_results"
    __table_args__ = (Index("ix_ai_results_symbol_kind_created", "symbol", "kind", "created_at"),)

    id: int | None = Field(default=None, primary_key=True)
    kind: str = Field(max_length=32)  # ex. volatility_cone
    symbol: str = Field(max_length=20)
    model_version: str = Field(max_length=32)
    confidence: float
    reliability: float | None = None  # part des cas passes ou le modele a vu juste
    explanation: str = Field(sa_column=Column(Text, nullable=False))
    value: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    requested_by: int | None = Field(default=None, foreign_key="users.id", ondelete="SET NULL")
    created_at: datetime = Field(
        default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
