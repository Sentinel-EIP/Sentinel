"""Inscription et connexion. Les jetons sont des JWT a duree limitee."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import select

from app.api.deps import SessionDep
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.services import audit

router = APIRouter(prefix="/auth", tags=["auth"])


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=12, max_length=128)


class UserPublic(BaseModel):
    id: int
    username: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105 - type de jeton OAuth2, pas un secret
    expires_in: int


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
def register(body: Credentials, session: SessionDep) -> User:
    if not get_settings().AUTH_ALLOW_REGISTRATION:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Inscription fermee")
    if session.exec(select(User).where(User.username == body.username)).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Nom d'utilisateur deja pris")
    user = User(username=body.username, password_hash=hash_password(body.password))
    session.add(user)
    session.flush()
    audit.record(session, "register", user.id)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(body: Credentials, session: SessionDep) -> Token:
    user = session.exec(select(User).where(User.username == body.username)).first()
    valid = verify_password(body.password, user.password_hash if user else None)
    if user is None or not valid or not user.is_active:
        # Meme reponse que le compte existe ou non.
        audit.record(session, "login_failed", user.id if user else None, username=body.username)
        session.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants invalides")
    assert user.id is not None
    audit.record(session, "login", user.id)
    session.commit()
    return Token(
        access_token=create_access_token(user.id),
        expires_in=get_settings().ACCESS_TOKEN_MINUTES * 60,
    )
