"""Journal d'actions des utilisateurs (qui a fait quoi, quand).

Distinct des logs applicatifs (stdout, Loki) : c'est une donnee metier,
consultable par l'utilisateur et conservee en base.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Index
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_logs_user_created", "user_id", "created_at"),)

    id: int | None = Field(default=None, primary_key=True)
    # Nul pour une action sans utilisateur identifie (connexion refusee).
    user_id: int | None = Field(default=None, foreign_key="users.id", ondelete="SET NULL")
    action: str = Field(max_length=64)
    detail: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(
        default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
