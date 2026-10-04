"""Tables applicatives. Importer ce paquet enregistre toutes les tables dans
SQLModel.metadata (Alembic, tests)."""

from app.models.analysis import AiResult
from app.models.audit import AuditLog
from app.models.market import Candle
from app.models.user import User

__all__ = ["AiResult", "AuditLog", "Candle", "User"]
