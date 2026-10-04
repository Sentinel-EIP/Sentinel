"""Mots de passe (argon2) et jetons d'acces (JWT HS256, signes par API_SECRET_KEY)."""

from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import get_settings

MIN_SECRET_LENGTH = 32
ALGORITHM = "HS256"
_hasher = PasswordHasher()
# Hash d'un mot de passe jetable : verifie quand l'utilisateur n'existe pas,
# pour que la duree de reponse ne revele pas si un nom de compte existe.
_DUMMY_HASH = _hasher.hash("compte-inexistant")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    try:
        return _hasher.verify(password_hash or _DUMMY_HASH, password) and password_hash is not None
    except (VerificationError, InvalidHashError):
        return False


def check_secret_key() -> None:
    """Appele au demarrage de l'API : une cle trop courte l'empeche de demarrer."""
    _secret()


def _secret() -> str:
    secret = get_settings().API_SECRET_KEY
    if len(secret) < MIN_SECRET_LENGTH:
        raise RuntimeError(
            f"API_SECRET_KEY doit faire au moins {MIN_SECRET_LENGTH} caracteres "
            "(openssl rand -hex 32)"
        )
    return secret


def create_access_token(user_id: int) -> str:
    now = datetime.now(UTC)
    claims = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=get_settings().ACCESS_TOKEN_MINUTES),
    }
    return jwt.encode(claims, _secret(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """Identifiant de l'utilisateur, ou None si le jeton est invalide ou expire."""
    try:
        claims = jwt.decode(
            token, _secret(), algorithms=[ALGORITHM], options={"require": ["sub", "exp"]}
        )
        return int(claims["sub"])
    except (jwt.PyJWTError, ValueError):
        return None
