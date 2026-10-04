"""Compte de l'utilisateur connecte et son journal d'actions."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlmodel import col, select

from app.api.deps import CurrentUser, SessionDep
from app.api.routes.auth import UserPublic
from app.models import AuditLog, User

router = APIRouter(prefix="/users", tags=["users"])


class Activity(BaseModel):
    action: str
    detail: dict[str, Any]
    created_at: datetime


@router.get("/me", response_model=UserPublic)
def me(user: CurrentUser) -> User:
    return user


@router.get("/me/activity", response_model=list[Activity])
def my_activity(
    user: CurrentUser, session: SessionDep, limit: int = Query(50, ge=1, le=500)
) -> list[AuditLog]:
    query = (
        select(AuditLog)
        .where(AuditLog.user_id == user.id)
        .order_by(col(AuditLog.created_at).desc())
        .limit(limit)
    )
    return list(session.exec(query))
