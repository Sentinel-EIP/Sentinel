"""Journal d'actions des utilisateurs (table audit_logs)."""

from typing import Any

from sqlmodel import Session

from app.models import AuditLog


def record(session: Session, action: str, user_id: int | None = None, **detail: Any) -> None:
    """Ajoute une entree au journal. La transaction est validee par l'appelant."""
    session.add(AuditLog(user_id=user_id, action=action, detail=detail))
