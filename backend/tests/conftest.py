"""Fixtures communes. Les tests tournent sur SQLite en memoire : les routes
n'utilisent que du SQL portable. Ce qui est propre a TimescaleDB (hypertable,
compression) est verifie par le smoke test de la CI (migrations + alembic check)."""

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - enregistre les tables

os.environ.setdefault("API_SECRET_KEY", "test-" + "x" * 40)


@pytest.fixture
def engine() -> Generator[Engine, None, None]:
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def session(engine: Engine) -> Generator[Session, None, None]:
    with Session(engine) as s:
        yield s


@pytest.fixture
def client(engine: Engine) -> Generator[TestClient, None, None]:
    """Client de l'API branche sur la base SQLite du test."""
    from app.db.session import get_session
    from app.main import app

    def session_override() -> Generator[Session, None, None]:
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = session_override
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    """En-tetes d'un utilisateur inscrit et connecte."""
    creds = {"username": "alice", "password": "mot-de-passe-solide"}
    assert client.post("/auth/register", json=creds).status_code == 201
    token = client.post("/auth/login", json=creds).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
